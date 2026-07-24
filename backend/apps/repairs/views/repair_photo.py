# -*- coding: utf-8 -*-
from django.core.exceptions import (
    ValidationError as DjangoValidationError,
)
from django.shortcuts import get_object_or_404
from rest_framework import (
    filters,
    parsers,
    status,
    viewsets,
)
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from ..models import RepairPhoto
from ..serializers import (
    ArchiveRepairPhotoSerializer,
    RemoveRepairPhotoVerificationSerializer,
    RepairPhotoCreateUpdateSerializer,
    RepairPhotoDetailSerializer,
    RepairPhotoListSerializer,
    VerifyRepairPhotoSerializer,
)
from ..services import (
    archive_repair_photo,
    create_repair_photo,
    remove_photo_verification,
    restore_repair_photo,
    verify_repair_photo,
)
from .common import (
    django_validation_error_response,
    get_authenticated_actor,
    get_boolean_query_param,
)


class RepairPhotoViewSet(
    viewsets.ModelViewSet
):
    permission_classes = (
        IsAuthenticated,
    )

    parser_classes = (
        parsers.MultiPartParser,
        parsers.FormParser,
        parsers.JSONParser,
    )

    filter_backends = (
        filters.SearchFilter,
        filters.OrderingFilter,
    )

    search_fields = (
        "repair__code",
        "repair__equipment__serial_number",
        "original_filename",
        "title",
        "description",
        "verification_notes",
        "checklist_item__code",
        "checklist_item__name",
        "taken_by__first_name",
        "taken_by__last_name",
        "taken_by__email",
        "uploaded_by__first_name",
        "uploaded_by__last_name",
        "uploaded_by__email",
    )

    ordering_fields = (
        "category",
        "stage",
        "taken_at",
        "uploaded_at",
        "is_required",
        "counts_for_minimum",
        "is_verified",
        "verified_at",
        "display_order",
        "created_at",
        "updated_at",
    )

    ordering = (
        "display_order",
        "created_at",
    )

    def get_queryset(self):
        queryset = (
            RepairPhoto.objects
            .select_related(
                "repair",
                "repair__equipment",
                "checklist_item",
                "checklist_item__checklist",
                "taken_by",
                "uploaded_by",
                "verified_by",
                "created_by",
                "updated_by",
                "archived_by",
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

        checklist_item_id = (
            self.request.query_params.get(
                "checklist_item"
            )
        )

        if checklist_item_id:
            queryset = queryset.filter(
                checklist_item_id=checklist_item_id,
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

        stage = self.request.query_params.get(
            "stage"
        )

        if stage:
            stages = [
                value.strip()
                for value in stage.split(",")
                if value.strip()
            ]

            if stages:
                queryset = queryset.filter(
                    stage__in=stages,
                )

        taken_by_id = self.request.query_params.get(
            "taken_by"
        )

        if taken_by_id:
            queryset = queryset.filter(
                taken_by_id=taken_by_id,
            )

        uploaded_by_id = (
            self.request.query_params.get(
                "uploaded_by"
            )
        )

        if uploaded_by_id:
            queryset = queryset.filter(
                uploaded_by_id=uploaded_by_id,
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

        counts_for_minimum = (
            get_boolean_query_param(
                self.request,
                "counts_for_minimum",
                None,
            )
        )

        if counts_for_minimum is not None:
            queryset = queryset.filter(
                counts_for_minimum=(
                    counts_for_minimum
                ),
            )

        is_verified = get_boolean_query_param(
            self.request,
            "is_verified",
            None,
        )

        if is_verified is not None:
            queryset = queryset.filter(
                is_verified=is_verified,
            )

        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return RepairPhotoListSerializer

        if self.action in (
            "create",
            "update",
            "partial_update",
        ):
            return RepairPhotoCreateUpdateSerializer

        return RepairPhotoDetailSerializer

    def create(self, request, *args, **kwargs):
        serializer = (
            RepairPhotoCreateUpdateSerializer(
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

        validated_data = dict(
            serializer.validated_data
        )

        repair = validated_data.pop(
            "repair"
        )

        image = validated_data.pop(
            "image"
        )

        try:
            photo = create_repair_photo(
                repair=repair,
                image=image,
                actor=actor,
                **validated_data,
            )
        except DjangoValidationError as exception:
            return django_validation_error_response(
                exception
            )

        return Response(
            RepairPhotoDetailSerializer(
                photo,
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

        try:
            archive_repair_photo(
                photo=instance,
                actor=actor,
                reason="Archivado desde la API.",
            )
        except DjangoValidationError as exception:
            from rest_framework.exceptions import (
                ValidationError as DRFValidationError,
            )

            if hasattr(
                exception,
                "message_dict",
            ):
                raise DRFValidationError(
                    exception.message_dict
                ) from exception

            raise DRFValidationError(
                exception.messages
            ) from exception

    @action(
        detail=True,
        methods=("post",),
        url_path="verify",
    )
    def verify(self, request, pk=None):
        photo = self.get_object()

        serializer = VerifyRepairPhotoSerializer(
            data=request.data,
            context={
                "request": request,
                "photo": photo,
            },
        )

        serializer.is_valid(
            raise_exception=True
        )

        actor = get_authenticated_actor(
            request
        )

        try:
            photo = verify_repair_photo(
                photo=photo,
                actor=actor,
                verification_notes=(
                    serializer.validated_data.get(
                        "verification_notes",
                        "",
                    )
                ),
            )
        except DjangoValidationError as exception:
            return django_validation_error_response(
                exception
            )

        return Response(
            RepairPhotoDetailSerializer(
                photo,
                context={
                    "request": request,
                },
            ).data,
            status=status.HTTP_200_OK,
        )

    @action(
        detail=True,
        methods=("post",),
        url_path="remove-verification",
    )
    def remove_verification(
        self,
        request,
        pk=None,
    ):
        photo = self.get_object()

        serializer = (
            RemoveRepairPhotoVerificationSerializer(
                data=request.data,
                context={
                    "request": request,
                    "photo": photo,
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
            photo = remove_photo_verification(
                photo=photo,
                actor=actor,
                reason=serializer.validated_data.get(
                    "reason",
                    "",
                ),
            )
        except DjangoValidationError as exception:
            return django_validation_error_response(
                exception
            )

        return Response(
            RepairPhotoDetailSerializer(
                photo,
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
        photo = get_object_or_404(
            RepairPhoto.objects.all(),
            pk=pk,
        )

        serializer = ArchiveRepairPhotoSerializer(
            data=request.data,
        )

        serializer.is_valid(
            raise_exception=True
        )

        actor = get_authenticated_actor(
            request
        )

        try:
            photo = archive_repair_photo(
                photo=photo,
                actor=actor,
                reason=serializer.validated_data.get(
                    "reason",
                    "",
                ),
            )
        except DjangoValidationError as exception:
            return django_validation_error_response(
                exception
            )

        return Response(
            RepairPhotoDetailSerializer(
                photo,
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
        photo = get_object_or_404(
            RepairPhoto.objects.all(),
            pk=pk,
        )

        actor = get_authenticated_actor(
            request
        )

        try:
            photo = restore_repair_photo(
                photo=photo,
                actor=actor,
            )
        except DjangoValidationError as exception:
            return django_validation_error_response(
                exception
            )

        return Response(
            RepairPhotoDetailSerializer(
                photo,
                context={
                    "request": request,
                },
            ).data,
            status=status.HTTP_200_OK,
        )