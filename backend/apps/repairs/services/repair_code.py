# -*- coding: utf-8 -*-
from django.db import transaction
from django.utils import timezone

from ..models import Repair


def build_repair_code(
    year,
    sequence,
):
    return (
        f"REP-{year}-"
        f"{sequence:06d}"
    )


@transaction.atomic
def generate_repair_code():
    current_year = timezone.localdate().year
    code_prefix = f"REP-{current_year}-"

    last_repair = (
        Repair.objects.select_for_update()
        .filter(
            code__startswith=code_prefix,
        )
        .order_by("-code")
        .first()
    )

    next_sequence = 1

    if last_repair:
        try:
            last_sequence = int(
                last_repair.code.rsplit(
                    "-",
                    1,
                )[-1]
            )

            next_sequence = (
                last_sequence + 1
            )
        except (
            TypeError,
            ValueError,
            IndexError,
        ):
            next_sequence = (
                Repair.objects.filter(
                    code__startswith=code_prefix,
                ).count()
                + 1
            )

    code = build_repair_code(
        current_year,
        next_sequence,
    )

    while Repair.objects.filter(
        code__iexact=code,
    ).exists():
        next_sequence += 1

        code = build_repair_code(
            current_year,
            next_sequence,
        )

    return code