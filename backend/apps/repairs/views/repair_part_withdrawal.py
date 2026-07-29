# -*- coding: utf-8 -*-
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from ..models.repair_part_withdrawal import RepairPartWithdrawal
from ..serializers.repair_part_withdrawal import (
    RepairPartWithdrawalAuthorizeSerializer,
    RepairPartWithdrawalConfirmSerializer,
    RepairPartWithdrawalCreateSerializer,
    RepairPartWithdrawalDetailSerializer,
    RepairPartWithdrawalListSerializer,
    RepairPartWithdrawalReceiveSerializer,
)
from ..services.repair_part_withdrawal import (
    authorize_repair_part_withdrawal,
    confirm_repair_part_withdrawal,
    receive_repair_part_withdrawal,
)
from .common import get_authenticated_actor, get_boolean_query_param


class RepairPartWithdrawalViewSet(viewsets.ModelViewSet):
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
        "authorization_notes",
        "withdrawal_notes",
    )
    ordering_fields = (
        "status",
        "authorized_at",
        "valid_until",
        "withdrawn_at",
        "received_at",
        "created_at",
    )
    ordering = ("-created_at",)

    def get_queryset(self):
        queryset = (
            RepairPartWithdrawal.objects
            .select_related(
                "item",
                "item__request",
                "item__component",
                "source",
                "authorized_person",
                "authorized_by",
                "withdrawn_by",
                "received_by",
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
            "authorized_person": "authorized_person_id",
        }

        for query_param, field_name in filters_map.items():
            value = self.request.query_params.get(query_param)
            if value:
                queryset = queryset.filter(**{field_name: value})

        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return RepairPartWithdrawalListSerializer
        if self.action == "create":
            return RepairPartWithdrawalCreateSerializer
        return RepairPartWithdrawalDetailSerializer

    @action(detail=True, methods=("post",), url_path="authorize")
    def authorize(self, request, pk=None):
        instance = self.get_object()
        serializer = RepairPartWithdrawalAuthorizeSerializer(
            data=request.data,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)

        instance = authorize_repair_part_withdrawal(
            withdrawal=instance,
            actor=get_authenticated_actor(request),
            authorized_person=serializer.validated_data[
                "authorized_person"
            ],
            valid_until=serializer.validated_data.get("valid_until"),
            notes=serializer.validated_data.get("notes", ""),
        )

        return Response(
            RepairPartWithdrawalDetailSerializer(
                instance,
                context={"request": request},
            ).data,
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=("post",), url_path="confirm-withdrawal")
    def confirm_withdrawal(self, request, pk=None):
        instance = self.get_object()
        serializer = RepairPartWithdrawalConfirmSerializer(
            data=request.data,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)

        instance = confirm_repair_part_withdrawal(
            withdrawal=instance,
            actor=get_authenticated_actor(request),
            notes=serializer.validated_data.get("notes", ""),
        )

        return Response(
            RepairPartWithdrawalDetailSerializer(
                instance,
                context={"request": request},
            ).data,
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=("post",), url_path="receive")
    def receive(self, request, pk=None):
        instance = self.get_object()
        serializer = RepairPartWithdrawalReceiveSerializer(
            data=request.data,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)

        instance = receive_repair_part_withdrawal(
            withdrawal=instance,
            actor=get_authenticated_actor(request),
            notes=serializer.validated_data.get("notes", ""),
        )

        return Response(
            RepairPartWithdrawalDetailSerializer(
                instance,
                context={"request": request},
            ).data,
            status=status.HTTP_200_OK,
        )
