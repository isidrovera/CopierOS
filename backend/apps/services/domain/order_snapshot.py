# -*- coding: utf-8 -*-
from apps.rentals.models import RentalAssignment
from apps.services.models import ServiceOrder


RENTAL_SERVICE_ASSIGNMENT_STATUSES = (
    RentalAssignment.Status.INSTALLED,
    RentalAssignment.Status.ACTIVE,
    RentalAssignment.Status.REMOVAL_PENDING,
)


def get_current_rental_assignment(equipment):
    """
    Obtiene la asignación vigente válida para una OS
    de alquiler propio.

    No se consideran:
    - Borradores.
    - Reservas.
    - Instalaciones pendientes.
    - Asignaciones retiradas.
    - Asignaciones canceladas.
    """

    if not equipment:
        return None

    return (
        RentalAssignment.objects
        .select_related(
            "contract",
            "rental_equipment",
            "rental_equipment__equipment",
            "customer",
            "branch",
            "contact",
        )
        .filter(
            rental_equipment__equipment=equipment,
            status__in=RENTAL_SERVICE_ASSIGNMENT_STATUSES,
            archived_at__isnull=True,
        )
        .order_by(
            "-installed_at",
            "-assigned_at",
            "-created_at",
        )
        .first()
    )


def _clean(value):
    return str(value or "").strip()


def _get_first_value(
    instance,
    field_names,
):
    if not instance:
        return ""

    for field_name in field_names:
        value = getattr(
            instance,
            field_name,
            None,
        )

        if value not in (
            None,
            "",
        ):
            return value

    return ""


def _get_partner_name(partner):
    if not partner:
        return ""

    return (
        _clean(
            getattr(
                partner,
                "legal_name",
                "",
            )
        )
        or _clean(
            getattr(
                partner,
                "trade_name",
                "",
            )
        )
        or _clean(partner)
    )


def _get_partner_trade_name(partner):
    if not partner:
        return ""

    return _clean(
        getattr(
            partner,
            "trade_name",
            "",
        )
    )


def _get_contact_name(contact):
    if not contact:
        return ""

    first_names = _clean(
        getattr(
            contact,
            "first_names",
            "",
        )
    )

    paternal_last_name = _clean(
        getattr(
            contact,
            "paternal_last_name",
            "",
        )
    )

    maternal_last_name = _clean(
        getattr(
            contact,
            "maternal_last_name",
            "",
        )
    )

    full_name = " ".join(
        value
        for value in (
            first_names,
            paternal_last_name,
            maternal_last_name,
        )
        if value
    )

    return full_name or _clean(contact)


def _get_contact_phone(contact):
    if not contact:
        return ""

    return _clean(
        _get_first_value(
            contact,
            (
                "primary_mobile",
                "work_phone",
                "whatsapp_number",
                "secondary_mobile",
                "phone",
                "mobile",
            ),
        )
    )


def _get_contact_email(contact):
    if not contact:
        return ""

    return _clean(
        _get_first_value(
            contact,
            (
                "primary_email",
                "work_email",
                "email",
            ),
        )
    )


def _get_branch_address(branch):
    if not branch:
        return ""

    return _clean(
        _get_first_value(
            branch,
            (
                "address",
                "street_address",
                "full_address",
            ),
        )
    )


def _get_branch_reference(branch):
    if not branch:
        return ""

    return _clean(
        _get_first_value(
            branch,
            (
                "address_reference",
                "reference",
            ),
        )
    )


def _get_branch_location_value(
    branch,
    field_names,
):
    if not branch:
        return ""

    return _clean(
        _get_first_value(
            branch,
            field_names,
        )
    )


def _get_equipment_customer(equipment):
    """
    Obtiene el cliente actual registrado directamente
    en Equipment para servicios externos.
    """

    if not equipment:
        return None

    return _get_first_value(
        equipment,
        (
            "customer",
            "current_customer",
            "owner_customer",
        ),
    ) or None


def _get_equipment_branch(equipment):
    """
    Obtiene la sede actual registrada directamente
    en Equipment para servicios externos.
    """

    if not equipment:
        return None

    return _get_first_value(
        equipment,
        (
            "customer_branch",
            "branch",
            "current_branch",
        ),
    ) or None


def _get_equipment_contact(equipment):
    """
    Obtiene el contacto actual del equipo externo
    cuando Equipment dispone de esa relación.
    """

    if not equipment:
        return None

    return _get_first_value(
        equipment,
        (
            "customer_contact",
            "contact",
            "current_contact",
        ),
    ) or None


