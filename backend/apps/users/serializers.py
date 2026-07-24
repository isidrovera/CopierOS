# -*- coding: utf-8 -*-
from django.contrib.auth.password_validation import validate_password
from django.db import transaction
from rest_framework import serializers

from .models import User


class UserListSerializer(serializers.ModelSerializer):
    """
    Serializer reducido para listar usuarios.
    """

    full_name = serializers.CharField(
        read_only=True,
    )

    photo_url = serializers.SerializerMethodField()

    class Meta:
        model = User

        fields = (
            "id",
            "dni",
            "full_name",
            "first_name",
            "paternal_last_name",
            "maternal_last_name",
            "email",
            "personal_phone",
            "work_phone",
            "job_title",
            "department_name",
            "company_name",
            "photo_url",
            "is_active",
            "is_staff",
            "is_verified",
            "is_archived",
            "registration_source",
            "last_login",
            "date_joined",
        )

        read_only_fields = fields

    def get_photo_url(self, obj):
        if not obj.photo:
            return None

        request = self.context.get("request")

        if request:
            return request.build_absolute_uri(obj.photo.url)

        return obj.photo.url


class UserDetailSerializer(serializers.ModelSerializer):
    """
    Información completa de un usuario.
    """

    full_name = serializers.CharField(
        read_only=True,
    )

    photo_url = serializers.SerializerMethodField()

    is_archived = serializers.BooleanField(
        read_only=True,
    )

    is_locked = serializers.BooleanField(
        read_only=True,
    )

    created_by_name = serializers.CharField(
        source="created_by.full_name",
        read_only=True,
    )

    updated_by_name = serializers.CharField(
        source="updated_by.full_name",
        read_only=True,
    )

    archived_by_name = serializers.CharField(
        source="archived_by.full_name",
        read_only=True,
    )

    class Meta:
        model = User

        fields = (
            "id",
            "username",
            "email",
            "dni",
            "first_name",
            "last_name",
            "paternal_last_name",
            "maternal_last_name",
            "full_name",
            "photo",
            "photo_url",
            "personal_phone",
            "work_phone",
            "work_extension",
            "job_title",
            "department_name",
            "company_name",
            "address",
            "ubigeo",
            "district",
            "province",
            "region",
            "registration_source",
            "dni_data_verified",
            "dni_verified_at",
            "is_verified",
            "email_verified_at",
            "must_change_password",
            "password_changed_at",
            "failed_login_attempts",
            "locked_until",
            "is_locked",
            "is_active",
            "is_staff",
            "is_superuser",
            "is_archived",
            "archived_at",
            "archived_reason",
            "created_at",
            "updated_at",
            "date_joined",
            "last_login",
            "created_by",
            "created_by_name",
            "updated_by",
            "updated_by_name",
            "archived_by",
            "archived_by_name",
        )

        read_only_fields = (
            "id",
            "username",
            "full_name",
            "photo_url",
            "dni_data_verified",
            "dni_verified_at",
            "email_verified_at",
            "password_changed_at",
            "failed_login_attempts",
            "locked_until",
            "is_locked",
            "is_archived",
            "archived_at",
            "archived_reason",
            "created_at",
            "updated_at",
            "date_joined",
            "last_login",
            "created_by",
            "created_by_name",
            "updated_by",
            "updated_by_name",
            "archived_by",
            "archived_by_name",
        )

    def get_photo_url(self, obj):
        if not obj.photo:
            return None

        request = self.context.get("request")

        if request:
            return request.build_absolute_uri(obj.photo.url)

        return obj.photo.url


