# -*- coding: utf-8 -*-
from calendar import monthrange
from datetime import datetime, time, timedelta
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from .base import MonitoringBaseModel


class MonitoringReportSchedule(MonitoringBaseModel):
    class ReportType(models.TextChoices):
        FLEET_SUMMARY = 'fleet_summary', 'Resumen de flota'
        DEVICE_DETAIL = 'device_detail', 'Detalle de dispositivo'
        COUNTERS = 'counters', 'Contadores'
        CONSUMABLES = 'consumables', 'Consumibles'
        COMPONENTS = 'components', 'Componentes'
        ALERTS = 'alerts', 'Alertas'
        EVENTS = 'events', 'Eventos'
        AVAILABILITY = 'availability', 'Disponibilidad'
        AGENT_HEALTH = 'agent_health', 'Salud de agentes'
        JOBS = 'jobs', 'Trabajos'
        RAW_OIDS = 'raw_oids', 'OID originales'
        CUSTOM = 'custom', 'Personalizado'

    class Status(models.TextChoices):
        DRAFT = 'draft', 'Borrador'
        ACTIVE = 'active', 'Activo'
        PAUSED = 'paused', 'Pausado'
        DISABLED = 'disabled', 'Deshabilitado'
        COMPLETED = 'completed', 'Finalizado'

    class Frequency(models.TextChoices):
        ONCE = 'once', 'Una vez'
        DAILY = 'daily', 'Diario'
        WEEKLY = 'weekly', 'Semanal'
        MONTHLY = 'monthly', 'Mensual'
        QUARTERLY = 'quarterly', 'Trimestral'
        YEARLY = 'yearly', 'Anual'
        CUSTOM = 'custom', 'Personalizado'

    class PeriodType(models.TextChoices):
        PREVIOUS_DAY = 'previous_day', 'Día anterior'
        PREVIOUS_WEEK = 'previous_week', 'Semana anterior'
        PREVIOUS_MONTH = 'previous_month', 'Mes anterior'
        PREVIOUS_QUARTER = 'previous_quarter', 'Trimestre anterior'
        PREVIOUS_YEAR = 'previous_year', 'Año anterior'
        ROLLING_DAYS = 'rolling_days', 'Últimos días'
        MONTH_TO_DATE = 'month_to_date', 'Mes a la fecha'
        YEAR_TO_DATE = 'year_to_date', 'Año a la fecha'
        CUSTOM = 'custom', 'Personalizado'

    class OutputFormat(models.TextChoices):
        PDF = 'pdf', 'PDF'
        XLSX = 'xlsx', 'Excel'
        CSV = 'csv', 'CSV'
        JSON = 'json', 'JSON'

    class DeliveryChannel(models.TextChoices):
        EMAIL = 'email', 'Correo electrónico'
        IN_APP = 'in_app', 'Copier OS'
        STORAGE = 'storage', 'Almacenamiento'
        WEBHOOK = 'webhook', 'Webhook'

    code = models.CharField(max_length=150, unique=True, db_index=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    report_type = models.CharField(max_length=40, choices=ReportType.choices, db_index=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT, db_index=True)
    frequency = models.CharField(max_length=20, choices=Frequency.choices, default=Frequency.MONTHLY, db_index=True)
    period_type = models.CharField(max_length=30, choices=PeriodType.choices, default=PeriodType.PREVIOUS_MONTH)

    customer = models.ForeignKey('partners.Partner', null=True, blank=True, on_delete=models.PROTECT, related_name='monitoring_report_schedules')
    branch = models.ForeignKey('partners.PartnerBranch', null=True, blank=True, on_delete=models.PROTECT, related_name='monitoring_report_schedules')
    agent = models.ForeignKey('monitoring.MonitoringAgent', null=True, blank=True, on_delete=models.PROTECT, related_name='report_schedules')
    network = models.ForeignKey('monitoring.MonitoringNetwork', null=True, blank=True, on_delete=models.PROTECT, related_name='report_schedules')
    device = models.ForeignKey('monitoring.MonitoredDevice', null=True, blank=True, on_delete=models.PROTECT, related_name='report_schedules')
    devices = models.ManyToManyField('monitoring.MonitoredDevice', blank=True, related_name='group_report_schedules')

    output_format = models.CharField(max_length=10, choices=OutputFormat.choices, default=OutputFormat.PDF)
    delivery_channels = models.JSONField(default=list, blank=True)
    recipient_users = models.ManyToManyField('users.User', blank=True, related_name='monitoring_report_schedules')
    recipient_emails = models.JSONField(default=list, blank=True)
    recipient_role_codes = models.JSONField(default=list, blank=True)
    webhook_url = models.URLField(max_length=1000, blank=True)

    timezone_name = models.CharField(max_length=100, default='America/Lima')
    run_time = models.TimeField(default=time(hour=8))
    day_of_week = models.PositiveSmallIntegerField(null=True, blank=True, help_text='1=lunes, 7=domingo')
    day_of_month = models.PositiveSmallIntegerField(null=True, blank=True)
    month_of_year = models.PositiveSmallIntegerField(null=True, blank=True)
    custom_interval_days = models.PositiveIntegerField(null=True, blank=True)
    rolling_days = models.PositiveIntegerField(null=True, blank=True)
    starts_at = models.DateTimeField(null=True, blank=True, db_index=True)
    ends_at = models.DateTimeField(null=True, blank=True, db_index=True)
    next_run_at = models.DateTimeField(null=True, blank=True, db_index=True)
    last_run_at = models.DateTimeField(null=True, blank=True, db_index=True)
    last_success_at = models.DateTimeField(null=True, blank=True)
    last_failure_at = models.DateTimeField(null=True, blank=True)

    execution_count = models.PositiveBigIntegerField(default=0)
    successful_execution_count = models.PositiveBigIntegerField(default=0)
    failed_execution_count = models.PositiveBigIntegerField(default=0)
    consecutive_failure_count = models.PositiveIntegerField(default=0)

    include_archived_devices = models.BooleanField(default=False)
    include_raw_data = models.BooleanField(default=False)
    include_charts = models.BooleanField(default=True)
    include_empty_sections = models.BooleanField(default=False)
    compress_output = models.BooleanField(default=False)
    attach_to_email = models.BooleanField(default=True)

    subject_template = models.CharField(max_length=500, blank=True)
    message_template = models.TextField(blank=True)
    filename_template = models.CharField(max_length=500, default='{report_code}_{period_start}_{period_end}')
    filters = models.JSONField(default=dict, blank=True)
    columns = models.JSONField(default=list, blank=True)
    grouping = models.JSONField(default=list, blank=True)
    sorting = models.JSONField(default=list, blank=True)
    report_options = models.JSONField(default=dict, blank=True)
    created_by = models.ForeignKey('users.User', null=True, blank=True, on_delete=models.SET_NULL, related_name='created_monitoring_report_schedules')
    last_error_message = models.TextField(blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ('next_run_at', 'name')
        indexes = [
            models.Index(fields=['status', 'next_run_at'], name='mon_rschedule_next_idx'),
            models.Index(fields=['customer', 'report_type', 'status'], name='mon_rschedule_customer_idx'),
            models.Index(fields=['device', 'status', 'next_run_at'], name='mon_rschedule_device_idx'),
        ]

    def __str__(self):
        return f'{self.code} - {self.name}'

    def get_timezone(self):
        try:
            return ZoneInfo(self.timezone_name)
        except ZoneInfoNotFoundError as exc:
            raise ValidationError({'timezone_name': 'La zona horaria no es válida.'}) from exc

    def get_period_range(self, reference_at=None):
        tz = self.get_timezone()
        local_reference = (reference_at or timezone.now()).astimezone(tz)
        today = local_reference.date()

        if self.period_type == self.PeriodType.PREVIOUS_DAY:
            end_date, start_date = today, today - timedelta(days=1)
        elif self.period_type == self.PeriodType.PREVIOUS_WEEK:
            end_date = today - timedelta(days=today.weekday())
            start_date = end_date - timedelta(days=7)
        elif self.period_type == self.PeriodType.PREVIOUS_MONTH:
            end_date = today.replace(day=1)
            start_date = (end_date - timedelta(days=1)).replace(day=1)
        elif self.period_type == self.PeriodType.PREVIOUS_QUARTER:
            end_month = ((today.month - 1) // 3) * 3 + 1
            end_date = today.replace(month=end_month, day=1)
            previous_end = end_date - timedelta(days=1)
            start_month = ((previous_end.month - 1) // 3) * 3 + 1
            start_date = previous_end.replace(month=start_month, day=1)
        elif self.period_type == self.PeriodType.PREVIOUS_YEAR:
            end_date = today.replace(month=1, day=1)
            start_date = end_date.replace(year=end_date.year - 1)
        elif self.period_type == self.PeriodType.ROLLING_DAYS:
            end_date = today + timedelta(days=1)
            start_date = end_date - timedelta(days=self.rolling_days or 1)
        elif self.period_type == self.PeriodType.MONTH_TO_DATE:
            start_date, end_date = today.replace(day=1), today + timedelta(days=1)
        elif self.period_type == self.PeriodType.YEAR_TO_DATE:
            start_date, end_date = today.replace(month=1, day=1), today + timedelta(days=1)
        else:
            start_raw = (self.report_options or {}).get('custom_period_start')
            end_raw = (self.report_options or {}).get('custom_period_end')
            if not start_raw or not end_raw:
                raise ValidationError('El periodo personalizado requiere inicio y fin.')
            try:
                start_date = datetime.fromisoformat(start_raw).date()
                end_date = datetime.fromisoformat(end_raw).date() + timedelta(days=1)
            except (TypeError, ValueError) as exc:
                raise ValidationError('El periodo personalizado no es válido.') from exc

        return (
            datetime.combine(start_date, time.min, tzinfo=tz).astimezone(ZoneInfo('UTC')),
            datetime.combine(end_date, time.min, tzinfo=tz).astimezone(ZoneInfo('UTC')),
        )

    def calculate_next_run(self, reference_at=None):
        if self.status != self.Status.ACTIVE:
            return None
        tz = self.get_timezone()
        ref = (reference_at or timezone.now()).astimezone(tz)
        candidate = datetime.combine(ref.date(), self.run_time, tzinfo=tz)
        if candidate <= ref:
            candidate += timedelta(days=1)

        if self.frequency == self.Frequency.ONCE:
            candidate = self.starts_at.astimezone(tz) if self.starts_at else candidate
        elif self.frequency == self.Frequency.WEEKLY:
            candidate += timedelta(days=((self.day_of_week or 1) - candidate.isoweekday()) % 7)
        elif self.frequency == self.Frequency.MONTHLY:
            target = self.day_of_month or 1
            day = min(target, monthrange(candidate.year, candidate.month)[1])
            candidate = candidate.replace(day=day)
            if candidate <= ref:
                year = candidate.year + (1 if candidate.month == 12 else 0)
                month = 1 if candidate.month == 12 else candidate.month + 1
                day = min(target, monthrange(year, month)[1])
                candidate = candidate.replace(year=year, month=month, day=day)
        elif self.frequency == self.Frequency.QUARTERLY:
            target = self.day_of_month or 1
            options = []
            for year in (ref.year, ref.year + 1):
                for month in (1, 4, 7, 10):
                    day = min(target, monthrange(year, month)[1])
                    dt = datetime(year, month, day, self.run_time.hour, self.run_time.minute, self.run_time.second, tzinfo=tz)
                    if dt > ref:
                        options.append(dt)
            candidate = min(options)
        elif self.frequency == self.Frequency.YEARLY:
            month = self.month_of_year or 1
            day = min(self.day_of_month or 1, monthrange(ref.year, month)[1])
            candidate = datetime(ref.year, month, day, self.run_time.hour, self.run_time.minute, self.run_time.second, tzinfo=tz)
            if candidate <= ref:
                year = ref.year + 1
                day = min(self.day_of_month or 1, monthrange(year, month)[1])
                candidate = candidate.replace(year=year, day=day)
        elif self.frequency == self.Frequency.CUSTOM:
            candidate = (ref + timedelta(days=self.custom_interval_days or 1)).replace(hour=self.run_time.hour, minute=self.run_time.minute, second=self.run_time.second, microsecond=0)

        if self.starts_at and candidate < self.starts_at.astimezone(tz):
            candidate = self.starts_at.astimezone(tz)
        if self.ends_at and candidate > self.ends_at.astimezone(tz):
            return None
        return candidate.astimezone(ZoneInfo('UTC'))

    def register_execution(self, successful, executed_at=None, error_message=''):
        executed_at = executed_at or timezone.now()
        self.execution_count += 1
        self.last_run_at = executed_at
        if successful:
            self.successful_execution_count += 1
            self.consecutive_failure_count = 0
            self.last_success_at = executed_at
            self.last_error_message = ''
        else:
            self.failed_execution_count += 1
            self.consecutive_failure_count += 1
            self.last_failure_at = executed_at
            self.last_error_message = str(error_message or '').strip()
        if self.frequency == self.Frequency.ONCE and successful:
            self.status = self.Status.COMPLETED
            self.next_run_at = None
        else:
            self.next_run_at = self.calculate_next_run(executed_at)
        self.save()

    def clean(self):
        super().clean()
        self.code = str(self.code or '').strip().upper()
        self.name = str(self.name or '').strip()
        if not self.code:
            raise ValidationError({'code': 'El código es obligatorio.'})
        if not self.name:
            raise ValidationError({'name': 'El nombre es obligatorio.'})
        self.get_timezone()
        if self.branch_id and self.branch.partner_id != self.customer_id:
            raise ValidationError({'branch': 'La sede no pertenece al cliente.'})
        if self.agent_id and self.customer_id and self.agent.customer_id != self.customer_id:
            raise ValidationError({'agent': 'El agente no pertenece al cliente.'})
        if self.network_id and self.agent_id and self.network.agent_id != self.agent_id:
            raise ValidationError({'network': 'La red no pertenece al agente.'})
        if self.device_id:
            if self.customer_id and self.device.customer_id != self.customer_id:
                raise ValidationError({'device': 'El dispositivo no pertenece al cliente.'})
            if self.agent_id and self.device.agent_id != self.agent_id:
                raise ValidationError({'device': 'El dispositivo no pertenece al agente.'})
        if self.starts_at and self.ends_at and self.ends_at <= self.starts_at:
            raise ValidationError({'ends_at': 'El fin debe ser posterior al inicio.'})
        if self.day_of_week is not None and not 1 <= self.day_of_week <= 7:
            raise ValidationError({'day_of_week': 'Debe estar entre 1 y 7.'})
        if self.day_of_month is not None and not 1 <= self.day_of_month <= 31:
            raise ValidationError({'day_of_month': 'Debe estar entre 1 y 31.'})
        if self.month_of_year is not None and not 1 <= self.month_of_year <= 12:
            raise ValidationError({'month_of_year': 'Debe estar entre 1 y 12.'})
        if self.frequency == self.Frequency.WEEKLY and self.day_of_week is None:
            raise ValidationError({'day_of_week': 'La frecuencia semanal requiere un día.'})
        if self.frequency in {self.Frequency.MONTHLY, self.Frequency.QUARTERLY, self.Frequency.YEARLY} and self.day_of_month is None:
            raise ValidationError({'day_of_month': 'La frecuencia seleccionada requiere un día.'})
        if self.frequency == self.Frequency.YEARLY and self.month_of_year is None:
            raise ValidationError({'month_of_year': 'La frecuencia anual requiere un mes.'})
        if self.frequency == self.Frequency.CUSTOM and not self.custom_interval_days:
            raise ValidationError({'custom_interval_days': 'Debe indicar el intervalo.'})
        if self.period_type == self.PeriodType.ROLLING_DAYS and not self.rolling_days:
            raise ValidationError({'rolling_days': 'Debe indicar los días.'})
        allowed = {v for v, _ in self.DeliveryChannel.choices}
        if not isinstance(self.delivery_channels, list) or not self.delivery_channels:
            raise ValidationError({'delivery_channels': 'Debe indicar al menos un canal.'})
        if any(channel not in allowed for channel in self.delivery_channels):
            raise ValidationError({'delivery_channels': 'Existen canales no válidos.'})
        if self.DeliveryChannel.WEBHOOK in self.delivery_channels and not self.webhook_url:
            raise ValidationError({'webhook_url': 'El webhook requiere una URL.'})
        for field in ('recipient_emails', 'recipient_role_codes', 'columns', 'grouping', 'sorting'):
            if not isinstance(getattr(self, field), list):
                raise ValidationError({field: 'Debe ser una lista.'})
        for field in ('filters', 'report_options'):
            if not isinstance(getattr(self, field), dict):
                raise ValidationError({field: 'Debe ser un objeto.'})

    def save(self, *args, **kwargs):
        self.code = str(self.code or '').strip().upper()
        self.delivery_channels = [str(v).strip().lower() for v in (self.delivery_channels or []) if str(v).strip()]
        self.recipient_emails = [str(v).strip().lower() for v in (self.recipient_emails or []) if str(v).strip()]
        self.recipient_role_codes = [str(v).strip().upper() for v in (self.recipient_role_codes or []) if str(v).strip()]
        if self.status == self.Status.ACTIVE and self.next_run_at is None:
            self.next_run_at = self.calculate_next_run()
        self.full_clean()
        return super().save(*args, **kwargs)