def build_rental_order_snapshot(equipment):
    """
    Construye el snapshot de una OS de Alquiler Andes.

    La información se obtiene únicamente desde una
    RentalAssignment instalada, activa o pendiente de retiro.

    No se conserva ninguna ForeignKey hacia rentals.
    """

    assignment = get_current_rental_assignment(
        equipment
    )

    if not assignment:
        return {}

    customer = assignment.customer
    branch = assignment.branch
    contact = assignment.contact
    contract = assignment.contract

    contract_reference = (
        _clean(
            getattr(
                contract,
                "contract_number",
                "",
            )
        )
        or _clean(
            getattr(
                contract,
                "code",
                "",
            )
        )
    )

    return {
        "customer_code": _clean(
            getattr(
                customer,
                "code",
                "",
            )
        ),
        "customer_document_type": _clean(
            getattr(
                customer,
                "document_type",
                "",
            )
        ),
        "customer_document_number": _clean(
            getattr(
                customer,
                "document_number",
                "",
            )
        ),
        "customer_name": _get_partner_name(
            customer
        ),
        "customer_trade_name": (
            _get_partner_trade_name(
                customer
            )
        ),
        "branch_name": _clean(
            getattr(
                branch,
                "name",
                "",
            )
        ),
        "address": _get_branch_address(
            branch
        ),
        "address_reference": (
            _get_branch_reference(
                branch
            )
        ),
        "district": (
            _get_branch_location_value(
                branch,
                (
                    "district",
                    "district_name",
                ),
            )
        ),
        "province": (
            _get_branch_location_value(
                branch,
                (
                    "province",
                    "province_name",
                ),
            )
        ),
        "region": (
            _get_branch_location_value(
                branch,
                (
                    "region",
                    "department",
                    "department_name",
                ),
            )
        ),
        "destination_latitude": getattr(
            branch,
            "latitude",
            None,
        ),
        "destination_longitude": getattr(
            branch,
            "longitude",
            None,
        ),
        "site_location": _clean(
            getattr(
                assignment,
                "site_location",
                "",
            )
        ),
        "contact_name": (
            _get_contact_name(
                contact
            )
        ),
        "contact_job_title": _clean(
            getattr(
                contact,
                "job_title",
                "",
            )
            if contact
            else ""
        ),
        "contact_phone": (
            _get_contact_phone(
                contact
            )
        ),
        "contact_email": (
            _get_contact_email(
                contact
            )
        ),
        "contract_reference": (
            contract_reference
        ),
        "rental_assignment_reference": (
            _clean(
                getattr(
                    assignment,
                    "code",
                    "",
                )
            )
        ),
    }


def build_external_order_snapshot(equipment):
    """
    Construye el snapshot de una OS de equipo externo.

    Los datos se obtienen desde las relaciones actuales
    registradas en Equipment:

    - customer.
    - customer_branch.
    - customer_contact, cuando exista.

    El equipo externo no necesita RentalEquipment,
    RentalContract ni RentalAssignment.
    """

    if not equipment:
        return {}

    customer = _get_equipment_customer(
        equipment
    )

    branch = _get_equipment_branch(
        equipment
    )

    contact = _get_equipment_contact(
        equipment
    )

    if not customer:
        return {}

    return {
        "customer_code": _clean(
            getattr(
                customer,
                "code",
                "",
            )
        ),
        "customer_document_type": _clean(
            getattr(
                customer,
                "document_type",
                "",
            )
        ),
        "customer_document_number": _clean(
            getattr(
                customer,
                "document_number",
                "",
            )
        ),
        "customer_name": _get_partner_name(
            customer
        ),
        "customer_trade_name": (
            _get_partner_trade_name(
                customer
            )
        ),
        "branch_name": _clean(
            getattr(
                branch,
                "name",
                "",
            )
            if branch
            else ""
        ),
        "address": (
            _get_branch_address(
                branch
            )
        ),
        "address_reference": (
            _get_branch_reference(
                branch
            )
        ),
        "district": (
            _get_branch_location_value(
                branch,
                (
                    "district",
                    "district_name",
                ),
            )
        ),
        "province": (
            _get_branch_location_value(
                branch,
                (
                    "province",
                    "province_name",
                ),
            )
        ),
        "region": (
            _get_branch_location_value(
                branch,
                (
                    "region",
                    "department",
                    "department_name",
                ),
            )
        ),
        "destination_latitude": (
            getattr(
                branch,
                "latitude",
                None,
            )
            if branch
            else None
        ),
        "destination_longitude": (
            getattr(
                branch,
                "longitude",
                None,
            )
            if branch
            else None
        ),
        "site_location": _clean(
            _get_first_value(
                equipment,
                (
                    "site_location",
                    "location",
                    "customer_location",
                ),
            )
        ),
        "contact_name": (
            _get_contact_name(
                contact
            )
        ),
        "contact_job_title": _clean(
            getattr(
                contact,
                "job_title",
                "",
            )
            if contact
            else ""
        ),
        "contact_phone": (
            _get_contact_phone(
                contact
            )
        ),
        "contact_email": (
            _get_contact_email(
                contact
            )
        ),
        "contract_reference": "",
        "rental_assignment_reference": "",
    }


def build_order_snapshot(
    equipment,
    service_origin,
):
    """
    Selecciona la fuente correcta del snapshot.

    Alquiler Andes:
    - RentalAssignment vigente.

    Equipo externo:
    - Relaciones actuales registradas en Equipment.
    """

    if (
        service_origin
        == ServiceOrder.ServiceOrigin.RENTAL
    ):
        return build_rental_order_snapshot(
            equipment
        )

    if (
        service_origin
        == ServiceOrder.ServiceOrigin.EXTERNAL
    ):
        return build_external_order_snapshot(
            equipment
        )

    return {}