class UserCreateSerializer(serializers.ModelSerializer):
    """
    Creación manual o mediante datos obtenidos por DNI.
    """

    password = serializers.CharField(
        write_only=True,
        required=True,
        trim_whitespace=False,
        validators=[validate_password],
        style={
            "input_type": "password",
        },
    )

    password_confirmation = serializers.CharField(
        write_only=True,
        required=True,
        trim_whitespace=False,
        style={
            "input_type": "password",
        },
    )

    class Meta:
        model = User

        fields = (
            "dni",
            "email",
            "password",
            "password_confirmation",
            "first_name",
            "paternal_last_name",
            "maternal_last_name",
            "photo",
            "personal_phone",
            "work_phone",
            "work_extension",
            "job_title",
            "department_name",
            "company_name",
            "address",
            "ubigeo",
            "district",
            "province",
            "region",
            "registration_source",
            "is_active",
            "is_staff",
            "is_verified",
            "must_change_password",
        )

    def validate_email(self, value):
        email = value.strip().lower()

        if User.objects.filter(email__iexact=email).exists():
            raise serializers.ValidationError(
                "Ya existe un usuario con este correo."
            )

        return email

    def validate_dni(self, value):
        if not value:
            return None

        dni = value.strip()

        if User.objects.filter(dni=dni).exists():
            raise serializers.ValidationError(
                "Ya existe un usuario con este DNI."
            )

        return dni

    def validate(self, attrs):
        password = attrs.get("password")
        confirmation = attrs.pop(
            "password_confirmation",
            None,
        )

        if password != confirmation:
            raise serializers.ValidationError(
                {
                    "password_confirmation": (
                        "Las contraseñas no coinciden."
                    )
                }
            )

        return attrs

    @transaction.atomic
    def create(self, validated_data):
        password = validated_data.pop("password")

        request = self.context.get("request")
        actor = None

        if request and request.user.is_authenticated:
            actor = request.user

        email = validated_data["email"]

        username_base = (
            validated_data.get("dni")
            or email.split("@")[0]
        )

        username = self._generate_unique_username(
            username_base
        )

        user = User(
            username=username,
            created_by=actor,
            updated_by=actor,
            **validated_data,
        )

        user.set_new_password(
            password,
            force_change=validated_data.get(
                "must_change_password",
                True,
            ),
        )

        user.full_clean()
        user.save()

        return user

    def _generate_unique_username(self, value):
        base = (
            value.strip()
            .lower()
            .replace(" ", "")
        )

        candidate = base
        counter = 1

        while User.objects.filter(
            username=candidate
        ).exists():
            candidate = f"{base}{counter}"
            counter += 1

        return candidate


class UserUpdateSerializer(serializers.ModelSerializer):
    """
    Edición de datos personales, laborales y de acceso.
    """

    class Meta:
        model = User

        fields = (
            "dni",
            "email",
            "first_name",
            "paternal_last_name",
            "maternal_last_name",
            "photo",
            "personal_phone",
            "work_phone",
            "work_extension",
            "job_title",
            "department_name",
            "company_name",
            "address",
            "ubigeo",
            "district",
            "province",
            "region",
            "is_active",
            "is_staff",
            "is_verified",
            "must_change_password",
        )

    def validate_email(self, value):
        email = value.strip().lower()

        queryset = User.objects.filter(
            email__iexact=email
        )

        if self.instance:
            queryset = queryset.exclude(
                pk=self.instance.pk
            )

        if queryset.exists():
            raise serializers.ValidationError(
                "Ya existe un usuario con este correo."
            )

        return email

    def validate_dni(self, value):
        if not value:
            return None

        dni = value.strip()

        queryset = User.objects.filter(dni=dni)

        if self.instance:
            queryset = queryset.exclude(
                pk=self.instance.pk
            )

        if queryset.exists():
            raise serializers.ValidationError(
                "Ya existe un usuario con este DNI."
            )

        return dni

    @transaction.atomic
    def update(self, instance, validated_data):
        request = self.context.get("request")

        if request and request.user.is_authenticated:
            instance.updated_by = request.user

        for field, value in validated_data.items():
            setattr(instance, field, value)

        instance.full_clean()
        instance.save()

        return instance


class ChangePasswordSerializer(serializers.Serializer):
    """
    Cambio de contraseña realizado por el propio usuario.
    """

    current_password = serializers.CharField(
        write_only=True,
        trim_whitespace=False,
    )

    new_password = serializers.CharField(
        write_only=True,
        trim_whitespace=False,
        validators=[validate_password],
    )

    new_password_confirmation = serializers.CharField(
        write_only=True,
        trim_whitespace=False,
    )

    def validate_current_password(self, value):
        user = self.context["request"].user

        if not user.check_password(value):
            raise serializers.ValidationError(
                "La contraseña actual es incorrecta."
            )

        return value

    def validate(self, attrs):
        if (
            attrs["new_password"]
            != attrs["new_password_confirmation"]
        ):
            raise serializers.ValidationError(
                {
                    "new_password_confirmation": (
                        "Las contraseñas no coinciden."
                    )
                }
            )

        return attrs

    def save(self, **kwargs):
        user = self.context["request"].user

        user.set_new_password(
            self.validated_data["new_password"],
            force_change=False,
        )

        user.save(
            update_fields=(
                "password",
                "password_changed_at",
                "must_change_password",
            )
        )

        return user


