# -*- coding: utf-8 -*-
from django.contrib.auth import authenticate
from django.contrib.auth.models import update_last_login
from django.core import signing
from django.core.signing import BadSignature, SignatureExpired
from django.db import transaction

from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.generics import (
    ListCreateAPIView,
    RetrieveUpdateAPIView,
)
from rest_framework.parsers import (
    FormParser,
    JSONParser,
    MultiPartParser,
)
from rest_framework.permissions import (
    IsAdminUser,
    IsAuthenticated,
)
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import User, UserAuditLog
from .serializers import (
    AdminResetPasswordSerializer,
    ArchiveUserSerializer,
    ChangePasswordSerializer,
    DisableTwoFactorSerializer,
    RegenerateRecoveryCodesSerializer,
    TwoFactorCodeSerializer,
    TwoFactorLoginSerializer,
    UserCreateSerializer,
    UserDetailSerializer,
    UserListSerializer,
    UserUpdateSerializer,
)
from .services.two_factor import (
    TwoFactorConfigurationError,
    TwoFactorValidationError,
    begin_totp_setup,
    confirm_totp_setup,
    disable_two_factor,
    generate_recovery_codes,
    get_two_factor_status,
    verify_recovery_code,
    verify_user_totp,
)


TWO_FACTOR_CHALLENGE_SALT = "users.two-factor-login"
TWO_FACTOR_CHALLENGE_MAX_AGE = 300


def get_client_ip(request):
    """
    Obtiene la dirección IP del cliente.
    """

    forwarded_for = request.META.get(
        "HTTP_X_FORWARDED_FOR",
    )

    if forwarded_for:
        return forwarded_for.split(",")[0].strip()

    return request.META.get("REMOTE_ADDR")


def register_audit(
    request,
    action,
    target_user=None,
    description="",
    status_value=UserAuditLog.STATUS_SUCCESS,
    changed_fields=None,
    error_message="",
):
    """
    Registra una acción realizada sobre un usuario.
    """

    actor = None

    if request.user and request.user.is_authenticated:
        actor = request.user

    UserAuditLog.objects.create(
        actor=actor,
        target_user=target_user,
        action=action,
        status=status_value,
        description=description,
        changed_fields=changed_fields or {},
        error_message=error_message,
        ip_address=get_client_ip(request),
        user_agent=request.META.get(
            "HTTP_USER_AGENT",
            "",
        ),
        request_method=request.method,
        request_path=request.path,
    )


def build_login_user_data(request, user):
    """
    Construye la información básica del usuario autenticado.
    """

    return {
        "id": str(user.id),
        "dni": user.dni,
        "email": user.email,
        "username": user.username,
        "first_name": user.first_name,
        "paternal_last_name": user.paternal_last_name,
        "maternal_last_name": user.maternal_last_name,
        "full_name": user.full_name,
        "photo": (
            request.build_absolute_uri(user.photo.url)
            if user.photo
            else None
        ),
        "job_title": user.job_title,
        "department_name": user.department_name,
        "is_staff": user.is_staff,
        "is_superuser": user.is_superuser,
        "must_change_password": user.must_change_password,
    }


