# -*- coding: utf-8 -*-
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html

from .models import (
    EmailVerificationCode,
    LoginAttempt,
    PasskeyCredential,
    PasswordHistory,
    PasswordResetToken,
    RecoveryCode,
    User,
    UserAuditLog,
    UserDataAccessLog,
    UserSecuritySettings,
    UserSession,
)


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    model = User

    list_display = (
        "photo_preview",
        "email",
        "dni",
        "display_full_name",
        "job_title",
        "department_name",
        "is_active",
        "is_staff",
        "is_verified",
        "registration_source",
    )

    list_filter = (
        "is_active",
        "is_staff",
        "is_superuser",
        "is_verified",
        "dni_data_verified",
        "registration_source",
        "must_change_password",
        "date_joined",
    )

    search_fields = (
        "email",
        "dni",
        "username",
        "first_name",
        "paternal_last_name",
        "maternal_last_name",
        "personal_phone",
        "work_phone",
        "job_title",
        "department_name",
        "company_name",
    )

    ordering = (
        "first_name",
        "paternal_last_name",
        "maternal_last_name",
        "email",
    )

    readonly_fields = (
        "photo_preview_large",
        "dni_verified_at",
        "email_verified_at",
        "password_changed_at",
        "failed_login_attempts",
        "locked_until",
        "archived_at",
        "created_at",
        "updated_at",
        "date_joined",
        "last_login",
        "created_by",
        "updated_by",
        "archived_by",
    )

    fieldsets = (
        (
            "Acceso al sistema",
            {
                "fields": (
                    "email",
                    "username",
                    "password",
                ),
            },
        ),
        (
            "Documento e identidad",
            {
                "fields": (
                    "dni",
                    "registration_source",
                    "dni_data_verified",
                    "dni_verified_at",
                    "first_name",
                    "paternal_last_name",
                    "maternal_last_name",
                    "last_name",
                ),
            },
        ),
        (
            "Fotografía",
            {
                "fields": (
                    "photo",
                    "photo_preview_large",
                ),
            },
        ),
        (
            "Datos de contacto",
            {
                "fields": (
                    "personal_phone",
                    "work_phone",
                    "work_extension",
                    "address",
                    "ubigeo",
                    "district",
                    "province",
                    "region",
                ),
            },
        ),
        (
            "Información laboral",
            {
                "fields": (
                    "job_title",
                    "department_name",
                    "company_name",
                ),
            },
        ),
        (
            "Estado y seguridad",
            {
                "fields": (
                    "is_active",
                    "is_verified",
                    "email_verified_at",
                    "must_change_password",
                    "password_changed_at",
                    "failed_login_attempts",
                    "locked_until",
                ),
            },
        ),
        (
            "Permisos",
            {
                "fields": (
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (
            "Archivado",
            {
                "fields": (
                    "archived_at",
                    "archived_by",
                    "archived_reason",
                ),
            },
        ),
        (
            "Auditoría",
            {
                "fields": (
                    "created_at",
                    "created_by",
                    "updated_at",
                    "updated_by",
                    "date_joined",
                    "last_login",
                ),
            },
        ),
    )

    add_fieldsets = (
        (
            "Acceso al sistema",
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "username",
                    "password1",
                    "password2",
                ),
            },
        ),
        (
            "Identificación",
            {
                "classes": ("wide",),
                "fields": (
                    "dni",
                    "first_name",
                    "paternal_last_name",
                    "maternal_last_name",
                    "registration_source",
                ),
            },
        ),
        (
            "Información laboral",
            {
                "classes": ("wide",),
                "fields": (
                    "job_title",
                    "department_name",
                    "company_name",
                    "personal_phone",
                    "work_phone",
                ),
            },
        ),
        (
            "Estado y permisos",
            {
                "classes": ("wide",),
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "is_verified",
                    "must_change_password",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
    )

    @admin.display(description="Nombre completo")
    def display_full_name(self, obj):
        return obj.full_name

    @admin.display(description="Foto")
    def photo_preview(self, obj):
        if not obj.photo:
            return "—"

        return format_html(
            '<img src="{}" width="38" height="38" '
            'style="object-fit:cover;border-radius:50%;" />',
            obj.photo.url,
        )

    @admin.display(description="Vista previa")
    def photo_preview_large(self, obj):
        if not obj.photo:
            return "Sin fotografía"

        return format_html(
            '<img src="{}" width="140" height="140" '
            'style="object-fit:cover;border-radius:14px;" />',
            obj.photo.url,
        )

    def save_model(self, request, obj, form, change):
        if change:
            obj.updated_by = request.user
        elif not obj.created_by:
            obj.created_by = request.user
            obj.updated_by = request.user

        super().save_model(request, obj, form, change)


@admin.register(UserSecuritySettings)
class UserSecuritySettingsAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "two_factor_enabled",
        "two_factor_method",
        "allow_password_login",
        "allow_passkey_login",
        "updated_at",
    )

    list_filter = (
        "two_factor_enabled",
        "two_factor_method",
        "allow_password_login",
        "allow_passkey_login",
    )

    search_fields = (
        "user__email",
        "user__dni",
        "user__first_name",
    )


@admin.register(PasskeyCredential)
class PasskeyCredentialAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "user",
        "device_type",
        "is_active",
        "last_used_at",
        "created_at",
    )

    list_filter = (
        "is_active",
        "device_type",
        "backed_up",
    )

    search_fields = (
        "name",
        "user__email",
        "user__dni",
        "credential_id",
    )

    readonly_fields = (
        "credential_id",
        "public_key",
        "sign_count",
        "last_used_at",
        "created_at",
        "updated_at",
    )


@admin.register(UserSession)
class UserSessionAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "device_name",
        "browser",
        "ip_address",
        "is_active",
        "last_activity_at",
        "expires_at",
    )

    list_filter = (
        "is_active",
        "authenticated_with_password",
        "authenticated_with_two_factor",
        "authenticated_with_passkey",
        "browser",
        "operating_system",
    )

    search_fields = (
        "user__email",
        "user__dni",
        "device_name",
        "ip_address",
    )

    readonly_fields = (
        "token_hash",
        "refresh_token_hash",
        "created_at",
        "updated_at",
        "last_activity_at",
        "revoked_at",
    )


