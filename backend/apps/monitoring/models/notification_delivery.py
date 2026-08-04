# -*- coding: utf-8 -*-
import hashlib
import json
import uuid

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from .base import MonitoringBaseModel


class MonitoringNotificationDelivery(MonitoringBaseModel):
    """
    Intento individual de entrega de una notificación.

    Cada registro representa un canal y destinatario concretos.

    Ejemplos:

    - Correo enviado a una asesora.
    - Notificación interna para un jefe de taller.
    - Notificación push a un usuario.
    - Solicitud enviada a un webhook externo.

    Conserva el historial completo de intentos, respuestas,
    errores, reintentos y confirmaciones de entrega.
    """

    class Channel(models.TextChoices):
        IN_APP = (
            "in_app",
            "Copier OS",
        )
        EMAIL = (
            "email",
            "Correo electrónico",
        )
        PUSH = (
            "push",
            "Notificación push",
        )
        WEBHOOK = (
            "webhook",
            "Webhook",
        )

    class Status(models.TextChoices):
        PENDING = (
            "pending",
            "Pendiente",
        )
        QUEUED = (
            "queued",
            "En cola",
        )
        SENDING = (
            "sending",
            "Enviando",
        )
        SENT = (
            "sent",
            "Enviada",
        )
        DELIVERED = (
            "delivered",
            "Entregada",
        )
        OPENED = (
            "opened",
            "Abierta",
        )
        ACKNOWLEDGED = (
            "acknowledged",
            "Reconocida",
        )
        FAILED = (
            "failed",
            "Fallida",
        )
        RETRY_SCHEDULED = (
            "retry_scheduled",
            "Reintento programado",
        )
        CANCELLED = (
            "cancelled",
            "Cancelada",
        )
        EXPIRED = (
            "expired",
            "Expirada",
        )
        REJECTED = (
            "rejected",
            "Rechazada",
        )
        BOUNCED = (
            "bounced",
            "Rebotada",
        )
        SUPPRESSED = (
            "suppressed",
            "Suprimida",
        )

    class RecipientType(models.TextChoices):
        USER = (
            "user",
            "Usuario",
        )
        CONTACT = (
            "contact",
            "Contacto",
        )
        EMAIL = (
            "email",
            "Correo",
        )
        ROLE = (
            "role",
            "Rol",
        )
        WEBHOOK = (
            "webhook",
            "Webhook",
        )
        DEVICE = (
            "device",
            "Dispositivo",
        )
        OTHER = (
            "other",
            "Otro",
        )

    class ProviderStatus(models.TextChoices):
        UNKNOWN = (
            "unknown",
            "Desconocido",
        )
        ACCEPTED = (
            "accepted",
            "Aceptado",
        )
        QUEUED = (
            "queued",
            "En cola",
        )
        SENT = (
            "sent",
            "Enviado",
        )
        DELIVERED = (
            "delivered",
            "Entregado",
        )
        OPENED = (
            "opened",
            "Abierto",
        )
        REJECTED = (
            "rejected",
            "Rechazado",
        )
        BOUNCED = (
            "bounced",
            "Rebotado",
        )
        FAILED = (
            "failed",
            "Fallido",
        )

    delivery_uuid = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False,
        db_index=True,
        verbose_name="UUID de entrega",
    )

    notification = models.ForeignKey(
        "monitoring.MonitoringNotificationInstance",
        on_delete=models.PROTECT,
        related_name="deliveries",
        verbose_name="Notificación",
    )

    rule = models.ForeignKey(
        "monitoring.MonitoringNotificationRule",
        on_delete=models.PROTECT,
        related_name="notification_deliveries",
        verbose_name="Regla",
    )

    customer = models.ForeignKey(
        "partners.Partner",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="monitoring_notification_deliveries",
        verbose_name="Cliente",
    )

    branch = models.ForeignKey(
        "partners.PartnerBranch",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="monitoring_notification_deliveries",
        verbose_name="Sede",
    )

    agent = models.ForeignKey(
        "monitoring.MonitoringAgent",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="notification_deliveries",
        verbose_name="Agente",
    )

    device = models.ForeignKey(
        "monitoring.MonitoredDevice",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="notification_deliveries",
        verbose_name="Dispositivo",
    )

    recipient_user = models.ForeignKey(
        "users.User",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="monitoring_notification_deliveries",
        verbose_name="Usuario destinatario",
    )

    recipient_contact = models.ForeignKey(
        "partners.PartnerContact",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="monitoring_notification_deliveries",
        verbose_name="Contacto destinatario",
    )

    duplicate_of = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="duplicate_deliveries",
        verbose_name="Duplicada de",
    )

    delivery_key = models.CharField(
        max_length=64,
        db_index=True,
        editable=False,
        verbose_name="Clave de entrega",
    )

    channel = models.CharField(
        max_length=20,
        choices=Channel.choices,
        db_index=True,
        verbose_name="Canal",
    )

    status = models.CharField(
        max_length=30,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True,
        verbose_name="Estado",
    )

    provider_status = models.CharField(
        max_length=20,
        choices=ProviderStatus.choices,
        default=ProviderStatus.UNKNOWN,
        db_index=True,
        verbose_name="Estado del proveedor",
    )

    recipient_type = models.CharField(
        max_length=20,
        choices=RecipientType.choices,
        default=RecipientType.OTHER,
        db_index=True,
        verbose_name="Tipo de destinatario",
    )

    recipient_identifier = models.CharField(
        max_length=500,
        db_index=True,
        verbose_name="Identificador del destinatario",
        help_text=(
            "Correo, UUID de usuario, código de rol, URL de webhook "
            "u otro identificador estable."
        ),
    )

    recipient_name = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Nombre del destinatario",
    )

    recipient_email = models.EmailField(
        max_length=320,
        blank=True,
        db_index=True,
        verbose_name="Correo del destinatario",
    )

    recipient_role_code = models.CharField(
        max_length=150,
        blank=True,
        db_index=True,
        verbose_name="Código de rol",
    )

    recipient_device_token_reference = models.CharField(
        max_length=255,
        blank=True,
        db_index=True,
        verbose_name="Referencia del token push",
        help_text=(
            "Debe guardar una referencia o huella, nunca "
            "el token push completo."
        ),
    )

    destination_url = models.URLField(
        max_length=1000,
        blank=True,
        verbose_name="URL de destino",
    )

    subject = models.CharField(
        max_length=500,
        blank=True,
        verbose_name="Asunto",
    )

    title = models.CharField(
        max_length=500,
        blank=True,
        verbose_name="Título",
    )

    message = models.TextField(
        verbose_name="Mensaje",
    )

    html_body = models.TextField(
        blank=True,
        verbose_name="Contenido HTML",
    )

    action_url = models.CharField(
        max_length=1000,
        blank=True,
        verbose_name="Enlace de acción",
    )

    payload = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Payload enviado",
        help_text=(
            "No debe incluir credenciales, tokens completos "
            "ni secretos sin cifrar."
        ),
    )

    request_headers = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Cabeceras enviadas",
        help_text=(
            "Las cabeceras sensibles deben encontrarse depuradas."
        ),
    )

    request_body_hash = models.CharField(
        max_length=64,
        blank=True,
        editable=False,
        db_index=True,
        verbose_name="Huella del contenido enviado",
    )

    provider_name = models.CharField(
        max_length=150,
        blank=True,
        db_index=True,
        verbose_name="Proveedor",
    )

    provider_message_id = models.CharField(
        max_length=255,
        blank=True,
        db_index=True,
        verbose_name="ID del proveedor",
    )

    provider_request_id = models.CharField(
        max_length=255,
        blank=True,
        db_index=True,
        verbose_name="ID de solicitud del proveedor",
    )

    provider_response_code = models.CharField(
        max_length=100,
        blank=True,
        db_index=True,
        verbose_name="Código de respuesta",
    )

    provider_response_status = models.PositiveIntegerField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Estado HTTP",
    )

    provider_response = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Respuesta del proveedor",
    )

    provider_response_text = models.TextField(
        blank=True,
        verbose_name="Respuesta textual",
    )

    queued_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Fecha de ingreso a cola",
    )

    first_attempt_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Primer intento",
    )

    last_attempt_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Último intento",
    )

    next_retry_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Próximo reintento",
    )

    sent_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Fecha de envío",
    )

    delivered_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Fecha de entrega",
    )

    opened_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Fecha de apertura",
    )

    acknowledged_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Fecha de reconocimiento",
    )

    failed_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Fecha de fallo",
    )

    cancelled_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Fecha de cancelación",
    )

    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Fecha de expiración",
    )

    duration_ms = models.PositiveBigIntegerField(
        null=True,
        blank=True,
        verbose_name="Duración del envío",
    )

    delivery_latency_ms = models.PositiveBigIntegerField(
        null=True,
        blank=True,
        verbose_name="Latencia de entrega",
    )

    attempt_count = models.PositiveIntegerField(
        default=0,
        verbose_name="Intentos realizados",
    )

    maximum_attempts = models.PositiveIntegerField(
        default=3,
        verbose_name="Intentos máximos",
    )

    retry_delay_seconds = models.PositiveIntegerField(
        default=300,
        verbose_name="Espera entre reintentos",
    )

    last_error_code = models.CharField(
        max_length=150,
        blank=True,
        db_index=True,
        verbose_name="Código del último error",
    )

    last_error_message = models.TextField(
        blank=True,
        verbose_name="Último error",
    )

    last_error_details = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Detalle del último error",
    )

    cancellation_reason = models.TextField(
        blank=True,
        verbose_name="Motivo de cancelación",
    )

    suppression_reason = models.TextField(
        blank=True,
        verbose_name="Motivo de supresión",
    )

    bounce_reason = models.TextField(
        blank=True,
        verbose_name="Motivo de rebote",
    )

    is_retryable = models.BooleanField(
        default=True,
        db_index=True,
        verbose_name="Permite reintento",
    )

    is_duplicate = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="Duplicada",
    )

    contains_sensitive_data = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="Contiene información sensible",
    )

    was_sanitized = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="Contenido depurado",
    )

    metadata = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Metadatos",
    )

    notes = models.TextField(
        blank=True,
        verbose_name="Observaciones",
    )

    class Meta:
        verbose_name = "Entrega de notificación"
        verbose_name_plural = "Entregas de notificaciones"
        ordering = (
            "-created_at",
        )
        indexes = [
            models.Index(
                fields=[
                    "notification",
                    "channel",
                    "status",
                ],
                name="mon_ndelivery_notification_idx",
            ),
            models.Index(
                fields=[
                    "customer",
                    "channel",
                    "created_at",
                ],
                name="mon_ndelivery_customer_idx",
            ),
            models.Index(
                fields=[
                    "recipient_identifier",
                    "channel",
                    "created_at",
                ],
                name="mon_ndelivery_recipient_idx",
            ),
            models.Index(
                fields=[
                    "status",
                    "next_retry_at",
                ],
                name="mon_ndelivery_retry_idx",
            ),
            models.Index(
                fields=[
                    "provider_name",
                    "provider_message_id",
                ],
                name="mon_ndelivery_provider_idx",
            ),
            models.Index(
                fields=[
                    "last_error_code",
                    "created_at",
                ],
                name="mon_ndelivery_error_idx",
            ),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "notification",
                    "delivery_key",
                ],
                condition=models.Q(
                    is_duplicate=False,
                    archived_at__isnull=True,
                ),
                name="unique_notification_delivery_key",
            ),
        ]

    def __str__(self):
        return (
            f"{self.notification} - "
            f"{self.get_channel_display()} - "
            f"{self.recipient_identifier}"
        )

    def is_terminal(self):
        return self.status in {
            self.Status.DELIVERED,
            self.Status.OPENED,
            self.Status.ACKNOWLEDGED,
            self.Status.CANCELLED,
            self.Status.EXPIRED,
            self.Status.REJECTED,
            self.Status.BOUNCED,
            self.Status.SUPPRESSED,
        }

    def calculate_delivery_key(self):
        values = [
            str(self.notification_id or ""),
            str(self.channel or ""),
            str(self.recipient_type or ""),
            str(self.recipient_identifier or "").strip().lower(),
            str(self.destination_url or "").strip().lower(),
        ]

        return hashlib.sha256(
            "|".join(values).encode("utf-8")
        ).hexdigest()

    def calculate_request_body_hash(self):
        body = {
            "subject": self.subject,
            "title": self.title,
            "message": self.message,
            "html_body": self.html_body,
            "action_url": self.action_url,
            "payload": self.payload,
        }

        serialized = json.dumps(
            body,
            sort_keys=True,
            ensure_ascii=False,
            default=str,
        )

        return hashlib.sha256(
            serialized.encode("utf-8")
        ).hexdigest()

    def calculate_duration(self):
        if self.first_attempt_at and self.sent_at:
            milliseconds = (
                self.sent_at - self.first_attempt_at
            ).total_seconds() * 1000

            self.duration_ms = max(
                int(milliseconds),
                0,
            )

    def calculate_delivery_latency(self):
        if self.sent_at and self.delivered_at:
            milliseconds = (
                self.delivered_at - self.sent_at
            ).total_seconds() * 1000

            self.delivery_latency_ms = max(
                int(milliseconds),
                0,
            )

    def can_retry(self, current_datetime=None):
        current_datetime = (
            current_datetime
            or timezone.now()
        )

        if not self.is_retryable:
            return False

        if self.is_terminal():
            return False

        if self.status not in {
            self.Status.FAILED,
            self.Status.RETRY_SCHEDULED,
        }:
            return False

        if self.attempt_count >= self.maximum_attempts:
            return False

        if (
            self.next_retry_at
            and self.next_retry_at > current_datetime
        ):
            return False

        if (
            self.expires_at
            and self.expires_at <= current_datetime
        ):
            return False

        return True

    def mark_queued(self):
        if self.is_terminal():
            raise ValidationError(
                "Una entrega finalizada no puede regresar a cola."
            )

        self.status = self.Status.QUEUED
        self.queued_at = timezone.now()
        self.next_retry_at = None

        self.save(
            update_fields=[
                "status",
                "queued_at",
                "next_retry_at",
                "updated_at",
            ]
        )

    def begin_attempt(self):
        if self.is_terminal():
            raise ValidationError(
                "Una entrega finalizada no admite más intentos."
            )

        if self.attempt_count >= self.maximum_attempts:
            raise ValidationError(
                "La entrega alcanzó el máximo de intentos."
            )

        now = timezone.now()

        self.status = self.Status.SENDING
        self.attempt_count += 1
        self.first_attempt_at = (
            self.first_attempt_at
            or now
        )
        self.last_attempt_at = now
        self.next_retry_at = None
        self.failed_at = None
        self.last_error_code = ""
        self.last_error_message = ""
        self.last_error_details = {}

        self.save(
            update_fields=[
                "status",
                "attempt_count",
                "first_attempt_at",
                "last_attempt_at",
                "next_retry_at",
                "failed_at",
                "last_error_code",
                "last_error_message",
                "last_error_details",
                "updated_at",
            ]
        )

    def mark_sent(
        self,
        *,
        provider_name="",
        provider_message_id="",
        provider_request_id="",
        provider_response_code="",
        provider_response_status=None,
        provider_response=None,
        provider_response_text="",
    ):
        if self.status != self.Status.SENDING:
            raise ValidationError(
                "La entrega debe estar en proceso de envío."
            )

        now = timezone.now()

        self.status = self.Status.SENT
        self.provider_status = (
            self.ProviderStatus.SENT
        )
        self.sent_at = now
        self.provider_name = str(
            provider_name or ""
        ).strip()
        self.provider_message_id = str(
            provider_message_id or ""
        ).strip()
        self.provider_request_id = str(
            provider_request_id or ""
        ).strip()
        self.provider_response_code = str(
            provider_response_code or ""
        ).strip()
        self.provider_response_status = (
            provider_response_status
        )
        self.provider_response = (
            provider_response
            if provider_response is not None
            else {}
        )
        self.provider_response_text = str(
            provider_response_text or ""
        ).strip()
        self.last_error_code = ""
        self.last_error_message = ""
        self.last_error_details = {}

        self.calculate_duration()
        self.save()

    def mark_delivered(
        self,
        *,
        delivered_at=None,
        provider_status=ProviderStatus.DELIVERED,
        provider_response=None,
    ):
        if self.status not in {
            self.Status.SENT,
            self.Status.DELIVERED,
            self.Status.OPENED,
        }:
            raise ValidationError(
                "La entrega no se encuentra enviada."
            )

        self.status = self.Status.DELIVERED
        self.provider_status = provider_status
        self.delivered_at = (
            delivered_at
            or timezone.now()
        )

        if provider_response is not None:
            self.provider_response = provider_response

        self.calculate_delivery_latency()
        self.save()

    def mark_opened(
        self,
        *,
        opened_at=None,
    ):
        if self.status not in {
            self.Status.SENT,
            self.Status.DELIVERED,
            self.Status.OPENED,
        }:
            raise ValidationError(
                "La entrega aún no fue enviada."
            )

        self.status = self.Status.OPENED
        self.provider_status = (
            self.ProviderStatus.OPENED
        )
        self.opened_at = (
            opened_at
            or timezone.now()
        )

        if not self.delivered_at:
            self.delivered_at = self.opened_at

        self.calculate_delivery_latency()
        self.save()

    def acknowledge(
        self,
        *,
        acknowledged_at=None,
    ):
        if self.status not in {
            self.Status.SENT,
            self.Status.DELIVERED,
            self.Status.OPENED,
            self.Status.ACKNOWLEDGED,
        }:
            raise ValidationError(
                "La entrega no puede reconocerse."
            )

        self.status = self.Status.ACKNOWLEDGED
        self.acknowledged_at = (
            acknowledged_at
            or timezone.now()
        )

        if not self.delivered_at:
            self.delivered_at = self.acknowledged_at

        self.calculate_delivery_latency()
        self.save()

    def mark_failed(
        self,
        *,
        error_message,
        error_code="",
        error_details=None,
        provider_status=ProviderStatus.FAILED,
        provider_response_code="",
        provider_response_status=None,
        provider_response=None,
        provider_response_text="",
        retryable=True,
        retry_at=None,
    ):
        if self.is_terminal():
            raise ValidationError(
                "Una entrega finalizada no puede marcarse como fallida."
            )

        now = timezone.now()

        self.failed_at = now
        self.last_error_code = str(
            error_code or ""
        ).strip().upper()
        self.last_error_message = str(
            error_message or ""
        ).strip()
        self.last_error_details = (
            error_details
            if error_details is not None
            else {}
        )
        self.provider_status = provider_status
        self.provider_response_code = str(
            provider_response_code or ""
        ).strip()
        self.provider_response_status = (
            provider_response_status
        )
        self.provider_response = (
            provider_response
            if provider_response is not None
            else {}
        )
        self.provider_response_text = str(
            provider_response_text or ""
        ).strip()
        self.is_retryable = bool(
            retryable
        )

        can_schedule_retry = (
            self.is_retryable
            and self.attempt_count < self.maximum_attempts
            and (
                not self.expires_at
                or self.expires_at > now
            )
        )

        if can_schedule_retry:
            self.status = self.Status.RETRY_SCHEDULED
            self.next_retry_at = (
                retry_at
                or (
                    now
                    + timezone.timedelta(
                        seconds=self.retry_delay_seconds
                    )
                )
            )
        else:
            self.status = self.Status.FAILED
            self.next_retry_at = None

        self.save()

    def mark_rejected(
        self,
        *,
        reason,
        provider_response=None,
    ):
        self.status = self.Status.REJECTED
        self.provider_status = (
            self.ProviderStatus.REJECTED
        )
        self.failed_at = timezone.now()
        self.is_retryable = False
        self.next_retry_at = None
        self.last_error_code = "DELIVERY_REJECTED"
        self.last_error_message = str(
            reason or ""
        ).strip()

        if provider_response is not None:
            self.provider_response = provider_response

        self.save()

    def mark_bounced(
        self,
        *,
        reason,
        provider_response=None,
    ):
        self.status = self.Status.BOUNCED
        self.provider_status = (
            self.ProviderStatus.BOUNCED
        )
        self.bounce_reason = str(
            reason or ""
        ).strip()
        self.failed_at = timezone.now()
        self.is_retryable = False
        self.next_retry_at = None

        if provider_response is not None:
            self.provider_response = provider_response

        self.save()

    def suppress(
        self,
        *,
        reason,
    ):
        if self.is_terminal():
            return self

        self.status = self.Status.SUPPRESSED
        self.suppression_reason = str(
            reason or ""
        ).strip()
        self.is_retryable = False
        self.next_retry_at = None

        self.save()

        return self

    def cancel(
        self,
        *,
        reason,
    ):
        if self.is_terminal():
            return self

        self.status = self.Status.CANCELLED
        self.cancelled_at = timezone.now()
        self.cancellation_reason = str(
            reason or ""
        ).strip()
        self.is_retryable = False
        self.next_retry_at = None

        self.save()

        return self

    def expire(self):
        if self.is_terminal():
            return self

        self.status = self.Status.EXPIRED
        self.is_retryable = False
        self.next_retry_at = None

        self.save(
            update_fields=[
                "status",
                "is_retryable",
                "next_retry_at",
                "updated_at",
            ]
        )

        return self

    def mark_duplicate(
        self,
        original_delivery,
    ):
        if (
            original_delivery.notification_id
            != self.notification_id
        ):
            raise ValidationError(
                "La entrega original pertenece a otra notificación."
            )

        self.is_duplicate = True
        self.duplicate_of = original_delivery
        self.status = self.Status.SUPPRESSED
        self.suppression_reason = (
            "Entrega duplicada para el mismo destinatario y canal."
        )
        self.is_retryable = False
        self.next_retry_at = None

        self.save()

    def clean(self):
        super().clean()

        text_fields = [
            "recipient_identifier",
            "recipient_name",
            "recipient_email",
            "recipient_role_code",
            "recipient_device_token_reference",
            "destination_url",
            "subject",
            "title",
            "message",
            "html_body",
            "action_url",
            "provider_name",
            "provider_message_id",
            "provider_request_id",
            "provider_response_code",
            "provider_response_text",
            "last_error_code",
            "last_error_message",
            "cancellation_reason",
            "suppression_reason",
            "bounce_reason",
            "notes",
        ]

        for field_name in text_fields:
            value = getattr(
                self,
                field_name,
                "",
            )

            setattr(
                self,
                field_name,
                str(value or "").strip(),
            )

        self.recipient_role_code = (
            self.recipient_role_code.upper()
        )
        self.last_error_code = (
            self.last_error_code.upper()
        )

        if not self.notification_id:
            raise ValidationError(
                {
                    "notification": (
                        "La notificación es obligatoria."
                    ),
                }
            )

        if not self.channel:
            raise ValidationError(
                {
                    "channel": (
                        "El canal es obligatorio."
                    ),
                }
            )

        if not self.recipient_identifier:
            raise ValidationError(
                {
                    "recipient_identifier": (
                        "El destinatario es obligatorio."
                    ),
                }
            )

        if not self.message:
            raise ValidationError(
                {
                    "message": (
                        "El mensaje es obligatorio."
                    ),
                }
            )

        if self.notification.rule_id != self.rule_id:
            raise ValidationError(
                {
                    "rule": (
                        "La regla no coincide con la notificación."
                    ),
                }
            )

        if (
            self.customer_id
            and self.branch_id
            and self.branch.partner_id
            != self.customer_id
        ):
            raise ValidationError(
                {
                    "branch": (
                        "La sede no pertenece al cliente."
                    ),
                }
            )

        if (
            self.agent_id
            and self.customer_id
            and self.agent.customer_id
            != self.customer_id
        ):
            raise ValidationError(
                {
                    "agent": (
                        "El agente no pertenece al cliente."
                    ),
                }
            )

        if (
            self.device_id
            and self.customer_id
            and self.device.customer_id
            != self.customer_id
        ):
            raise ValidationError(
                {
                    "device": (
                        "El dispositivo no pertenece al cliente."
                    ),
                }
            )

        if (
            self.device_id
            and self.agent_id
            and self.device.agent_id
            != self.agent_id
        ):
            raise ValidationError(
                {
                    "device": (
                        "El dispositivo no pertenece al agente."
                    ),
                }
            )

        if (
            self.recipient_contact_id
            and self.customer_id
            and self.recipient_contact.partner_id
            != self.customer_id
        ):
            raise ValidationError(
                {
                    "recipient_contact": (
                        "El contacto no pertenece al cliente."
                    ),
                }
            )

        if self.channel == self.Channel.EMAIL:
            if not self.recipient_email:
                raise ValidationError(
                    {
                        "recipient_email": (
                            "El canal de correo requiere "
                            "un correo destinatario."
                        ),
                    }
                )

            if not self.subject:
                raise ValidationError(
                    {
                        "subject": (
                            "El correo requiere un asunto."
                        ),
                    }
                )

        if self.channel == self.Channel.WEBHOOK:
            if not self.destination_url:
                raise ValidationError(
                    {
                        "destination_url": (
                            "El webhook requiere una URL."
                        ),
                    }
                )

        if self.channel == self.Channel.PUSH:
            if not self.recipient_device_token_reference:
                raise ValidationError(
                    {
                        "recipient_device_token_reference": (
                            "La notificación push requiere una "
                            "referencia de dispositivo."
                        ),
                    }
                )

        if self.channel == self.Channel.IN_APP:
            if not self.recipient_user_id:
                raise ValidationError(
                    {
                        "recipient_user": (
                            "La notificación interna requiere "
                            "un usuario."
                        ),
                    }
                )

        if self.maximum_attempts < 1:
            raise ValidationError(
                {
                    "maximum_attempts": (
                        "Debe permitirse al menos un intento."
                    ),
                }
            )

        if self.attempt_count > self.maximum_attempts:
            raise ValidationError(
                {
                    "attempt_count": (
                        "Los intentos realizados no pueden superar "
                        "el máximo configurado."
                    ),
                }
            )

        if self.retry_delay_seconds < 1:
            raise ValidationError(
                {
                    "retry_delay_seconds": (
                        "El tiempo de reintento debe ser "
                        "mayor que cero."
                    ),
                }
            )

        if (
            self.last_attempt_at
            and self.first_attempt_at
            and self.last_attempt_at < self.first_attempt_at
        ):
            raise ValidationError(
                {
                    "last_attempt_at": (
                        "El último intento no puede ser anterior "
                        "al primero."
                    ),
                }
            )

        if (
            self.sent_at
            and self.first_attempt_at
            and self.sent_at < self.first_attempt_at
        ):
            raise ValidationError(
                {
                    "sent_at": (
                        "El envío no puede ser anterior "
                        "al primer intento."
                    ),
                }
            )

        if (
            self.delivered_at
            and self.sent_at
            and self.delivered_at < self.sent_at
        ):
            raise ValidationError(
                {
                    "delivered_at": (
                        "La entrega no puede ser anterior "
                        "al envío."
                    ),
                }
            )

        if (
            self.opened_at
            and self.delivered_at
            and self.opened_at < self.delivered_at
        ):
            raise ValidationError(
                {
                    "opened_at": (
                        "La apertura no puede ser anterior "
                        "a la entrega."
                    ),
                }
            )

        if (
            self.next_retry_at
            and self.expires_at
            and self.next_retry_at >= self.expires_at
        ):
            raise ValidationError(
                {
                    "next_retry_at": (
                        "El reintento debe programarse antes "
                        "de la expiración."
                    ),
                }
            )

        if (
            self.status == self.Status.FAILED
            and not self.last_error_message
        ):
            raise ValidationError(
                {
                    "last_error_message": (
                        "Una entrega fallida debe registrar "
                        "el error."
                    ),
                }
            )

        if (
            self.status == self.Status.CANCELLED
            and not self.cancellation_reason
        ):
            raise ValidationError(
                {
                    "cancellation_reason": (
                        "Debe indicar el motivo de cancelación."
                    ),
                }
            )

        if (
            self.status == self.Status.SUPPRESSED
            and not self.suppression_reason
        ):
            raise ValidationError(
                {
                    "suppression_reason": (
                        "Debe indicar el motivo de supresión."
                    ),
                }
            )

        if (
            self.status == self.Status.BOUNCED
            and not self.bounce_reason
        ):
            raise ValidationError(
                {
                    "bounce_reason": (
                        "Debe indicar el motivo del rebote."
                    ),
                }
            )

        if (
            self.is_duplicate
            and not self.duplicate_of_id
        ):
            raise ValidationError(
                {
                    "duplicate_of": (
                        "Debe indicar la entrega original."
                    ),
                }
            )

        if (
            not self.is_duplicate
            and self.duplicate_of_id
        ):
            raise ValidationError(
                {
                    "is_duplicate": (
                        "Debe marcar la entrega como duplicada."
                    ),
                }
            )

        if (
            self.duplicate_of_id
            and self.duplicate_of_id == self.id
        ):
            raise ValidationError(
                {
                    "duplicate_of": (
                        "Una entrega no puede duplicarse "
                        "a sí misma."
                    ),
                }
            )

        dict_fields = [
            "payload",
            "request_headers",
            "provider_response",
            "last_error_details",
            "metadata",
        ]

        for field_name in dict_fields:
            if not isinstance(
                getattr(
                    self,
                    field_name,
                ),
                dict,
            ):
                raise ValidationError(
                    {
                        field_name: (
                            "Este campo debe ser un objeto."
                        ),
                    }
                )

        self.delivery_key = (
            self.calculate_delivery_key()
        )
        self.request_body_hash = (
            self.calculate_request_body_hash()
        )
        self.calculate_duration()
        self.calculate_delivery_latency()

    def save(self, *args, **kwargs):
        if self.notification_id:
            self.rule = self.notification.rule
            self.customer = self.notification.customer
            self.branch = self.notification.branch
            self.agent = self.notification.agent
            self.device = self.notification.device

            if not self.title:
                self.title = self.notification.title

            if not self.message:
                self.message = self.notification.message

            if not self.action_url:
                self.action_url = self.notification.action_url

        if self.recipient_user_id:
            self.recipient_type = self.RecipientType.USER
            self.recipient_identifier = str(
                self.recipient_user_id
            )

            if not self.recipient_name:
                self.recipient_name = str(
                    self.recipient_user
                )

            if (
                self.channel == self.Channel.EMAIL
                and not self.recipient_email
            ):
                self.recipient_email = str(
                    getattr(
                        self.recipient_user,
                        "email",
                        "",
                    )
                    or ""
                ).strip()

        elif self.recipient_contact_id:
            self.recipient_type = self.RecipientType.CONTACT
            self.recipient_identifier = str(
                self.recipient_contact_id
            )

            if not self.recipient_name:
                self.recipient_name = str(
                    self.recipient_contact
                )

            if (
                self.channel == self.Channel.EMAIL
                and not self.recipient_email
            ):
                self.recipient_email = str(
                    getattr(
                        self.recipient_contact,
                        "email",
                        "",
                    )
                    or ""
                ).strip()

        elif self.recipient_email:
            self.recipient_type = self.RecipientType.EMAIL
            self.recipient_identifier = (
                self.recipient_email.lower()
            )

        elif self.recipient_role_code:
            self.recipient_type = self.RecipientType.ROLE
            self.recipient_identifier = (
                self.recipient_role_code.upper()
            )

        elif self.channel == self.Channel.WEBHOOK:
            self.recipient_type = self.RecipientType.WEBHOOK
            self.recipient_identifier = self.destination_url

        self.recipient_identifier = str(
            self.recipient_identifier or ""
        ).strip()

        self.recipient_email = str(
            self.recipient_email or ""
        ).strip().lower()

        self.recipient_role_code = str(
            self.recipient_role_code or ""
        ).strip().upper()

        self.last_error_code = str(
            self.last_error_code or ""
        ).strip().upper()

        self.delivery_key = (
            self.calculate_delivery_key()
        )
        self.request_body_hash = (
            self.calculate_request_body_hash()
        )
        self.calculate_duration()
        self.calculate_delivery_latency()
        self.full_clean()

        return super().save(
            *args,
            **kwargs,
        )

    def archive(
        self,
        user=None,
        reason="",
        save=True,
    ):
        raise ValidationError(
            "Las entregas históricas no pueden archivarse."
        )

    def restore(
        self,
        user=None,
        save=True,
    ):
        raise ValidationError(
            "Las entregas históricas no pueden restaurarse."
        )