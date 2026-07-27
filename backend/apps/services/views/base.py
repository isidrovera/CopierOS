# -*- coding: utf-8 -*-
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response


class ArchiveRestoreMixin:
    @action(detail=True, methods=["post"])
    def archive(self, request, pk=None):
        instance = self.get_object()
        reason = str(request.data.get("reason", "") or "").strip()
        instance.archive(user=request.user, reason=reason)
        return Response(self.get_serializer(instance).data)

    @action(detail=True, methods=["post"])
    def restore(self, request, pk=None):
        instance = self.get_object()
        instance.restore(user=request.user)
        return Response(self.get_serializer(instance).data)