@admin.register(LoginAttempt)
class LoginAttemptAdmin(admin.ModelAdmin):
    list_display = (
        "email_entered",
        "user",
        "result",
        "ip_address",
        "attempted_at",
    )

    list_filter = (
        "result",
        "browser",
        "operating_system",
        "attempted_at",
    )

    search_fields = (
        "email_entered",
        "user__email",
        "ip_address",
        "failure_reason",
    )

    readonly_fields = (
        "user",
        "email_entered",
        "result",
        "failure_reason",
        "ip_address",
        "user_agent",
        "device_name",
        "browser",
        "operating_system",
        "attempted_at",
    )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(UserAuditLog)
class UserAuditLogAdmin(admin.ModelAdmin):
    list_display = (
        "created_at",
        "actor",
        "action",
        "target_user",
        "status",
        "ip_address",
    )

    list_filter = (
        "action",
        "status",
        "created_at",
    )

    search_fields = (
        "actor__email",
        "target_user__email",
        "description",
        "ip_address",
    )

    readonly_fields = (
        "actor",
        "target_user",
        "action",
        "status",
        "description",
        "changed_fields",
        "metadata",
        "error_message",
        "ip_address",
        "user_agent",
        "device_name",
        "browser",
        "operating_system",
        "request_method",
        "request_path",
        "created_at",
    )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(UserDataAccessLog)
class UserDataAccessLogAdmin(admin.ModelAdmin):
    list_display = (
        "created_at",
        "user",
        "target_user",
        "data_type",
        "access_type",
        "ip_address",
    )

    list_filter = (
        "data_type",
        "access_type",
        "created_at",
    )

    search_fields = (
        "user__email",
        "target_user__email",
        "purpose",
        "ip_address",
    )

    readonly_fields = (
        "user",
        "target_user",
        "data_type",
        "access_type",
        "purpose",
        "ip_address",
        "request_path",
        "created_at",
    )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(RecoveryCode)
class RecoveryCodeAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "used_at",
        "created_at",
    )

    search_fields = (
        "user__email",
        "user__dni",
    )

    readonly_fields = (
        "user",
        "code_hash",
        "used_at",
        "created_at",
    )


@admin.register(EmailVerificationCode)
class EmailVerificationCodeAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "expires_at",
        "used_at",
        "attempts",
        "created_at",
    )

    search_fields = (
        "user__email",
        "user__dni",
    )

    readonly_fields = (
        "user",
        "code_hash",
        "expires_at",
        "used_at",
        "attempts",
        "created_at",
    )


@admin.register(PasswordResetToken)
class PasswordResetTokenAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "expires_at",
        "used_at",
        "requested_ip",
        "created_at",
    )

    search_fields = (
        "user__email",
        "user__dni",
        "requested_ip",
    )

    readonly_fields = (
        "user",
        "token_hash",
        "expires_at",
        "used_at",
        "requested_ip",
        "user_agent",
        "created_at",
    )


@admin.register(PasswordHistory)
class PasswordHistoryAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "created_at",
    )

    search_fields = (
        "user__email",
        "user__dni",
    )

    readonly_fields = (
        "user",
        "password_hash",
        "created_at",
    )