# -*- coding: utf-8 -*-
from django.core.exceptions import ValidationError

from apps.services.models import ServiceEvidence


def validate_service_order_closure(service_order):
    errors = {}

    if not str(service_order.diagnosis or "").strip():
        errors["diagnosis"] = "Debe registrar el diagnóstico."

    if not str(service_order.work_performed or "").strip():
        errors["work_performed"] = "Debe registrar el trabajo realizado."

    checklist = getattr(service_order, "checklist", None)

    if checklist is None or checklist.status != checklist.Status.COMPLETED:
        errors["checklist"] = "El checklist debe estar completado."

    before_count = service_order.evidences.filter(
        archived_at__isnull=True,
        stage=ServiceEvidence.Stage.BEFORE,
    ).count()

    after_count = service_order.evidences.filter(
        archived_at__isnull=True,
        stage=ServiceEvidence.Stage.AFTER,
    ).count()

    if before_count < 3:
        errors["before_evidence"] = "Se requieren al menos 3 fotos antes."

    if after_count < 3:
        errors["after_evidence"] = "Se requieren al menos 3 fotos después."

    if errors:
        raise ValidationError(errors)

    return True
