# -*- coding: utf-8 -*-
from django.core.exceptions import (
    ValidationError as DjangoValidationError,
)
from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import (
    filters,
    status,
    viewsets,
)
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from ..models import (
    RepairChecklist,
    RepairChecklistItem,
)
from ..serializers import (
    ArchiveRepairChecklistItemSerializer,
    ArchiveRepairChecklistSerializer,
    CompleteRepairChecklistSerializer,
    RepairChecklistCreateUpdateSerializer,
    RepairChecklistDetailSerializer,
    RepairChecklistItemCreateUpdateSerializer,
    RepairChecklistItemDetailSerializer,
    RepairChecklistItemListSerializer,
    RepairChecklistListSerializer,
    ReviewRepairChecklistItemSerializer,
    StartRepairChecklistSerializer,
)
from ..services import (
    complete_checklist,
    create_compatible_component_items,
    create_main_checklist,
    reopen_checklist,
    review_checklist_item,
    start_checklist,
)
from .common import (
    django_validation_error_response,
    get_authenticated_actor,
    get_boolean_query_param,
)


class RepairChecklistViewSet(
    viewsets.ModelViewSet
):
    permission_classes = (
        IsAuthenticated,
    )

    filter_backends = (
        filters.SearchFilter,
        filters.OrderingFilter,
    )

    search_fields = (
        "repair__code",
        "repair__equipment__serial_number",
        "name",
        "description",
        "observations",
        "started_by__first_name",
        "started_by__last_name",
        "started_by__email",
        "completed_by__first_name",
        "completed_by__last_name",
        "completed_by__email",
    )

    ordering_fields = (
        "name",
        "status",
        "is_main_checklist",
        "started_at",
        "completed_at",
        "created_at",
        "updated_at",
    )

    ordering = (
        "-is_main_checklist",
        "-created_at",
    )

    def get_queryset(self):
        queryset = (
            RepairChecklist.objects
            .select_related(
                "repair",
                "repair__equipment",
                "started_by",
                "completed_by",
                "created_by",
                "updated_by",
                "archived_by",
            )
            .prefetch_related(
                "items",
                "items__component",
                "items__component__component_type",
                "items__component__parent_component",
                "items__component__subcomponents",
                "items__selected_subcomponents",
                "items__selected_subcomponents__component_type",
                "items__selected_subcomponents__parent_component",
                "items__checked_by",
                "items__photos",
            )
        )

        include_archived = get_boolean_query_param(
            self.request,
            "include_archived",
            False,
        )

        if not include_archived:
            queryset = queryset.filter(
                archived_at__isnull=True,
            )

        repair_id = self.request.query_params.get(
            "repair"
        )

        if repair_id:
            queryset = queryset.filter(
                repair_id=repair_id,
            )

        equipment_id = self.request.query_params.get(
            "equipment"
        )

        if equipment_id:
            queryset = queryset.filter(
                repair__equipment_id=equipment_id,
            )

        checklist_status = (
            self.request.query_params.get(
                "status"
            )
        )

        if checklist_status:
            statuses = [
                value.strip()
                for value in checklist_status.split(",")
                if value.strip()
            ]

            if statuses:
                queryset = queryset.filter(
                    status__in=statuses,
                )

        is_main_checklist = (
            get_boolean_query_param(
                self.request,
                "is_main_checklist",
                None,
            )
        )

        if is_main_checklist is not None:
            queryset = queryset.filter(
                is_main_checklist=(
                    is_main_checklist
                ),
            )

        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return RepairChecklistListSerializer

        if self.action in (
            "create",
            "update",
            "partial_update",
        ):
            return RepairChecklistCreateUpdateSerializer

        return RepairChecklistDetailSerializer

    def create(self, request, *args, **kwargs):
        serializer = (
            RepairChecklistCreateUpdateSerializer(
                data=request.data,
                context={
                    "request": request,
                },
            )
        )

        serializer.is_valid(
            raise_exception=True
        )

        actor = get_authenticated_actor(
            request
        )

        validated_data = serializer.validated_data

        try:
            if validated_data.get(
                "is_main_checklist",
                True,
            ):
                checklist = create_main_checklist(
                    repair=validated_data["repair"],
                    actor=actor,
                    name=validated_data.get(
                        "name",
                        "Lista principal de revisión",
                    ),
                    description=validated_data.get(
                        "description",
                        "",
                    ),
                    include_general_items=True,
                    include_compatible_components=True,
                )

                observations = validated_data.get(
                    "observations",
                    "",
                )

                if observations:
                    checklist.observations = (
                        observations
                    )
                    checklist.updated_by = actor
                    checklist.save(
                        update_fields=[
                            "observations",
                            "updated_by",
                            "updated_at",
                        ]
                    )
            else:
                checklist = serializer.save(
                    created_by=actor,
                    updated_by=actor,
                )
        except DjangoValidationError as exception:
            return django_validation_error_response(
                exception
            )

        return Response(
            RepairChecklistDetailSerializer(
                checklist,
                context={
                    "request": request,
                },
            ).data,
            status=status.HTTP_201_CREATED,
        )

    def perform_destroy(self, instance):
        actor = get_authenticated_actor(
            self.request
        )

        if instance.status == (
            RepairChecklist.Status.IN_PROGRESS
        ):
            raise DjangoValidationError(
                "No puedes archivar una lista en proceso."
            )

        instance.archive(
            user=actor,
            reason="Archivado desde la API.",
        )

    @action(
        detail=True,
        methods=("post",),
        url_path="load-compatible-components",
    )
    def load_compatible_components(
        self,
        request,
        pk=None,
    ):
        checklist = self.get_object()

        actor = get_authenticated_actor(
            request
        )

        try:
            created_items = (
                create_compatible_component_items(
                    checklist=checklist,
                    actor=actor,
                )
            )
        except DjangoValidationError as exception:
            return django_validation_error_response(
                exception
            )

        checklist = self.get_queryset().get(
            pk=checklist.pk
        )

        return Response(
            {
                "created_count": len(
                    created_items
                ),
                "detail": (
                    "Se cargaron "
                    f"{len(created_items)} "
                    "unidades compatibles."
                    if created_items
                    else (
                        "No se encontraron unidades "
                        "compatibles nuevas para cargar."
                    )
                ),
                "checklist": (
                    RepairChecklistDetailSerializer(
                        checklist,
                        context={
                            "request": request,
                        },
                    ).data
                ),
            },
            status=status.HTTP_200_OK,
        )

    @action(
        detail=True,
        methods=("post",),
        url_path="start",
    )
    def start(self, request, pk=None):
        checklist = self.get_object()

        serializer = StartRepairChecklistSerializer(
            data=request.data,
            context={
                "request": request,
                "checklist": checklist,
            },
        )

        serializer.is_valid(
            raise_exception=True
        )

        actor = get_authenticated_actor(
            request
        )

        try:
            checklist = start_checklist(
                checklist=checklist,
                actor=actor,
                observations=(
                    serializer.validated_data.get(
                        "observations",
                        "",
                    )
                ),
            )
        except DjangoValidationError as exception:
            return django_validation_error_response(
                exception
            )

        return Response(
            RepairChecklistDetailSerializer(
                checklist,
                context={
                    "request": request,
                },
            ).data,
            status=status.HTTP_200_OK,
        )

    @action(
        detail=True,
        methods=("post",),
        url_path="complete",
    )
    def complete(self, request, pk=None):
        checklist = self.get_object()

        serializer = (
            CompleteRepairChecklistSerializer(
                data=request.data,
                context={
                    "request": request,
                    "checklist": checklist,
                },
            )
        )

        serializer.is_valid(
            raise_exception=True
        )

        actor = get_authenticated_actor(
            request
        )

        try:
            checklist = complete_checklist(
                checklist=checklist,
                actor=actor,
                observations=(
                    serializer.validated_data.get(
                        "observations",
                        "",
                    )
                ),
            )
        except DjangoValidationError as exception:
            return django_validation_error_response(
                exception
            )

        return Response(
            RepairChecklistDetailSerializer(
                checklist,
                context={
                    "request": request,
                },
            ).data,
            status=status.HTTP_200_OK,
        )

    @action(
        detail=True,
        methods=("post",),
        url_path="reopen",
    )
    def reopen(self, request, pk=None):
        checklist = self.get_object()

        reason = str(
            request.data.get(
                "reason",
                "",
            )
            or ""
        ).strip()

        actor = get_authenticated_actor(
            request
        )

        try:
            checklist = reopen_checklist(
                checklist=checklist,
                actor=actor,
                reason=reason,
            )
        except DjangoValidationError as exception:
            return django_validation_error_response(
                exception
            )

        return Response(
            RepairChecklistDetailSerializer(
                checklist,
                context={
                    "request": request,
                },
            ).data,
            status=status.HTTP_200_OK,
        )

    @action(
        detail=True,
        methods=("post",),
        url_path="archive",
    )
    def archive(self, request, pk=None):
        checklist = get_object_or_404(
            RepairChecklist.objects.all(),
            pk=pk,
        )

        serializer = (
            ArchiveRepairChecklistSerializer(
                data=request.data,
            )
        )

        serializer.is_valid(
            raise_exception=True
        )

        if checklist.archived_at is not None:
            return Response(
                {
                    "detail": (
                        "La lista ya se encuentra archivada."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if checklist.status == (
            RepairChecklist.Status.IN_PROGRESS
        ):
            return Response(
                {
                    "detail": (
                        "No puedes archivar una lista en proceso."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        actor = get_authenticated_actor(
            request
        )

        checklist.archive(
            user=actor,
            reason=serializer.validated_data.get(
                "reason",
                "",
            ),
        )

        return Response(
            RepairChecklistDetailSerializer(
                checklist,
                context={
                    "request": request,
                },
            ).data,
            status=status.HTTP_200_OK,
        )

    @action(
        detail=True,
        methods=("post",),
        url_path="restore",
    )
    def restore(self, request, pk=None):
        checklist = get_object_or_404(
            RepairChecklist.objects.all(),
            pk=pk,
        )

        if checklist.archived_at is None:
            return Response(
                {
                    "detail": (
                        "La lista no se encuentra archivada."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not checklist.repair.is_active:
            return Response(
                {
                    "detail": (
                        "La reparación ya no está activa."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if (
            checklist.is_main_checklist
            and RepairChecklist.objects.filter(
                repair=checklist.repair,
                is_main_checklist=True,
                archived_at__isnull=True,
            )
            .exclude(
                pk=checklist.pk,
            )
            .exists()
        ):
            return Response(
                {
                    "is_main_checklist": (
                        "La reparación ya tiene otra "
                        "lista principal."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        actor = get_authenticated_actor(
            request
        )

        checklist.restore(
            user=actor,
        )

        return Response(
            RepairChecklistDetailSerializer(
                checklist,
                context={
                    "request": request,
                },
            ).data,
            status=status.HTTP_200_OK,
        )


class RepairChecklistItemViewSet(
    viewsets.ModelViewSet
):
    permission_classes = (
        IsAuthenticated,
    )

    filter_backends = (
        filters.SearchFilter,
        filters.OrderingFilter,
    )

    search_fields = (
        "checklist__repair__code",
        "checklist__repair__equipment__serial_number",
        "code",
        "name",
        "description",
        "instructions",
        "observation",
        "component__name",
        "component__code",
    )

    ordering_fields = (
        "code",
        "name",
        "category",
        "status",
        "is_required",
        "requires_photo",
        "display_order",
        "checked_at",
        "created_at",
        "updated_at",
    )

    ordering = (
        "display_order",
        "created_at",
    )

    def get_queryset(self):
        queryset = (
            RepairChecklistItem.objects
            .select_related(
                "checklist",
                "checklist__repair",
                "checklist__repair__equipment",
                "component",
                "component__component_type",
                "component__parent_component",
                "checked_by",
                "created_by",
                "updated_by",
                "archived_by",
            )
            .prefetch_related(
                "component__subcomponents",
                "selected_subcomponents",
                "selected_subcomponents__component_type",
                "selected_subcomponents__parent_component",
                "photos",
            )
        )

        include_archived = get_boolean_query_param(
            self.request,
            "include_archived",
            False,
        )

        if not include_archived:
            queryset = queryset.filter(
                archived_at__isnull=True,
            )

        checklist_id = self.request.query_params.get(
            "checklist"
        )

        if checklist_id:
            queryset = queryset.filter(
                checklist_id=checklist_id,
            )

        repair_id = self.request.query_params.get(
            "repair"
        )

        if repair_id:
            queryset = queryset.filter(
                checklist__repair_id=repair_id,
            )

        component_id = self.request.query_params.get(
            "component"
        )

        if component_id:
            queryset = queryset.filter(
                component_id=component_id,
            )

        category = self.request.query_params.get(
            "category"
        )

        if category:
            categories = [
                value.strip()
                for value in category.split(",")
                if value.strip()
            ]

            if categories:
                queryset = queryset.filter(
                    category__in=categories,
                )

        item_status = self.request.query_params.get(
            "status"
        )

        if item_status:
            statuses = [
                value.strip()
                for value in item_status.split(",")
                if value.strip()
            ]

            if statuses:
                queryset = queryset.filter(
                    status__in=statuses,
                )

        is_required = get_boolean_query_param(
            self.request,
            "is_required",
            None,
        )

        if is_required is not None:
            queryset = queryset.filter(
                is_required=is_required,
            )

        requires_photo = get_boolean_query_param(
            self.request,
            "requires_photo",
            None,
        )

        if requires_photo is not None:
            queryset = queryset.filter(
                requires_photo=requires_photo,
            )

        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return RepairChecklistItemListSerializer

        if self.action in (
            "create",
            "update",
            "partial_update",
        ):
            return RepairChecklistItemCreateUpdateSerializer

        return RepairChecklistItemDetailSerializer

    def perform_destroy(self, instance):
        actor = get_authenticated_actor(
            self.request
        )

        if (
            instance.checklist.status
            == RepairChecklist.Status.COMPLETED
        ):
            raise DjangoValidationError(
                "No puedes archivar un punto de una lista completada."
            )

        instance.archive(
            user=actor,
            reason="Archivado desde la API.",
        )

    @action(
        detail=True,
        methods=("post",),
        url_path="review",
    )
    def review(self, request, pk=None):
        item = self.get_object()

        serializer = (
            ReviewRepairChecklistItemSerializer(
                data=request.data,
                context={
                    "request": request,
                    "item": item,
                },
            )
        )

        serializer.is_valid(
            raise_exception=True
        )

        actor = get_authenticated_actor(
            request
        )

        selected_subcomponents = (
            serializer.validated_data.get(
                "selected_subcomponents",
                [],
            )
        )

        try:
            with transaction.atomic():
                item = review_checklist_item(
                    item=item,
                    status=(
                        serializer.validated_data[
                            "status"
                        ]
                    ),
                    actor=actor,
                    observation=(
                        serializer.validated_data.get(
                            "observation",
                            "",
                        )
                    ),
                    consumable_present=(
                        serializer.validated_data.get(
                            "consumable_present",
                            None,
                        )
                    ),
                    consumable_level_percent=(
                        serializer.validated_data.get(
                            "consumable_level_percent",
                            None,
                        )
                    ),
                )

                if (
                    item.status
                    == RepairChecklistItem.Status.FAILED
                ):
                    item.selected_subcomponents.set(
                        selected_subcomponents
                    )
                else:
                    item.selected_subcomponents.clear()

        except DjangoValidationError as exception:
            return django_validation_error_response(
                exception
            )

        item = self.get_queryset().get(
            pk=item.pk
        )

        return Response(
            RepairChecklistItemDetailSerializer(
                item,
                context={
                    "request": request,
                },
            ).data,
            status=status.HTTP_200_OK,
        )

    @action(
        detail=True,
        methods=("post",),
        url_path="archive",
    )
    def archive(self, request, pk=None):
        item = get_object_or_404(
            RepairChecklistItem.objects.all(),
            pk=pk,
        )

        serializer = (
            ArchiveRepairChecklistItemSerializer(
                data=request.data,
            )
        )

        serializer.is_valid(
            raise_exception=True
        )

        if item.archived_at is not None:
            return Response(
                {
                    "detail": (
                        "El punto ya se encuentra archivado."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if (
            item.checklist.status
            == RepairChecklist.Status.COMPLETED
        ):
            return Response(
                {
                    "detail": (
                        "No puedes archivar un punto "
                        "de una lista completada."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        actor = get_authenticated_actor(
            request
        )

        item.archive(
            user=actor,
            reason=serializer.validated_data.get(
                "reason",
                "",
            ),
        )

        return Response(
            RepairChecklistItemDetailSerializer(
                item,
                context={
                    "request": request,
                },
            ).data,
            status=status.HTTP_200_OK,
        )

    @action(
        detail=True,
        methods=("post",),
        url_path="restore",
    )
    def restore(self, request, pk=None):
        item = get_object_or_404(
            RepairChecklistItem.objects.all(),
            pk=pk,
        )

        if item.archived_at is None:
            return Response(
                {
                    "detail": (
                        "El punto no se encuentra archivado."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if item.checklist.archived_at is not None:
            return Response(
                {
                    "detail": (
                        "La lista de revisión está archivada."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if (
            item.checklist.status
            == RepairChecklist.Status.COMPLETED
        ):
            return Response(
                {
                    "detail": (
                        "No puedes restaurar puntos "
                        "en una lista completada."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        duplicate_exists = (
            RepairChecklistItem.objects.filter(
                checklist=item.checklist,
                code__iexact=item.code,
                archived_at__isnull=True,
            )
            .exclude(
                pk=item.pk,
            )
            .exists()
        )

        if duplicate_exists:
            return Response(
                {
                    "code": (
                        "Ya existe otro punto activo "
                        "con este código."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        actor = get_authenticated_actor(
            request
        )

        item.restore(
            user=actor,
        )

        return Response(
            RepairChecklistItemDetailSerializer(
                item,
                context={
                    "request": request,
                },
            ).data,
            status=status.HTTP_200_OK,
        )