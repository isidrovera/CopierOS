# -*- coding: utf-8 -*-

import uuid

from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class AttendanceAuditLog(models.Model):
    """
    Auditoría transversal del módulo de asistencia.

    Registra acciones realizadas sobre cualquier modelo del módulo:

    - Creación.
    - Edición.
    - Cambio de estado.
    - Presentación.
    - Aprobación.
    - Rechazo.
    - Cancelación.
    - Cierre.
    - Reapertura.
    - Archivado.
    - Restauración.
    - Marcación.
    - Corrección.
    - Procesamiento automático.
    - Inicio o finalización de sesiones operativas.
    - Cambios ejecutados mediante API, web, móvil o sistema.

    El registro guarda:

    - Usuario que ejecutó la acción.
    - Trabajador afectado.
    - Objeto afectado.
    - Valores anteriores.
    - Valores posteriores.
    - Dirección IP.
    - Dispositivo.
    - Origen.
    - Resultado.
    - Motivo.
    """

    class ActionType(models.TextChoices):
        CREATE = (
            "create",
            "Creación",
        )
        UPDATE = (
            "update",
            "Actualización",
        )
        DELETE = (
            "delete",
            "Eliminación",
        )
        ARCHIVE = (
            "archive",
            "Archivado",
        )
        RESTORE = (
            "restore",
            "Restauración",
        )
        SUBMIT = (
            "submit",
            "Presentación",
        )
        APPROVE = (
            "approve",
            "Aprobación",
        )
        PARTIAL_APPROVAL = (
            "partial_approval",
            "Aprobación parcial",
        )
        REJECT = (
            "reject",
            "Rechazo",
        )
        CANCEL = (
            "cancel",
            "Cancelación",
        )
        ACTIVATE = (
            "activate",
            "Activación",
        )
        DEACTIVATE = (
            "deactivate",
            "Desactivación",
        )
        SUSPEND = (
            "suspend",
            "Suspensión",
        )
        RESUME = (
            "resume",
            "Reanudación",
        )
        START = (
            "start",
            "Inicio",
        )
        PAUSE = (
            "pause",
            "Pausa",
        )
        COMPLETE = (
            "complete",
            "Finalización",
        )
        CLOSE = (
            "close",
            "Cierre",
        )
        REOPEN = (
            "reopen",
            "Reapertura",
        )
        CLOCK = (
            "clock",
            "Marcación",
        )
        VALIDATE = (
            "validate",
            "Validación",
        )
        OBSERVE = (
            "observe",
            "Observación",
        )
        CORRECT = (
            "correct",
            "Corrección",
        )
        RECALCULATE = (
            "recalculate",
            "Recálculo",
        )
        PROCESS = (
            "process",
            "Procesamiento",
        )
        SYNCHRONIZE = (
            "synchronize",
            "Sincronización",
        )
        ASSIGN = (
            "assign",
            "Asignación",
        )
        UNASSIGN = (
            "unassign",
            "Desasignación",
        )
        AUTHORIZE = (
            "authorize",
            "Autorización",
        )
        REVOKE = (
            "revoke",
            "Revocación",
        )
        BLOCK = (
            "block",
            "Bloqueo",
        )
        UNBLOCK = (
            "unblock",
            "Desbloqueo",
        )
        LOGIN = (
            "login",
            "Inicio de sesión",
        )
        LOGOUT = (
            "logout",
            "Cierre de sesión",
        )
        EXPORT = (
            "export",
            "Exportación",
        )
        IMPORT = (
            "import",
            "Importación",
        )
        VIEW = (
            "view",
            "Consulta",
        )
        OTHER = (
            "other",
            "Otra acción",
        )

    class SourceType(models.TextChoices):
        WEB = (
            "web",
            "Aplicación web",
        )
        MOBILE = (
            "mobile",
            "Aplicación móvil",
        )
        FIXED_DEVICE = (
            "fixed_device",
            "Dispositivo fijo",
        )
        QR = (
            "qr",
            "Código QR",
        )
        API = (
            "api",
            "API",
        )
        ADMIN = (
            "admin",
            "Administrador Django",
        )
        BACKGROUND_TASK = (
            "background_task",
            "Tarea automática",
        )
        MANAGEMENT_COMMAND = (
            "management_command",
            "Comando de administración",
        )
        IMPORT = (
            "import",
            "Importación",
        )
        SYSTEM = (
            "system",
            "Sistema",
        )
        OTHER = (
            "other",
            "Otro origen",
        )

    class ResultStatus(models.TextChoices):
        SUCCESS = (
            "success",
            "Correcto",
        )
        PARTIAL = (
            "partial",
            "Parcial",
        )
        FAILED = (
            "failed",
            "Fallido",
        )
        DENIED = (
            "denied",
            "Denegado",
        )
        VALIDATION_ERROR = (
            "validation_error",
            "Error de validación",
        )
        SYSTEM_ERROR = (
            "system_error",
            "Error del sistema",
        )

    class Severity(models.TextChoices):
        INFORMATION = (
            "information",
            "Informativa",
        )
        LOW = (
            "low",
            "Baja",
        )
        MEDIUM = (
            "medium",
            "Media",
        )
        HIGH = (
            "high",
            "Alta",
        )
        CRITICAL = (
            "critical",
            "Crítica",
        )

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name="ID",
    )

    occurred_at = models.DateTimeField(
        default=timezone.now,
        db_index=True,
        verbose_name="Fecha y hora",
    )

    action_type = models.CharField(
        max_length=40,
        choices=ActionType.choices,
        db_index=True,
        verbose_name="Tipo de acción",
    )

    source_type = models.CharField(
        max_length=30,
        choices=SourceType.choices,
        default=SourceType.WEB,
        db_index=True,
        verbose_name="Origen",
    )

    result_status = models.CharField(
        max_length=30,
        choices=ResultStatus.choices,
        default=ResultStatus.SUCCESS,
        db_index=True,
        verbose_name="Resultado",
    )

    severity = models.CharField(
        max_length=20,
        choices=Severity.choices,
        default=Severity.INFORMATION,
        db_index=True,
        verbose_name="Severidad",
    )

    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="attendance_audit_actions",
        verbose_name="Usuario ejecutor",
    )

    employee_profile = models.ForeignKey(
        "attendance.EmployeeProfile",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="audit_logs",
        verbose_name="Trabajador afectado",
    )

    content_type = models.ForeignKey(
        ContentType,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="attendance_audit_logs",
        verbose_name="Tipo de objeto",
    )

    object_id = models.CharField(
        max_length=100,
        blank=True,
        db_index=True,
        verbose_name="ID del objeto",
    )

    content_object = GenericForeignKey(
        "content_type",
        "object_id",
    )

    object_model = models.CharField(
        max_length=150,
        blank=True,
        db_index=True,
        verbose_name="Modelo del objeto",
    )

    object_representation = models.CharField(
        max_length=500,
        blank=True,
        verbose_name="Representación del objeto",
    )

    action_title = models.CharField(
        max_length=255,
        verbose_name="Título de la acción",
    )

    action_description = models.TextField(
        blank=True,
        verbose_name="Descripción",
    )

    reason = models.TextField(
        blank=True,
        verbose_name="Motivo",
    )

    previous_values = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Valores anteriores",
    )

    new_values = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Valores posteriores",
    )

    changed_fields = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Campos modificados",
    )

    request_method = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="Método HTTP",
    )

    request_path = models.CharField(
        max_length=500,
        blank=True,
        verbose_name="Ruta solicitada",
    )

    request_id = models.CharField(
        max_length=100,
        blank=True,
        db_index=True,
        verbose_name="ID de solicitud",
    )

    correlation_id = models.CharField(
        max_length=100,
        blank=True,
        db_index=True,
        verbose_name="ID de correlación",
        help_text=(
            "Permite agrupar varias acciones originadas "
            "por una misma operación."
        ),
    )

    session_key = models.CharField(
        max_length=100,
        blank=True,
        db_index=True,
        verbose_name="Clave de sesión",
    )

    device = models.ForeignKey(
        "attendance.AttendanceDevice",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="audit_logs",
        verbose_name="Dispositivo",
    )

    work_location = models.ForeignKey(
        "attendance.WorkLocation",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="audit_logs",
        verbose_name="Ubicación de trabajo",
    )

    public_ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name="Dirección IP pública",
    )

    local_ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name="Dirección IP local",
    )

    user_agent = models.TextField(
        blank=True,
        verbose_name="Agente del navegador",
    )

    device_identifier = models.CharField(
        max_length=255,
        blank=True,
        db_index=True,
        verbose_name="Identificador del dispositivo",
    )

    app_version = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Versión de aplicación",
    )

    latitude = models.DecimalField(
        max_digits=10,
        decimal_places=7,
        null=True,
        blank=True,
        verbose_name="Latitud",
    )

    longitude = models.DecimalField(
        max_digits=10,
        decimal_places=7,
        null=True,
        blank=True,
        verbose_name="Longitud",
    )

    error_code = models.CharField(
        max_length=100,
        blank=True,
        db_index=True,
        verbose_name="Código de error",
    )

    error_message = models.TextField(
        blank=True,
        verbose_name="Mensaje de error",
    )

    exception_type = models.CharField(
        max_length=255,
        blank=True,
        db_index=True,
        verbose_name="Tipo de excepción",
    )

    stack_trace = models.TextField(
        blank=True,
        verbose_name="Traza del error",
    )

    metadata = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Metadatos",
    )

    contains_sensitive_data = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="Contiene datos sensibles",
    )

    requires_review = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="Requiere revisión",
    )

    reviewed_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Revisado el",
    )

    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="attendance_audit_logs_reviewed",
        verbose_name="Revisado por",
    )

    review_notes = models.TextField(
        blank=True,
        verbose_name="Observaciones de revisión",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        verbose_name="Creado el",
    )

    class Meta:
        verbose_name = "Registro de auditoría de asistencia"
        verbose_name_plural = "Registros de auditoría de asistencia"

        ordering = (
            "-occurred_at",
            "-created_at",
        )

        indexes = (
            models.Index(
                fields=(
                    "actor",
                    "occurred_at",
                    "action_type",
                ),
                name="att_audit_actor_time_idx",
            ),
            models.Index(
                fields=(
                    "employee_profile",
                    "occurred_at",
                ),
                name="att_audit_emp_time_idx",
            ),
            models.Index(
                fields=(
                    "content_type",
                    "object_id",
                    "occurred_at",
                ),
                name="att_audit_object_time_idx",
            ),
            models.Index(
                fields=(
                    "action_type",
                    "result_status",
                    "occurred_at",
                ),
                name="att_audit_action_result_idx",
            ),
            models.Index(
                fields=(
                    "source_type",
                    "occurred_at",
                ),
                name="att_audit_source_time_idx",
            ),
            models.Index(
                fields=(
                    "severity",
                    "requires_review",
                    "occurred_at",
                ),
                name="att_audit_sev_review_idx",
            ),
            models.Index(
                fields=(
                    "request_id",
                    "correlation_id",
                ),
                name="att_audit_request_corr_idx",
            ),
            models.Index(
                fields=(
                    "device",
                    "occurred_at",
                ),
                name="att_audit_device_time_idx",
            ),
            models.Index(
                fields=(
                    "work_location",
                    "occurred_at",
                ),
                name="att_audit_location_time_idx",
            ),
            models.Index(
                fields=(
                    "error_code",
                    "exception_type",
                    "occurred_at",
                ),
                name="att_audit_error_type_idx",
            ),
            models.Index(
                fields=(
                    "contains_sensitive_data",
                    "requires_review",
                ),
                name="att_audit_sensitive_idx",
            ),
        )

    def __str__(self):
        actor_name = (
            self.actor.full_name
            if self.actor_id
            else "Sistema"
        )

        return (
            f"{actor_name} - "
            f"{self.get_action_type_display()} - "
            f"{self.occurred_at}"
        )

    @property
    def object_reference(self):
        if self.object_model and self.object_id:
            return (
                f"{self.object_model}:"
                f"{self.object_id}"
            )

        if self.object_id:
            return self.object_id

        return ""

    @property
    def is_successful(self):
        return self.result_status in (
            self.ResultStatus.SUCCESS,
            self.ResultStatus.PARTIAL,
        )

    @property
    def has_error(self):
        return self.result_status in (
            self.ResultStatus.FAILED,
            self.ResultStatus.DENIED,
            self.ResultStatus.VALIDATION_ERROR,
            self.ResultStatus.SYSTEM_ERROR,
        )

    @property
    def has_changes(self):
        return bool(
            self.changed_fields
            or self.previous_values
            or self.new_values
        )

    def clean(self):
        super().clean()

        errors = {}

        if bool(self.content_type_id) != bool(self.object_id):
            errors["object_id"] = (
                "Debes registrar tanto el tipo como el ID "
                "del objeto auditado."
            )

        if (
            self.device_id
            and self.device.archived_at
        ):
            errors["device"] = (
                "El dispositivo relacionado está archivado."
            )

        if (
            self.work_location_id
            and self.work_location.archived_at
        ):
            errors["work_location"] = (
                "La ubicación relacionada está archivada."
            )

        if (
            self.employee_profile_id
            and self.employee_profile.archived_at
        ):
            errors["employee_profile"] = (
                "El perfil laboral relacionado está archivado."
            )

        if (
            self.latitude is None
            and self.longitude is not None
        ):
            errors["latitude"] = (
                "Debes registrar la latitud junto "
                "con la longitud."
            )

        if (
            self.longitude is None
            and self.latitude is not None
        ):
            errors["longitude"] = (
                "Debes registrar la longitud junto "
                "con la latitud."
            )

        if (
            self.latitude is not None
            and not (
                -90 <= self.latitude <= 90
            )
        ):
            errors["latitude"] = (
                "La latitud debe estar entre -90 y 90."
            )

        if (
            self.longitude is not None
            and not (
                -180 <= self.longitude <= 180
            )
        ):
            errors["longitude"] = (
                "La longitud debe estar entre -180 y 180."
            )

        if (
            self.result_status
            in (
                self.ResultStatus.FAILED,
                self.ResultStatus.VALIDATION_ERROR,
                self.ResultStatus.SYSTEM_ERROR,
            )
            and not self.error_message.strip()
        ):
            errors["error_message"] = (
                "Una acción fallida debe registrar "
                "el mensaje de error."
            )

        if (
            self.result_status
            == self.ResultStatus.DENIED
            and not self.reason.strip()
            and not self.error_message.strip()
        ):
            errors["reason"] = (
                "Una acción denegada debe indicar el motivo."
            )

        if (
            self.requires_review
            and self.reviewed_at
            and not self.reviewed_by_id
        ):
            errors["reviewed_by"] = (
                "Debes indicar quién revisó el registro."
            )

        if (
            self.reviewed_by_id
            and not self.reviewed_at
        ):
            errors["reviewed_at"] = (
                "Debes indicar cuándo se revisó el registro."
            )

        if (
            not isinstance(
                self.previous_values,
                dict,
            )
        ):
            errors["previous_values"] = (
                "Los valores anteriores deben ser un objeto JSON."
            )

        if not isinstance(
            self.new_values,
            dict,
        ):
            errors["new_values"] = (
                "Los valores posteriores deben ser un objeto JSON."
            )

        if not isinstance(
            self.changed_fields,
            list,
        ):
            errors["changed_fields"] = (
                "Los campos modificados deben ser una lista."
            )

        if not isinstance(
            self.metadata,
            dict,
        ):
            errors["metadata"] = (
                "Los metadatos deben ser un objeto JSON."
            )

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        if self.content_type_id:
            self.object_model = (
                f"{self.content_type.app_label}."
                f"{self.content_type.model}"
            )

        if (
            self.content_object is not None
            and not self.object_representation
        ):
            self.object_representation = str(
                self.content_object
            )[:500]

        self.request_method = str(
            self.request_method or ""
        ).strip().upper()

        self.full_clean()

        super().save(
            *args,
            **kwargs,
        )

    def mark_reviewed(
        self,
        user,
        notes="",
    ):
        self.requires_review = False
        self.reviewed_at = timezone.now()
        self.reviewed_by = user
        self.review_notes = str(
            notes or ""
        ).strip()

        self.save(
            update_fields=[
                "requires_review",
                "reviewed_at",
                "reviewed_by",
                "review_notes",
            ]
        )

    @classmethod
    def register(
        cls,
        *,
        action_type,
        action_title,
        actor=None,
        employee_profile=None,
        content_object=None,
        source_type=SourceType.SYSTEM,
        result_status=ResultStatus.SUCCESS,
        severity=Severity.INFORMATION,
        action_description="",
        reason="",
        previous_values=None,
        new_values=None,
        changed_fields=None,
        device=None,
        work_location=None,
        public_ip_address=None,
        local_ip_address=None,
        user_agent="",
        request_method="",
        request_path="",
        request_id="",
        correlation_id="",
        session_key="",
        device_identifier="",
        app_version="",
        latitude=None,
        longitude=None,
        error_code="",
        error_message="",
        exception_type="",
        stack_trace="",
        metadata=None,
        contains_sensitive_data=False,
        requires_review=False,
    ):
        """
        Crea un registro de auditoría desde servicios, vistas,
        señales o tareas automáticas.
        """

        content_type = None
        object_id = ""
        object_representation = ""

        if content_object is not None:
            content_type = (
                ContentType.objects
                .get_for_model(
                    content_object,
                    for_concrete_model=False,
                )
            )

            object_id = str(
                content_object.pk
            )

            object_representation = str(
                content_object
            )[:500]

        log = cls(
            action_type=action_type,
            action_title=action_title,
            actor=actor,
            employee_profile=employee_profile,
            content_type=content_type,
            object_id=object_id,
            object_representation=object_representation,
            source_type=source_type,
            result_status=result_status,
            severity=severity,
            action_description=str(
                action_description or ""
            ).strip(),
            reason=str(
                reason or ""
            ).strip(),
            previous_values=previous_values or {},
            new_values=new_values or {},
            changed_fields=changed_fields or [],
            device=device,
            work_location=work_location,
            public_ip_address=public_ip_address,
            local_ip_address=local_ip_address,
            user_agent=str(
                user_agent or ""
            ),
            request_method=str(
                request_method or ""
            ).upper(),
            request_path=str(
                request_path or ""
            ),
            request_id=str(
                request_id or ""
            ),
            correlation_id=str(
                correlation_id or ""
            ),
            session_key=str(
                session_key or ""
            ),
            device_identifier=str(
                device_identifier or ""
            ),
            app_version=str(
                app_version or ""
            ),
            latitude=latitude,
            longitude=longitude,
            error_code=str(
                error_code or ""
            ),
            error_message=str(
                error_message or ""
            ),
            exception_type=str(
                exception_type or ""
            ),
            stack_trace=str(
                stack_trace or ""
            ),
            metadata=metadata or {},
            contains_sensitive_data=(
                contains_sensitive_data
            ),
            requires_review=requires_review,
        )

        log.save()

        return log

    @classmethod
    def register_success(
        cls,
        *,
        action_type,
        action_title,
        **kwargs,
    ):
        return cls.register(
            action_type=action_type,
            action_title=action_title,
            result_status=cls.ResultStatus.SUCCESS,
            **kwargs,
        )

    @classmethod
    def register_failure(
        cls,
        *,
        action_type,
        action_title,
        error_message,
        **kwargs,
    ):
        return cls.register(
            action_type=action_type,
            action_title=action_title,
            result_status=cls.ResultStatus.FAILED,
            severity=cls.Severity.HIGH,
            error_message=error_message,
            requires_review=True,
            **kwargs,
        )

    @classmethod
    def register_validation_error(
        cls,
        *,
        action_type,
        action_title,
        error_message,
        **kwargs,
    ):
        return cls.register(
            action_type=action_type,
            action_title=action_title,
            result_status=(
                cls.ResultStatus.VALIDATION_ERROR
            ),
            severity=cls.Severity.MEDIUM,
            error_message=error_message,
            **kwargs,
        )

    @classmethod
    def register_denied(
        cls,
        *,
        action_type,
        action_title,
        reason,
        **kwargs,
    ):
        return cls.register(
            action_type=action_type,
            action_title=action_title,
            result_status=cls.ResultStatus.DENIED,
            severity=cls.Severity.MEDIUM,
            reason=reason,
            **kwargs,
        )