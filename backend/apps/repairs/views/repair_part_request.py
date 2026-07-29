# -*- coding: utf-8 -*-
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from ..models.repair_part_request import RepairPartRequest
from ..serializers.repair_part_request import (
    ArchiveRepairPartRequestSerializer,
    RepairPartRequestCancelSerializer,
    RepairPartRequestCloseSerializer,
    RepairPartRequestCreateUpdateSerializer,
    RepairPartRequestDetailSerializer,
    RepairPartRequestListSerializer,
    RepairPartRequestSubmitSerializer,
)
from ..services.repair_part_request import (
    archive_repair_part_request,
    cancel_repair_part_request,
    close_repair_part_request,
    restore_repair_part_request,
    submit_repair_part_request,
)
from .common import (
    django_validation_error_response,
    get_authenticated_actor,
    get_boolean_query_param,
)


class RepairPartRequestViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    filter_backends = (
        filters.SearchFilter,
        filters.OrderingFilter,
    )
    search_fields = (
        "code",
        "repair__code",
        "repair__equipment__serial_number",
        "title",
        "description",
        "technical_justification",
        "requested_by__first_name",
        "requested_by__last_name",
        "requested_by__email",
    )
    ordering_fields = (
        "code",
        "status",
        "priority",
        "submitted_at",
        "approved_at",
        "closed_at",
        "created_at",
        "updated_at",
    )
    ordering = ("-created_at",)

    def get_queryset(self):
        queryset = (
            RepairPartRequest.objects
            .select_related(
                "repair",
                "repair__equipment",
                "requested_by",
                "submitted_by",
                "approved_by",
                "rejected_by",
                "closed_by",
                "current_responsible_user",
                "created_by",
                "updated_by",
                "archived_by",
            )
            .prefetch_related("items")
        )

        if not get_boolean_query_param(
            self.request,
            "include_archived",
            False,
        ):
            queryset = queryset.filter(
                archived_at__isnull=True,
            )

        filters_map = {
            "repair": "repair_id",
            "status": "status",
            "priority": "priority",
            "requested_by": "requested_by_id",
            "current_responsible_area": "current_responsible_area",
            "current_responsible_user": "current_responsible_user_id",
        }

        for query_param, field_name in filters_map.items():
            value = self.request.query_params.get(query_param)
            if value:
                queryset = queryset.filter(**{field_name: value})

        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return RepairPartRequestListSerializer

        if self.action in {
            "create",
            "update",
            "partial_update",
        }:
            return RepairPartRequestCreateUpdateSerializer

        return RepairPartRequestDetailSerializer

    def perform_destroy(self, instance):
        archive_repair_part_request(
            request_instance=instance,
            actor=get_authenticated_actor(self.request),
            reason="Archivado desde la API.",
        )

    @action(detail=True, methods=("post",), url_path="submit")
    def submit(self, request, pk=None):
        instance = self.get_object()
        serializer = RepairPartRequestSubmitSerializer(
            data=request.data,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)

        try:
            instance = submit_repair_part_request(
                request_instance=instance,
                actor=get_authenticated_actor(request),
                observations=serializer.validated_data.get(
                    "observations",
                    "",
                ),
            )
        except Exception as exception:
            from django.core.exceptions import ValidationError
            if isinstance(exception, ValidationError):
                return django_validation_error_response(exception)
            raise

        return Response(
            RepairPartRequestDetailSerializer(
                instance,
                context={"request": request},
            ).data,
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=("post",), url_path="cancel")
    def cancel(self, request, pk=None):
        instance = self.get_object()
        serializer = RepairPartRequestCancelSerializer(
            data=request.data,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)

        try:
            instance = cancel_repair_part_request(
                request_instance=instance,
                actor=get_authenticated_actor(request),
                reason=serializer.validated_data["reason"],
            )
        except Exception as exception:
            from django.core.exceptions import ValidationError
            if isinstance(exception, ValidationError):
                return django_validation_error_response(exception)
            raise

        return Response(
            RepairPartRequestDetailSerializer(
                instance,
                context={"request": request},
            ).data,
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=("post",), url_path="close")
    def close(self, request, pk=None):
        instance = self.get_object()
        serializer = RepairPartRequestCloseSerializer(
            data=request.data,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)

        try:
            instance = close_repair_part_request(
                request_instance=instance,
                actor=get_authenticated_actor(request),
                observations=serializer.validated_data.get(
                    "observations",
                    "",
                ),
            )
        except Exception as exception:
            from django.core.exceptions import ValidationError
            if isinstance(exception, ValidationError):
                return django_validation_error_response(exception)
            raise

        return Response(
            RepairPartRequestDetailSerializer(
                instance,
                context={"request": request},
            ).data,
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=("post",), url_path="archive")
    def archive(self, request, pk=None):
        instance = self.get_object()
        serializer = ArchiveRepairPartRequestSerializer(
            data=request.data,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)

        try:
            instance = archive_repair_part_request(
                request_instance=instance,
                actor=get_authenticated_actor(request),
                reason=serializer.validated_data["reason"],
            )
        except Exception as exception:
            from django.core.exceptions import ValidationError
            if isinstance(exception, ValidationError):
                return django_validation_error_response(exception)
            raise

        return Response(
            RepairPartRequestDetailSerializer(
                instance,
                context={"request": request},
            ).data,
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=("post",), url_path="restore")
    def restore(self, request, pk=None):
        instance = self.get_queryset().model.objects.get(pk=pk)

        try:
            instance = restore_repair_part_request(
                request_instance=instance,
                actor=get_authenticated_actor(request),
            )
        except Exception as exception:
            from django.core.exceptions import ValidationError
            if isinstance(exception, ValidationError):
                return django_validation_error_response(exception)
            raise

        return Response(
            RepairPartRequestDetailSerializer(
                instance,
                context={"request": request},
            ).data,
            status=status.HTTP_200_OK,
        )
