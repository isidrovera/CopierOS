# -*- coding: utf-8 -*-
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from ..models.repair_part_delivery import RepairPartDelivery
from ..serializers.repair_part_delivery import (
    RepairPartDeliveryCreateSerializer,
    RepairPartDeliveryDeliverSerializer,
    RepairPartDeliveryDetailSerializer,
    RepairPartDeliveryListSerializer,
    RepairPartDeliveryPrepareSerializer,
    RepairPartDeliveryReceiveSerializer,
)
from ..services.repair_part_delivery import (
    deliver_repair_part,
    prepare_repair_part_delivery,
    receive_repair_part_delivery,
)
from .common import get_authenticated_actor, get_boolean_query_param


class RepairPartDeliveryViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    http_method_names = ("get", "post", "head", "options")
    filter_backends = (
        filters.SearchFilter,
        filters.OrderingFilter,
    )
    search_fields = (
        "item__request__code",
        "item__component__name",
        "item__custom_name",
        "delivery_document",
        "notes",
    )
    ordering_fields = (
        "status",
        "prepared_at",
        "delivered_at",
        "confirmed_at",
        "created_at",
    )
    ordering = ("-created_at",)

    def get_queryset(self):
        queryset = (
            RepairPartDelivery.objects
            .select_related(
                "item",
                "item__request",
                "item__component",
                "prepared_by",
                "delivered_by",
                "delivered_to",
                "confirmed_by",
                "created_by",
                "updated_by",
                "archived_by",
            )
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
            "item": "item_id",
            "request": "item__request_id",
            "status": "status",
            "delivered_to": "delivered_to_id",
        }

        for query_param, field_name in filters_map.items():
            value = self.request.query_params.get(query_param)
            if value:
                queryset = queryset.filter(**{field_name: value})

        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return RepairPartDeliveryListSerializer
        if self.action == "create":
            return RepairPartDeliveryCreateSerializer
        return RepairPartDeliveryDetailSerializer

    @action(detail=True, methods=("post",), url_path="prepare")
    def prepare(self, request, pk=None):
        instance = self.get_object()
        serializer = RepairPartDeliveryPrepareSerializer(
            data=request.data,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)

        instance = prepare_repair_part_delivery(
            delivery=instance,
            actor=get_authenticated_actor(request),
            notes=serializer.validated_data.get("notes", ""),
        )

        return Response(
            RepairPartDeliveryDetailSerializer(
                instance,
                context={"request": request},
            ).data,
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=("post",), url_path="deliver")
    def deliver(self, request, pk=None):
        instance = self.get_object()
        serializer = RepairPartDeliveryDeliverSerializer(
            data=request.data,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)

        instance = deliver_repair_part(
            delivery=instance,
            actor=get_authenticated_actor(request),
            delivered_to=serializer.validated_data["delivered_to"],
            quantity=serializer.validated_data["quantity"],
            delivery_document=serializer.validated_data.get(
                "delivery_document",
                "",
            ),
            notes=serializer.validated_data.get("notes", ""),
        )

        return Response(
            RepairPartDeliveryDetailSerializer(
                instance,
                context={"request": request},
            ).data,
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=("post",), url_path="receive")
    def receive(self, request, pk=None):
        instance = self.get_object()
        serializer = RepairPartDeliveryReceiveSerializer(
            data=request.data,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)

        instance = receive_repair_part_delivery(
            delivery=instance,
            actor=get_authenticated_actor(request),
            received_quantity=serializer.validated_data[
                "received_quantity"
            ],
            notes=serializer.validated_data.get("notes", ""),
        )

        return Response(
            RepairPartDeliveryDetailSerializer(
                instance,
                context={"request": request},
            ).data,
            status=status.HTTP_200_OK,
        )