class LoginView(APIView):
    """
    Primer paso del inicio de sesión.

    Si el usuario tiene 2FA activo, devuelve un challenge temporal
    en lugar del token definitivo.
    """

    authentication_classes = []
    permission_classes = []

    def post(self, request):
        email = str(
            request.data.get("email", "")
        ).strip().lower()

        password = request.data.get("password")

        if not email or not password:
            return Response(
                {
                    "detail": (
                        "Correo y contraseña son obligatorios."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        user_record = User.objects.filter(
            email__iexact=email
        ).first()

        if user_record and user_record.is_archived:
            register_audit(
                request=request,
                action=UserAuditLog.ACTION_LOGIN_FAILED,
                target_user=user_record,
                description=(
                    "Intento de acceso de usuario archivado."
                ),
                status_value=UserAuditLog.STATUS_FAILED,
            )

            return Response(
                {
                    "detail": (
                        "Este usuario se encuentra archivado."
                    )
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        if user_record and user_record.is_locked:
            register_audit(
                request=request,
                action=UserAuditLog.ACTION_LOGIN_FAILED,
                target_user=user_record,
                description=(
                    "Intento de acceso de usuario bloqueado."
                ),
                status_value=UserAuditLog.STATUS_FAILED,
            )

            return Response(
                {
                    "detail": (
                        "El usuario está bloqueado temporalmente."
                    )
                },
                status=status.HTTP_423_LOCKED,
            )

        user = authenticate(
            request=request,
            username=email,
            password=password,
        )

        if user is None:
            if user_record:
                user_record.register_failed_login()
                user_record.save(
                    update_fields=[
                        "failed_login_attempts",
                    ]
                )

            register_audit(
                request=request,
                action=UserAuditLog.ACTION_LOGIN_FAILED,
                target_user=user_record,
                description="Credenciales incorrectas.",
                status_value=UserAuditLog.STATUS_FAILED,
            )

            return Response(
                {
                    "detail": "Credenciales incorrectas."
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if not user.is_active:
            return Response(
                {
                    "detail": (
                        "Este usuario se encuentra desactivado."
                    )
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        user.reset_failed_login()

        user.save(
            update_fields=[
                "failed_login_attempts",
                "locked_until",
            ]
        )

        security = getattr(
            user,
            "security_settings",
            None,
        )

        if (
            security
            and security.two_factor_enabled
            and security.require_two_factor_for_login
        ):
            challenge_token = signing.dumps(
                {
                    "user_id": str(user.id),
                },
                salt=TWO_FACTOR_CHALLENGE_SALT,
                compress=True,
            )

            return Response(
                {
                    "requires_two_factor": True,
                    "two_factor_method": (
                        security.two_factor_method
                    ),
                    "challenge_token": challenge_token,
                    "detail": (
                        "Ingresa el código de tu aplicación "
                        "autenticadora."
                    ),
                },
                status=status.HTTP_200_OK,
            )

        token, _ = Token.objects.get_or_create(
            user=user
        )

        update_last_login(
            None,
            user,
        )

        register_audit(
            request=request,
            action=UserAuditLog.ACTION_LOGIN,
            target_user=user,
            description="Inicio de sesión exitoso.",
        )

        return Response(
            {
                "requires_two_factor": False,
                "token": token.key,
                "user": build_login_user_data(
                    request,
                    user,
                ),
            },
            status=status.HTTP_200_OK,
        )


class LogoutView(APIView):
    """
    Cierra la sesión eliminando el token actual.
    """

    permission_classes = [
        IsAuthenticated,
    ]

    def post(self, request):
        register_audit(
            request=request,
            action=UserAuditLog.ACTION_LOGOUT,
            target_user=request.user,
            description="Cierre de sesión.",
        )

        Token.objects.filter(
            user=request.user
        ).delete()

        return Response(
            {
                "detail": (
                    "Sesión cerrada correctamente."
                )
            },
            status=status.HTTP_200_OK,
        )


class CurrentUserView(APIView):
    """
    Devuelve los datos del usuario autenticado.
    """

    permission_classes = [
        IsAuthenticated,
    ]

    def get(self, request):
        serializer = UserDetailSerializer(
            request.user,
            context={
                "request": request,
            },
        )

        return Response(
            serializer.data
        )


class UserListCreateView(ListCreateAPIView):
    """
    Lista y crea usuarios.

    GET:
        Lista usuarios.

    POST:
        Crea un nuevo usuario.
    """

    permission_classes = [
        IsAdminUser,
    ]

    parser_classes = [
        JSONParser,
        MultiPartParser,
        FormParser,
    ]

    def get_queryset(self):
        queryset = User.objects.all().order_by(
            "first_name",
            "paternal_last_name",
            "maternal_last_name",
            "email",
        )

        include_archived = (
            self.request.query_params.get(
                "include_archived",
                "",
            ).lower()
            in (
                "1",
                "true",
                "yes",
            )
        )

        if not include_archived:
            queryset = queryset.filter(
                archived_at__isnull=True
            )

        search = self.request.query_params.get(
            "search",
            "",
        ).strip()

        if search:
            from django.db.models import Q

            queryset = queryset.filter(
                Q(
                    email__icontains=search
                )
                | Q(
                    dni__icontains=search
                )
                | Q(
                    first_name__icontains=search
                )
                | Q(
                    paternal_last_name__icontains=search
                )
                | Q(
                    maternal_last_name__icontains=search
                )
                | Q(
                    job_title__icontains=search
                )
                | Q(
                    department_name__icontains=search
                )
            )

        is_active = (
            self.request.query_params.get(
                "is_active"
            )
        )

        if is_active in (
            "true",
            "false",
        ):
            queryset = queryset.filter(
                is_active=(
                    is_active == "true"
                )
            )

        return queryset

    def get_serializer_class(self):
        if self.request.method == "POST":
            return UserCreateSerializer

        return UserListSerializer

    @transaction.atomic
    def perform_create(self, serializer):
        user = serializer.save()

        register_audit(
            request=self.request,
            action=UserAuditLog.ACTION_CREATE,
            target_user=user,
            description="Usuario creado.",
        )


class UserDetailUpdateView(
    RetrieveUpdateAPIView
):
    """
    Consulta y edita un usuario.

    GET:
        Devuelve el detalle.

    PUT/PATCH:
        Actualiza sus datos.
    """

    queryset = User.objects.all()

    permission_classes = [
        IsAdminUser,
    ]

    lookup_field = "id"

    parser_classes = [
        JSONParser,
        MultiPartParser,
        FormParser,
    ]

    def get_serializer_class(self):
        if self.request.method in (
            "PUT",
            "PATCH",
        ):
            return UserUpdateSerializer

        return UserDetailSerializer

    @transaction.atomic
    def perform_update(self, serializer):
        before = {
            field: getattr(
                serializer.instance,
                field,
                None,
            )
            for field in (
                serializer.validated_data.keys()
            )
        }

        user = serializer.save()

        changed_fields = {}

        for field, previous_value in before.items():
            current_value = getattr(
                user,
                field,
                None,
            )

            if previous_value != current_value:
                changed_fields[field] = {
                    "before": str(
                        previous_value
                    ),
                    "after": str(
                        current_value
                    ),
                }

        register_audit(
            request=self.request,
            action=UserAuditLog.ACTION_UPDATE,
            target_user=user,
            description=(
                "Datos del usuario modificados."
            ),
            changed_fields=changed_fields,
        )


class ArchiveUserView(APIView):
    """
    Archiva un usuario sin eliminar su historial.
    """

    permission_classes = [
        IsAdminUser,
    ]

    @transaction.atomic
    def post(
        self,
        request,
        user_id,
    ):
        user = User.objects.filter(
            id=user_id
        ).first()

        if not user:
            return Response(
                {
                    "detail": (
                        "Usuario no encontrado."
                    )
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        if user == request.user:
            return Response(
                {
                    "detail": (
                        "No puedes archivar tu "
                        "propio usuario."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if user.is_archived:
            return Response(
                {
                    "detail": (
                        "El usuario ya se encuentra "
                        "archivado."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = ArchiveUserSerializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        reason = serializer.validated_data.get(
            "reason",
            "",
        )

        user.archive(
            user=request.user,
            reason=reason,
        )

        user.updated_by = request.user

        user.save(
            update_fields=[
                "is_active",
                "archived_at",
                "archived_by",
                "archived_reason",
                "updated_by",
                "updated_at",
            ]
        )

        Token.objects.filter(
            user=user
        ).delete()

        register_audit(
            request=request,
            action=UserAuditLog.ACTION_ARCHIVE,
            target_user=user,
            description=(
                reason
                or "Usuario archivado."
            ),
        )

        return Response(
            {
                "detail": (
                    "Usuario archivado "
                    "correctamente."
                )
            }
        )


class RestoreUserView(APIView):
    """
    Restaura un usuario archivado.
    """

    permission_classes = [
        IsAdminUser,
    ]

    @transaction.atomic
    def post(
        self,
        request,
        user_id,
    ):
        user = User.objects.filter(
            id=user_id
        ).first()

        if not user:
            return Response(
                {
                    "detail": (
                        "Usuario no encontrado."
                    )
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        if not user.is_archived:
            return Response(
                {
                    "detail": (
                        "El usuario no está "
                        "archivado."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.restore(
            user=request.user
        )

        user.save(
            update_fields=[
                "is_active",
                "archived_at",
                "archived_by",
                "archived_reason",
                "updated_by",
                "updated_at",
            ]
        )

        register_audit(
            request=request,
            action=UserAuditLog.ACTION_RESTORE,
            target_user=user,
            description="Usuario restaurado.",
        )

        return Response(
            {
                "detail": (
                    "Usuario restaurado "
                    "correctamente."
                )
            }
        )


class ChangePasswordView(APIView):
    """
    Permite al usuario cambiar su propia contraseña.
    """

    permission_classes = [
        IsAuthenticated,
    ]

    @transaction.atomic
    def post(self, request):
        serializer = ChangePasswordSerializer(
            data=request.data,
            context={
                "request": request,
            },
        )

        serializer.is_valid(
            raise_exception=True
        )

        user = serializer.save()

        Token.objects.filter(
            user=user
        ).delete()

        new_token = Token.objects.create(
            user=user
        )

        register_audit(
            request=request,
            action=(
                UserAuditLog.ACTION_PASSWORD_CHANGE
            ),
            target_user=user,
            description="Contraseña modificada.",
        )

        return Response(
            {
                "detail": (
                    "Contraseña cambiada "
                    "correctamente."
                ),
                "token": new_token.key,
            }
        )


class AdminResetPasswordView(APIView):
    """
    Permite que un administrador restablezca la contraseña.
    """

    permission_classes = [
        IsAdminUser,
    ]

    @transaction.atomic
    def post(
        self,
        request,
        user_id,
    ):
        user = User.objects.filter(
            id=user_id
        ).first()

        if not user:
            return Response(
                {
                    "detail": (
                        "Usuario no encontrado."
                    )
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = AdminResetPasswordSerializer(
            data=request.data,
        )

        serializer.is_valid(
            raise_exception=True
        )

        serializer.save(
            user=user
        )

        user.updated_by = request.user

        user.save(
            update_fields=[
                "updated_by",
                "updated_at",
            ]
        )

        Token.objects.filter(
            user=user
        ).delete()

        register_audit(
            request=request,
            action=(
                UserAuditLog.ACTION_PASSWORD_RESET
            ),
            target_user=user,
            description=(
                "Contraseña restablecida "
                "por administrador."
            ),
        )

        return Response(
            {
                "detail": (
                    "Contraseña restablecida "
                    "correctamente."
                )
            }
        )


class TwoFactorStatusView(APIView):
    permission_classes = [
        IsAuthenticated,
    ]

    def get(self, request):
        return Response(
            get_two_factor_status(
                request.user
            )
        )


class BeginTotpSetupView(APIView):
    permission_classes = [
        IsAuthenticated,
    ]

    def post(self, request):
        current_status = get_two_factor_status(
            request.user
        )

        if current_status[
            "two_factor_enabled"
        ]:
            return Response(
                {
                    "detail": (
                        "El doble factor ya está activo. "
                        "Desactívalo antes de configurarlo "
                        "nuevamente."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            setup = begin_totp_setup(
                request.user
            )
        except TwoFactorConfigurationError as exc:
            return Response(
                {
                    "detail": str(exc)
                },
                status=(
                    status.HTTP_500_INTERNAL_SERVER_ERROR
                ),
            )

        return Response(
            setup,
            status=status.HTTP_200_OK,
        )


class ConfirmTotpSetupView(APIView):
    permission_classes = [
        IsAuthenticated,
    ]

    def post(self, request):
        serializer = TwoFactorCodeSerializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        try:
            result = confirm_totp_setup(
                request.user,
                serializer.validated_data[
                    "code"
                ],
            )
        except (
            TwoFactorValidationError,
            TwoFactorConfigurationError,
        ) as exc:
            return Response(
                {
                    "detail": str(exc)
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {
                "detail": (
                    "Autenticación en dos "
                    "factores activada."
                ),
                "recovery_codes": (
                    result["recovery_codes"]
                ),
            },
            status=status.HTTP_200_OK,
        )


class DisableTwoFactorView(APIView):
    permission_classes = [
        IsAuthenticated,
    ]

    def post(self, request):
        serializer = DisableTwoFactorSerializer(
            data=request.data,
            context={
                "request": request,
            },
        )

        serializer.is_valid(
            raise_exception=True
        )

        code = serializer.validated_data[
            "code"
        ]

        try:
            valid = (
                verify_user_totp(
                    request.user,
                    code,
                )
                if (
                    code.isdigit()
                    and len(code) == 6
                )
                else verify_recovery_code(
                    request.user,
                    code,
                )
            )
        except (
            TwoFactorValidationError,
            TwoFactorConfigurationError,
        ) as exc:
            return Response(
                {
                    "detail": str(exc)
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not valid:
            return Response(
                {
                    "detail": (
                        "El código de seguridad "
                        "es incorrecto."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        disable_two_factor(
            request.user
        )

        return Response(
            {
                "detail": (
                    "Autenticación en dos "
                    "factores desactivada."
                )
            }
        )


class RegenerateRecoveryCodesView(APIView):
    permission_classes = [
        IsAuthenticated,
    ]

    def post(self, request):
        serializer = (
            RegenerateRecoveryCodesSerializer(
                data=request.data,
                context={
                    "request": request,
                },
            )
        )

        serializer.is_valid(
            raise_exception=True
        )

        code = serializer.validated_data[
            "code"
        ]

        try:
            valid = (
                verify_user_totp(
                    request.user,
                    code,
                )
                if (
                    code.isdigit()
                    and len(code) == 6
                )
                else verify_recovery_code(
                    request.user,
                    code,
                )
            )
        except (
            TwoFactorValidationError,
            TwoFactorConfigurationError,
        ) as exc:
            return Response(
                {
                    "detail": str(exc)
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not valid:
            return Response(
                {
                    "detail": (
                        "El código de seguridad "
                        "es incorrecto."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        codes = generate_recovery_codes(
            request.user
        )

        return Response(
            {
                "detail": (
                    "Códigos de recuperación "
                    "regenerados."
                ),
                "recovery_codes": codes,
            }
        )


class TwoFactorLoginView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        serializer = TwoFactorLoginSerializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        try:
            payload = signing.loads(
                serializer.validated_data[
                    "challenge_token"
                ],
                salt=TWO_FACTOR_CHALLENGE_SALT,
                max_age=(
                    TWO_FACTOR_CHALLENGE_MAX_AGE
                ),
            )
        except SignatureExpired:
            return Response(
                {
                    "detail": (
                        "La solicitud de autenticación "
                        "venció. Inicia sesión nuevamente."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        except BadSignature:
            return Response(
                {
                    "detail": (
                        "La solicitud de autenticación "
                        "no es válida."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = User.objects.filter(
            id=payload.get(
                "user_id"
            ),
            is_active=True,
            archived_at__isnull=True,
        ).first()

        if not user:
            return Response(
                {
                    "detail": (
                        "Usuario no disponible."
                    )
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )

        code = serializer.validated_data[
            "code"
        ]

        try:
            valid = (
                verify_user_totp(
                    user,
                    code,
                )
                if (
                    code.isdigit()
                    and len(code) == 6
                )
                else verify_recovery_code(
                    user,
                    code,
                )
            )
        except (
            TwoFactorValidationError,
            TwoFactorConfigurationError,
        ) as exc:
            return Response(
                {
                    "detail": str(exc)
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not valid:
            register_audit(
                request=request,
                action=(
                    UserAuditLog.ACTION_LOGIN_FAILED
                ),
                target_user=user,
                description=(
                    "Código 2FA incorrecto."
                ),
                status_value=(
                    UserAuditLog.STATUS_FAILED
                ),
            )

            return Response(
                {
                    "detail": (
                        "El código de autenticación "
                        "es incorrecto."
                    )
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )

        token, _ = Token.objects.get_or_create(
            user=user
        )

        update_last_login(
            None,
            user,
        )

        register_audit(
            request=request,
            action=UserAuditLog.ACTION_LOGIN,
            target_user=user,
            description=(
                "Inicio de sesión con 2FA exitoso."
            ),
        )

        return Response(
            {
                "token": token.key,
                "user": build_login_user_data(
                    request,
                    user,
                ),
            },
            status=status.HTTP_200_OK,
        )