class AdminResetPasswordSerializer(serializers.Serializer):
    """
    Restablecimiento de contraseña realizado por un administrador.
    """

    new_password = serializers.CharField(
        write_only=True,
        trim_whitespace=False,
        validators=[validate_password],
    )

    new_password_confirmation = serializers.CharField(
        write_only=True,
        trim_whitespace=False,
    )

    force_change = serializers.BooleanField(
        default=True,
    )

    def validate(self, attrs):
        if (
            attrs["new_password"]
            != attrs["new_password_confirmation"]
        ):
            raise serializers.ValidationError(
                {
                    "new_password_confirmation": (
                        "Las contraseñas no coinciden."
                    )
                }
            )

        return attrs

    def save(self, user):
        user.set_new_password(
            self.validated_data["new_password"],
            force_change=self.validated_data[
                "force_change"
            ],
        )

        user.save(
            update_fields=(
                "password",
                "password_changed_at",
                "must_change_password",
            )
        )

        return user


class ArchiveUserSerializer(serializers.Serializer):
    reason = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=500,
    )


class TwoFactorCodeSerializer(serializers.Serializer):
    """
    Valida un código de seis dígitos generado por
    una aplicación autenticadora.
    """

    code = serializers.CharField(
        required=True,
        min_length=6,
        max_length=6,
        trim_whitespace=True,
        write_only=True,
    )

    def validate_code(self, value):
        code = value.replace(" ", "").strip()

        if not code.isdigit():
            raise serializers.ValidationError(
                "El código debe contener únicamente números."
            )

        if len(code) != 6:
            raise serializers.ValidationError(
                "El código debe contener exactamente 6 números."
            )

        return code


class DisableTwoFactorSerializer(serializers.Serializer):
    """
    Confirma la contraseña antes de desactivar el 2FA.
    """

    current_password = serializers.CharField(
        required=True,
        write_only=True,
        trim_whitespace=False,
        style={
            "input_type": "password",
        },
    )

    code = serializers.CharField(
        required=True,
        min_length=6,
        max_length=20,
        write_only=True,
        trim_whitespace=True,
    )

    def validate_current_password(self, value):
        request = self.context.get("request")

        if not request or not request.user.is_authenticated:
            raise serializers.ValidationError(
                "No se pudo identificar al usuario."
            )

        if not request.user.check_password(value):
            raise serializers.ValidationError(
                "La contraseña actual es incorrecta."
            )

        return value

    def validate_code(self, value):
        code = (
            value.replace(" ", "")
            .strip()
            .upper()
        )

        if not code:
            raise serializers.ValidationError(
                "Debes ingresar el código de seguridad."
            )

        return code


class RegenerateRecoveryCodesSerializer(
    serializers.Serializer
):
    """
    Confirma contraseña y código 2FA antes de generar
    nuevos códigos de recuperación.
    """

    current_password = serializers.CharField(
        required=True,
        write_only=True,
        trim_whitespace=False,
        style={
            "input_type": "password",
        },
    )

    code = serializers.CharField(
        required=True,
        min_length=6,
        max_length=20,
        write_only=True,
        trim_whitespace=True,
    )

    def validate_current_password(self, value):
        request = self.context.get("request")

        if not request or not request.user.is_authenticated:
            raise serializers.ValidationError(
                "No se pudo identificar al usuario."
            )

        if not request.user.check_password(value):
            raise serializers.ValidationError(
                "La contraseña actual es incorrecta."
            )

        return value

    def validate_code(self, value):
        code = (
            value.replace(" ", "")
            .strip()
            .upper()
        )

        if not code:
            raise serializers.ValidationError(
                "Debes ingresar el código de seguridad."
            )

        return code


class TwoFactorLoginSerializer(serializers.Serializer):
    """
    Segundo paso del inicio de sesión cuando el usuario
    tiene 2FA activo.
    """

    challenge_token = serializers.CharField(
        required=True,
        write_only=True,
        trim_whitespace=True,
    )

    code = serializers.CharField(
        required=True,
        min_length=6,
        max_length=20,
        write_only=True,
        trim_whitespace=True,
    )

    def validate_challenge_token(self, value):
        token = value.strip()

        if not token:
            raise serializers.ValidationError(
                "El identificador de autenticación es obligatorio."
            )

        return token

    def validate_code(self, value):
        code = (
            value.replace(" ", "")
            .strip()
            .upper()
        )

        if not code:
            raise serializers.ValidationError(
                "Debes ingresar el código de autenticación."
            )

        return code