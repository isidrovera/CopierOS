# -*- coding: utf-8 -*-
from django.db import transaction
from django.db.models import Count, Q
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.services.models import (
    ServicePartRequest,
    ServicePartRequestComment,
    ServicePartRequestStatusHistory,
)
from apps.services.serializers import (
    ArchiveServicePartRequestSerializer,
    ServicePartRequestListSerializer,
    ServicePartRequestSerializer,
    ServicePartRequestStatusChangeSerializer,
)


class ServicePartRequestViewSet(viewsets.ModelViewSet):
    queryset = ServicePartRequest.objects.none()
    serializer_class = ServicePartRequestSerializer

    def get_queryset(self):
        queryset = (
            ServicePartRequest.objects
            .select_related(
                "service_order",
                "service_order__equipment",
                "installation_service_order",
                "requested_by",
                "submitted_by",
                "management_reviewed_by",
                "stock_reviewed_by",
                "logistics_prepared_by",
                "current_responsible_user",
            )
            .annotate(
                item_count=Count(
                    "items",
                    filter=Q(
                        items__archived_at__isnull=True,
                    ),
                    distinct=True,
                )
            )
        )

        include_archived = (
            self.request.query_params
            .get("include_archived", "")
            .strip()
            .lower()
            in {"1", "true", "yes"}
        )

        if not include_archived:
            queryset = queryset.filter(
                archived_at__isnull=True,
            )

        service_order = self.request.query_params.get(
            "service_order"
        )

        if service_order:
            queryset = queryset.filter(
                service_order_id=service_order,
            )

        status_value = self.request.query_params.get(
            "status"
        )

        if status_value:
            queryset = queryset.filter(
                status=status_value,
            )

        responsible_area = self.request.query_params.get(
            "responsible_area"
        )

        if responsible_area:
            queryset = queryset.filter(
                current_responsible_area=responsible_area,
            )

        responsible_user = self.request.query_params.get(
            "responsible_user"
        )

        if responsible_user:
            queryset = queryset.filter(
                current_responsible_user_id=responsible_user,
            )

        search = str(
            self.request.query_params.get("search", "")
        ).strip()

        if search:
            queryset = queryset.filter(
                Q(code__icontains=search)
                | Q(service_order__code__icontains=search)
                | Q(
                    service_order__equipment__serial_number__icontains=search
                )
                | Q(
                    service_order__equipment__internal_code__icontains=search
                )
            )

        return queryset.order_by(
            "-created_at",
        )

    def get_serializer_class(self):
        if self.action == "list":
            return ServicePartRequestListSerializer

        if self.action == "change_status":
            return ServicePartRequestStatusChangeSerializer

        if self.action == "archive":
            return ArchiveServicePartRequestSerializer

        return ServicePartRequestSerializer

    @staticmethod
    def _status_fields(status_value, user):
        now = timezone.now()
        values = {}

        mapping = {
            "submitted": (
                "submitted_at",
                "submitted_by",
            ),
            "under_management_review": (
                "management_reviewed_at",
                "management_reviewed_by",
            ),
            "information_required": (
                "information_requested_at",
                None,
            ),
            "information_answered": (
                "information_answered_at",
                None,
            ),
            "under_stock_review": (
                "stock_reviewed_at",
                "stock_reviewed_by",
            ),
            "ready_for_installation": (
                "logistics_ready_at",
                "logistics_prepared_by",
            ),
            "delivered": (
                "delivered_at",
                None,
            ),
            "closed": (
                "closed_at",
                None,
            ),
        }

        date_field, user_field = mapping.get(
            status_value,
            (None, None),
        )

        if date_field:
            values[date_field] = now

        if user_field:
            values[user_field] = user

        return values

    @action(
        detail=True,
        methods=["post"],
        url_path="change-status",
    )
    @transaction.atomic
    def change_status(self, request, pk=None):
        part_request = self.get_object()
        serializer = self.get_serializer(
            data=request.data,
        )
        serializer.is_valid(raise_exception=True)

        previous_status = part_request.status
        new_status = serializer.validated_data["status"]
        user = (
            request.user
            if request.user.is_authenticated
            else None
        )

        if previous_status == new_status:
            return Response(
                {
                    "detail": (
                        "El pedido ya tiene el estado indicado."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        part_request.status = new_status

        if "current_responsible_area" in serializer.validated_data:
            part_request.current_responsible_area = (
                serializer.validated_data[
                    "current_responsible_area"
                ]
            )

        if "current_responsible_user" in serializer.validated_data:
            part_request.current_responsible_user = (
                serializer.validated_data[
                    "current_responsible_user"
                ]
            )

        for field, value in self._status_fields(
            new_status,
            user,
        ).items():
            setattr(part_request, field, value)

        if user and hasattr(part_request, "updated_by"):
            part_request.updated_by = user

        part_request.save()

        comment = str(
            serializer.validated_data.get(
                "comment",
                "",
            )
            or ""
        ).strip()

        ServicePartRequestStatusHistory.objects.create(
            request=part_request,
            previous_status=previous_status,
            new_status=new_status,
            action="status_change",
            responsible_area=(
                part_request.current_responsible_area
            ),
            changed_by=user,
            source="api",
            comment=comment,
            created_by=user,
            updated_by=user,
        )

        if comment:
            ServicePartRequestComment.objects.create(
                request=part_request,
                comment_type="general",
                message=comment,
                author=user,
                created_by=user,
                updated_by=user,
            )

        return Response(
            ServicePartRequestSerializer(
                part_request,
                context=self.get_serializer_context(),
            ).data
        )

    @action(
        detail=True,
        methods=["post"],
        url_path="archive",
    )
    @transaction.atomic
    def archive(self, request, pk=None):
        part_request = self.get_object()
        serializer = self.get_serializer(
            data=request.data,
        )
        serializer.is_valid(raise_exception=True)

        if part_request.archived_at:
            return Response(
                {
                    "detail": "El pedido ya está archivado."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = (
            request.user
            if request.user.is_authenticated
            else None
        )

        part_request.archived_at = timezone.now()
        part_request.archived_by = user
        part_request.archived_reason = (
            serializer.validated_data["reason"]
        )

        if user and hasattr(part_request, "updated_by"):
            part_request.updated_by = user

        part_request.save()

        return Response(
            ServicePartRequestSerializer(
                part_request,
                context=self.get_serializer_context(),
            ).data
        )

    @action(
        detail=True,
        methods=["post"],
        url_path="restore",
    )
    @transaction.atomic
    def restore(self, request, pk=None):
        part_request = (
            ServicePartRequest.objects
            .select_related(
                "service_order",
                "installation_service_order",
            )
            .get(pk=pk)
        )

        if not part_request.archived_at:
            return Response(
                {
                    "detail": "El pedido no está archivado."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = (
            request.user
            if request.user.is_authenticated
            else None
        )

        part_request.archived_at = None
        part_request.archived_by = None
        part_request.archived_reason = ""

        if user and hasattr(part_request, "updated_by"):
            part_request.updated_by = user

        part_request.save()

        return Response(
            ServicePartRequestSerializer(
                part_request,
                context=self.get_serializer_context(),
            ).data
        )
