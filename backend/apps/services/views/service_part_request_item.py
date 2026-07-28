# -*- coding: utf-8 -*-
from django.db import transaction
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.services.models import ServicePartRequestItem
from apps.services.serializers import (
    ServicePartRequestItemDecisionSerializer,
    ServicePartRequestItemListSerializer,
    ServicePartRequestItemSerializer,
    ServicePartRequestItemSupplySerializer,
)


class ServicePartRequestItemViewSet(viewsets.ModelViewSet):
    queryset = ServicePartRequestItem.objects.none()
    serializer_class = ServicePartRequestItemSerializer

    def get_queryset(self):
        queryset = (
            ServicePartRequestItem.objects
            .select_related(
                "request",
                "request__service_order",
                "checklist_item",
                "source_component",
            )
            .prefetch_related(
                "attachments",
                "comments",
                "management_decisions",
                "installation_items",
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

        request_id = self.request.query_params.get(
            "request"
        )

        if request_id:
            queryset = queryset.filter(
                request_id=request_id,
            )

        checklist_item = self.request.query_params.get(
            "checklist_item"
        )

        if checklist_item:
            queryset = queryset.filter(
                checklist_item_id=checklist_item,
            )

        item_type = self.request.query_params.get(
            "item_type"
        )

        if item_type:
            queryset = queryset.filter(
                item_type=item_type,
            )

        management_decision = self.request.query_params.get(
            "management_decision"
        )

        if management_decision:
            queryset = queryset.filter(
                management_decision=management_decision,
            )

        supply_method = self.request.query_params.get(
            "supply_method"
        )

        if supply_method:
            queryset = queryset.filter(
                supply_method=supply_method,
            )

        return queryset.order_by(
            "created_at",
        )

    def get_serializer_class(self):
        if self.action == "list":
            return ServicePartRequestItemListSerializer

        if self.action == "management_decision":
            return ServicePartRequestItemDecisionSerializer

        if self.action == "confirm_supply":
            return ServicePartRequestItemSupplySerializer

        return ServicePartRequestItemSerializer

    @action(
        detail=True,
        methods=["post"],
        url_path="management-decision",
    )
    @transaction.atomic
    def management_decision(self, request, pk=None):
        item = self.get_object()
        serializer = self.get_serializer(
            data=request.data,
        )
        serializer.is_valid(raise_exception=True)

        item.management_decision = (
            serializer.validated_data[
                "management_decision"
            ]
        )

        if "approved_quantity" in serializer.validated_data:
            item.approved_quantity = (
                serializer.validated_data[
                    "approved_quantity"
                ]
            )

        if "management_notes" in serializer.validated_data:
            item.management_notes = (
                serializer.validated_data[
                    "management_notes"
                ]
            )

        if (
            request.user.is_authenticated
            and hasattr(item, "updated_by")
        ):
            item.updated_by = request.user

        item.save()

        return Response(
            ServicePartRequestItemSerializer(
                item,
                context=self.get_serializer_context(),
            ).data
        )

    @action(
        detail=True,
        methods=["post"],
        url_path="confirm-supply",
    )
    @transaction.atomic
    def confirm_supply(self, request, pk=None):
        item = self.get_object()
        serializer = self.get_serializer(
            data=request.data,
        )
        serializer.is_valid(raise_exception=True)

        item.supply_method = serializer.validated_data[
            "supply_method"
        ]

        if (
            "stock_confirmed_quantity"
            in serializer.validated_data
        ):
            item.stock_confirmed_quantity = (
                serializer.validated_data[
                    "stock_confirmed_quantity"
                ]
            )

        if "stock_notes" in serializer.validated_data:
            item.stock_notes = serializer.validated_data[
                "stock_notes"
            ]

        if (
            request.user.is_authenticated
            and hasattr(item, "updated_by")
        ):
            item.updated_by = request.user

        item.save()

        return Response(
            ServicePartRequestItemSerializer(
                item,
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
        item = self.get_object()

        if item.archived_at:
            return Response(
                {
                    "detail": "El artículo ya está archivado."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        reason = str(
            request.data.get("reason", "")
        ).strip()

        if not reason:
            return Response(
                {
                    "reason": [
                        "Debe indicar el motivo del archivado."
                    ]
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = (
            request.user
            if request.user.is_authenticated
            else None
        )

        item.archived_at = timezone.now()
        item.archived_by = user
        item.archived_reason = reason

        if user and hasattr(item, "updated_by"):
            item.updated_by = user

        item.save()

        return Response(
            ServicePartRequestItemSerializer(
                item,
                context=self.get_serializer_context(),
            ).data
        )
