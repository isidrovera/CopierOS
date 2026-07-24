# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from django.db import transaction

from apps.equipment.models import (
    ComponentType,
    EquipmentComponent,
)


class Command(BaseCommand):
    help = (
        "Crea el catálogo inicial de unidades técnicas, "
        "subpartes, accesorios, tóners y repuestos."
    )

    @transaction.atomic
    def handle(self, *args, **options):
        component_types = {
            component_type.code: component_type
            for component_type in ComponentType.objects.filter(
                archived_at__isnull=True,
            )
        }

        required_types = {
            "TECHNICAL_UNIT",
            "COLORED_TECHNICAL_UNIT",
            "SUBPART",
            "COLORED_SUBPART",
            "ACCESSORY",
            "TONER",
            "SPARE_PART",
        }

        missing_types = sorted(
            required_types.difference(
                component_types.keys()
            )
        )

        if missing_types:
            self.stderr.write(
                self.style.ERROR(
                    (
                        "Faltan tipos de componentes: "
                        f"{', '.join(missing_types)}. "
                        "Ejecuta primero seed_equipment_catalogs."
                    )
                )
            )
            return

        components = [
            {
                "code": "IMAGE_UNIT",
                "component_type": "TECHNICAL_UNIT",
                "name": "Unidad de imagen",
                "condition_control": "date_and_meter",
                "expected_life_meter": 300000,
                "expected_life_days": 1095,
                "requires_individual_serial": True,
                "is_consumable": False,
                "is_reusable": True,
                "can_be_repaired": True,
                "requires_removed_part_tracking": True,
                "unit_of_measure": "unit",
                "display_order": 10,
                "description": (
                    "Unidad principal encargada de formar "
                    "la imagen antes de transferirla al papel."
                ),
            },
            {
                "code": "IMAGE_UNIT_BLACK",
                "component_type": "COLORED_TECHNICAL_UNIT",
                "name": "Unidad de imagen",
                "color": "black",
                "condition_control": "date_and_meter",
                "expected_life_meter": 300000,
                "expected_life_days": 1095,
                "requires_individual_serial": True,
                "is_consumable": False,
                "is_reusable": True,
                "can_be_repaired": True,
                "requires_removed_part_tracking": True,
                "unit_of_measure": "unit",
                "display_order": 20,
            },
            {
                "code": "IMAGE_UNIT_CYAN",
                "component_type": "COLORED_TECHNICAL_UNIT",
                "name": "Unidad de imagen",
                "color": "cyan",
                "condition_control": "date_and_meter",
                "expected_life_meter": 250000,
                "expected_life_days": 1095,
                "requires_individual_serial": True,
                "is_consumable": False,
                "is_reusable": True,
                "can_be_repaired": True,
                "requires_removed_part_tracking": True,
                "unit_of_measure": "unit",
                "display_order": 21,
            },
            {
                "code": "IMAGE_UNIT_MAGENTA",
                "component_type": "COLORED_TECHNICAL_UNIT",
                "name": "Unidad de imagen",
                "color": "magenta",
                "condition_control": "date_and_meter",
                "expected_life_meter": 250000,
                "expected_life_days": 1095,
                "requires_individual_serial": True,
                "is_consumable": False,
                "is_reusable": True,
                "can_be_repaired": True,
                "requires_removed_part_tracking": True,
                "unit_of_measure": "unit",
                "display_order": 22,
            },
            {
                "code": "IMAGE_UNIT_YELLOW",
                "component_type": "COLORED_TECHNICAL_UNIT",
                "name": "Unidad de imagen",
                "color": "yellow",
                "condition_control": "date_and_meter",
                "expected_life_meter": 250000,
                "expected_life_days": 1095,
                "requires_individual_serial": True,
                "is_consumable": False,
                "is_reusable": True,
                "can_be_repaired": True,
                "requires_removed_part_tracking": True,
                "unit_of_measure": "unit",
                "display_order": 23,
            },
            {
                "code": "DEVELOPER_UNIT",
                "component_type": "TECHNICAL_UNIT",
                "name": "Unidad de revelado",
                "condition_control": "date_and_meter",
                "expected_life_meter": 300000,
                "expected_life_days": 1095,
                "requires_individual_serial": True,
                "is_consumable": False,
                "is_reusable": True,
                "can_be_repaired": True,
                "requires_removed_part_tracking": True,
                "unit_of_measure": "unit",
                "display_order": 30,
            },
            {
                "code": "DEVELOPER_UNIT_BLACK",
                "component_type": "COLORED_TECHNICAL_UNIT",
                "name": "Unidad de revelado",
                "color": "black",
                "condition_control": "date_and_meter",
                "expected_life_meter": 300000,
                "expected_life_days": 1095,
                "requires_individual_serial": True,
                "is_consumable": False,
                "is_reusable": True,
                "can_be_repaired": True,
                "requires_removed_part_tracking": True,
                "unit_of_measure": "unit",
                "display_order": 31,
            },
            {
                "code": "DEVELOPER_UNIT_CYAN",
                "component_type": "COLORED_TECHNICAL_UNIT",
                "name": "Unidad de revelado",
                "color": "cyan",
                "condition_control": "date_and_meter",
                "expected_life_meter": 250000,
                "expected_life_days": 1095,
                "requires_individual_serial": True,
                "is_consumable": False,
                "is_reusable": True,
                "can_be_repaired": True,
                "requires_removed_part_tracking": True,
                "unit_of_measure": "unit",
                "display_order": 32,
            },
            {
                "code": "DEVELOPER_UNIT_MAGENTA",
                "component_type": "COLORED_TECHNICAL_UNIT",
                "name": "Unidad de revelado",
                "color": "magenta",
                "condition_control": "date_and_meter",
                "expected_life_meter": 250000,
                "expected_life_days": 1095,
                "requires_individual_serial": True,
                "is_consumable": False,
                "is_reusable": True,
                "can_be_repaired": True,
                "requires_removed_part_tracking": True,
                "unit_of_measure": "unit",
                "display_order": 33,
            },
            {
                "code": "DEVELOPER_UNIT_YELLOW",
                "component_type": "COLORED_TECHNICAL_UNIT",
                "name": "Unidad de revelado",
                "color": "yellow",
                "condition_control": "date_and_meter",
                "expected_life_meter": 250000,
                "expected_life_days": 1095,
                "requires_individual_serial": True,
                "is_consumable": False,
                "is_reusable": True,
                "can_be_repaired": True,
                "requires_removed_part_tracking": True,
                "unit_of_measure": "unit",
                "display_order": 34,
            },
            {
                "code": "FUSER_UNIT",
                "component_type": "TECHNICAL_UNIT",
                "name": "Unidad de fusor",
                "condition_control": "date_and_meter",
                "expected_life_meter": 300000,
                "expected_life_days": 1095,
                "requires_individual_serial": True,
                "is_consumable": False,
                "is_reusable": True,
                "can_be_repaired": True,
                "requires_removed_part_tracking": True,
                "unit_of_measure": "unit",
                "display_order": 40,
                "description": (
                    "Unidad encargada de fijar el tóner "
                    "sobre el papel mediante calor y presión."
                ),
            },
            {
                "code": "TRANSFER_UNIT",
                "component_type": "TECHNICAL_UNIT",
                "name": "Unidad de transferencia",
                "condition_control": "date_and_meter",
                "expected_life_meter": 300000,
                "expected_life_days": 1095,
                "requires_individual_serial": True,
                "is_consumable": False,
                "is_reusable": True,
                "can_be_repaired": True,
                "requires_removed_part_tracking": True,
                "unit_of_measure": "unit",
                "display_order": 50,
            },
            {
                "code": "DUPLEX_UNIT",
                "component_type": "TECHNICAL_UNIT",
                "name": "Unidad dúplex",
                "condition_control": "none",
                "requires_individual_serial": True,
                "is_consumable": False,
                "is_reusable": True,
                "can_be_repaired": True,
                "requires_removed_part_tracking": True,
                "unit_of_measure": "unit",
                "display_order": 60,
            },
            {
                "code": "PAPER_FEED_UNIT",
                "component_type": "TECHNICAL_UNIT",
                "name": "Unidad de alimentación de papel",
                "condition_control": "meter",
                "expected_life_meter": 500000,
                "requires_individual_serial": True,
                "is_consumable": False,
                "is_reusable": True,
                "can_be_repaired": True,
                "requires_removed_part_tracking": True,
                "unit_of_measure": "unit",
                "display_order": 70,
            },
            {
                "code": "ADF_UNIT",
                "component_type": "TECHNICAL_UNIT",
                "name": "Unidad alimentadora de documentos",
                "condition_control": "meter",
                "expected_life_meter": 500000,
                "requires_individual_serial": True,
                "is_consumable": False,
                "is_reusable": True,
                "can_be_repaired": True,
                "requires_removed_part_tracking": True,
                "unit_of_measure": "unit",
                "display_order": 80,
            },
            {
                "code": "DRUM",
                "component_type": "SUBPART",
                "parent_component": "IMAGE_UNIT",
                "name": "Cilindro fotoconductor",
                "condition_control": "meter",
                "expected_life_meter": 150000,
                "is_consumable": True,
                "is_reusable": False,
                "can_be_repaired": False,
                "requires_removed_part_tracking": True,
                "unit_of_measure": "unit",
                "display_order": 100,
            },
            {
                "code": "CLEANING_BLADE",
                "component_type": "SUBPART",
                "parent_component": "IMAGE_UNIT",
                "name": "Cuchilla de limpieza",
                "condition_control": "meter",
                "expected_life_meter": 150000,
                "is_consumable": True,
                "is_reusable": False,
                "can_be_repaired": False,
                "requires_removed_part_tracking": True,
                "unit_of_measure": "unit",
                "display_order": 110,
            },
            {
                "code": "CHARGE_ROLLER",
                "component_type": "SUBPART",
                "parent_component": "IMAGE_UNIT",
                "name": "Rodillo de carga",
                "condition_control": "meter",
                "expected_life_meter": 150000,
                "is_consumable": True,
                "is_reusable": False,
                "can_be_repaired": False,
                "requires_removed_part_tracking": True,
                "unit_of_measure": "unit",
                "display_order": 120,
            },
            {
                "code": "DEVELOPER",
                "component_type": "SUBPART",
                "parent_component": "DEVELOPER_UNIT",
                "name": "Developer",
                "condition_control": "meter",
                "expected_life_meter": 200000,
                "is_consumable": True,
                "is_reusable": False,
                "can_be_repaired": False,
                "requires_removed_part_tracking": True,
                "unit_of_measure": "bottle",
                "display_order": 130,
            },
            {
                "code": "MAGNETIC_ROLLER",
                "component_type": "SUBPART",
                "parent_component": "DEVELOPER_UNIT",
                "name": "Rodillo magnético",
                "condition_control": "meter",
                "expected_life_meter": 300000,
                "is_consumable": False,
                "is_reusable": True,
                "can_be_repaired": False,
                "requires_removed_part_tracking": True,
                "unit_of_measure": "unit",
                "display_order": 140,
            },
            {
                "code": "HEATING_ROLLER",
                "component_type": "SUBPART",
                "parent_component": "FUSER_UNIT",
                "name": "Rodillo de calor",
                "condition_control": "meter",
                "expected_life_meter": 200000,
                "is_consumable": True,
                "is_reusable": False,
                "can_be_repaired": False,
                "requires_removed_part_tracking": True,
                "unit_of_measure": "unit",
                "display_order": 150,
            },
            {
                "code": "PRESSURE_ROLLER",
                "component_type": "SUBPART",
                "parent_component": "FUSER_UNIT",
                "name": "Rodillo de presión",
                "condition_control": "meter",
                "expected_life_meter": 200000,
                "is_consumable": True,
                "is_reusable": False,
                "can_be_repaired": False,
                "requires_removed_part_tracking": True,
                "unit_of_measure": "unit",
                "display_order": 160,
            },
            {
                "code": "FUSER_FILM",
                "component_type": "SUBPART",
                "parent_component": "FUSER_UNIT",
                "name": "Película de fusor",
                "condition_control": "meter",
                "expected_life_meter": 150000,
                "is_consumable": True,
                "is_reusable": False,
                "can_be_repaired": False,
                "requires_removed_part_tracking": True,
                "unit_of_measure": "unit",
                "display_order": 170,
            },
            {
                "code": "FUSER_HEATING_ELEMENT",
                "component_type": "SUBPART",
                "parent_component": "FUSER_UNIT",
                "name": "Elemento calefactor",
                "condition_control": "meter",
                "expected_life_meter": 250000,
                "is_consumable": False,
                "is_reusable": True,
                "can_be_repaired": False,
                "requires_removed_part_tracking": True,
                "unit_of_measure": "unit",
                "display_order": 180,
            },
            {
                "code": "THERMISTOR",
                "component_type": "SUBPART",
                "parent_component": "FUSER_UNIT",
                "name": "Termistor",
                "condition_control": "none",
                "is_consumable": False,
                "is_reusable": True,
                "can_be_repaired": False,
                "requires_removed_part_tracking": True,
                "unit_of_measure": "unit",
                "display_order": 190,
            },
            {
                "code": "THERMOSTAT",
                "component_type": "SUBPART",
                "parent_component": "FUSER_UNIT",
                "name": "Termostato",
                "condition_control": "none",
                "is_consumable": False,
                "is_reusable": True,
                "can_be_repaired": False,
                "requires_removed_part_tracking": True,
                "unit_of_measure": "unit",
                "display_order": 200,
            },
            {
                "code": "TRANSFER_BELT",
                "component_type": "SUBPART",
                "parent_component": "TRANSFER_UNIT",
                "name": "Faja de transferencia",
                "condition_control": "meter",
                "expected_life_meter": 300000,
                "is_consumable": True,
                "is_reusable": False,
                "can_be_repaired": False,
                "requires_removed_part_tracking": True,
                "unit_of_measure": "unit",
                "display_order": 210,
            },
            {
                "code": "TRANSFER_CLEANING_BLADE",
                "component_type": "SUBPART",
                "parent_component": "TRANSFER_UNIT",
                "name": "Cuchilla de limpieza de transferencia",
                "condition_control": "meter",
                "expected_life_meter": 200000,
                "is_consumable": True,
                "is_reusable": False,
                "can_be_repaired": False,
                "requires_removed_part_tracking": True,
                "unit_of_measure": "unit",
                "display_order": 220,
            },
            {
                "code": "PICKUP_ROLLER",
                "component_type": "SUBPART",
                "parent_component": "PAPER_FEED_UNIT",
                "name": "Rodillo de alimentación",
                "condition_control": "meter",
                "expected_life_meter": 150000,
                "is_consumable": True,
                "is_reusable": False,
                "can_be_repaired": False,
                "requires_removed_part_tracking": True,
                "unit_of_measure": "unit",
                "display_order": 230,
            },
            {
                "code": "SEPARATION_ROLLER",
                "component_type": "SUBPART",
                "parent_component": "PAPER_FEED_UNIT",
                "name": "Rodillo de separación",
                "condition_control": "meter",
                "expected_life_meter": 150000,
                "is_consumable": True,
                "is_reusable": False,
                "can_be_repaired": False,
                "requires_removed_part_tracking": True,
                "unit_of_measure": "unit",
                "display_order": 240,
            },
            {
                "code": "SEPARATION_PAD",
                "component_type": "SUBPART",
                "parent_component": "PAPER_FEED_UNIT",
                "name": "Pad de separación",
                "condition_control": "meter",
                "expected_life_meter": 150000,
                "is_consumable": True,
                "is_reusable": False,
                "can_be_repaired": False,
                "requires_removed_part_tracking": True,
                "unit_of_measure": "unit",
                "display_order": 250,
            },
            {
                "code": "ADF_PICKUP_ROLLER",
                "component_type": "SUBPART",
                "parent_component": "ADF_UNIT",
                "name": "Rodillo de alimentación ADF",
                "condition_control": "meter",
                "expected_life_meter": 150000,
                "is_consumable": True,
                "is_reusable": False,
                "can_be_repaired": False,
                "requires_removed_part_tracking": True,
                "unit_of_measure": "unit",
                "display_order": 260,
            },
            {
                "code": "ADF_SEPARATION_ROLLER",
                "component_type": "SUBPART",
                "parent_component": "ADF_UNIT",
                "name": "Rodillo de separación ADF",
                "condition_control": "meter",
                "expected_life_meter": 150000,
                "is_consumable": True,
                "is_reusable": False,
                "can_be_repaired": False,
                "requires_removed_part_tracking": True,
                "unit_of_measure": "unit",
                "display_order": 270,
            },
            {
                "code": "FINISHER",
                "component_type": "ACCESSORY",
                "name": "Finalizador",
                "condition_control": "none",
                "requires_individual_serial": True,
                "is_consumable": False,
                "is_reusable": True,
                "can_be_repaired": True,
                "requires_removed_part_tracking": True,
                "unit_of_measure": "unit",
                "display_order": 300,
            },
            {
                "code": "BOOKLET_FINISHER",
                "component_type": "ACCESSORY",
                "name": "Finalizador de cuadernillos",
                "condition_control": "none",
                "requires_individual_serial": True,
                "is_consumable": False,
                "is_reusable": True,
                "can_be_repaired": True,
                "requires_removed_part_tracking": True,
                "unit_of_measure": "unit",
                "display_order": 310,
            },
            {
                "code": "PAPER_DECK",
                "component_type": "ACCESSORY",
                "name": "Banco de papel",
                "condition_control": "none",
                "requires_individual_serial": True,
                "is_consumable": False,
                "is_reusable": True,
                "can_be_repaired": True,
                "requires_removed_part_tracking": True,
                "unit_of_measure": "unit",
                "display_order": 320,
            },
            {
                "code": "DOCUMENT_FEEDER",
                "component_type": "ACCESSORY",
                "name": "Alimentador de documentos",
                "condition_control": "none",
                "requires_individual_serial": True,
                "is_consumable": False,
                "is_reusable": True,
                "can_be_repaired": True,
                "requires_removed_part_tracking": True,
                "unit_of_measure": "unit",
                "display_order": 330,
            },
            {
                "code": "TONER_BLACK",
                "component_type": "TONER",
                "name": "Tóner",
                "color": "black",
                "condition_control": "none",
                "is_consumable": True,
                "is_reusable": False,
                "can_be_repaired": False,
                "requires_removed_part_tracking": False,
                "unit_of_measure": "bottle",
                "display_order": 400,
            },
            {
                "code": "TONER_CYAN",
                "component_type": "TONER",
                "name": "Tóner",
                "color": "cyan",
                "condition_control": "none",
                "is_consumable": True,
                "is_reusable": False,
                "can_be_repaired": False,
                "requires_removed_part_tracking": False,
                "unit_of_measure": "bottle",
                "display_order": 410,
            },
            {
                "code": "TONER_MAGENTA",
                "component_type": "TONER",
                "name": "Tóner",
                "color": "magenta",
                "condition_control": "none",
                "is_consumable": True,
                "is_reusable": False,
                "can_be_repaired": False,
                "requires_removed_part_tracking": False,
                "unit_of_measure": "bottle",
                "display_order": 420,
            },
            {
                "code": "TONER_YELLOW",
                "component_type": "TONER",
                "name": "Tóner",
                "color": "yellow",
                "condition_control": "none",
                "is_consumable": True,
                "is_reusable": False,
                "can_be_repaired": False,
                "requires_removed_part_tracking": False,
                "unit_of_measure": "bottle",
                "display_order": 430,
            },
            {
                "code": "WASTE_TONER_CONTAINER",
                "component_type": "SPARE_PART",
                "name": "Depósito de tóner residual",
                "condition_control": "meter",
                "expected_life_meter": 100000,
                "is_consumable": True,
                "is_reusable": False,
                "can_be_repaired": False,
                "requires_removed_part_tracking": True,
                "unit_of_measure": "unit",
                "display_order": 500,
            },
            {
                "code": "MAIN_DRIVE_MOTOR",
                "component_type": "SPARE_PART",
                "name": "Motor principal",
                "condition_control": "none",
                "is_consumable": False,
                "is_reusable": True,
                "can_be_repaired": True,
                "requires_removed_part_tracking": True,
                "unit_of_measure": "unit",
                "display_order": 510,
            },
            {
                "code": "POWER_SUPPLY",
                "component_type": "SPARE_PART",
                "name": "Fuente de alimentación",
                "condition_control": "none",
                "is_consumable": False,
                "is_reusable": True,
                "can_be_repaired": True,
                "requires_removed_part_tracking": True,
                "unit_of_measure": "unit",
                "display_order": 520,
            },
            {
                "code": "MAIN_CONTROLLER_BOARD",
                "component_type": "SPARE_PART",
                "name": "Tarjeta controladora principal",
                "condition_control": "none",
                "is_consumable": False,
                "is_reusable": True,
                "can_be_repaired": True,
                "requires_removed_part_tracking": True,
                "unit_of_measure": "unit",
                "display_order": 530,
            },
            {
                "code": "HARD_DISK",
                "component_type": "SPARE_PART",
                "name": "Disco duro",
                "condition_control": "none",
                "is_consumable": False,
                "is_reusable": True,
                "can_be_repaired": False,
                "requires_removed_part_tracking": True,
                "unit_of_measure": "unit",
                "display_order": 540,
            },
            {
                "code": "CONTROL_PANEL",
                "component_type": "SPARE_PART",
                "name": "Panel de control",
                "condition_control": "none",
                "is_consumable": False,
                "is_reusable": True,
                "can_be_repaired": True,
                "requires_removed_part_tracking": True,
                "unit_of_measure": "unit",
                "display_order": 550,
            },
        ]

        created_components = {}

        pending_components = list(
            components
        )

        while pending_components:
            processed_in_cycle = 0

            for component_data in pending_components.copy():
                data = component_data.copy()

                component_type_code = data.pop(
                    "component_type"
                )

                parent_code = data.pop(
                    "parent_component",
                    None,
                )

                if (
                    parent_code
                    and parent_code not in created_components
                ):
                    continue

                component_type = component_types[
                    component_type_code
                ]

                parent_component = None

                if parent_code:
                    parent_component = created_components[
                        parent_code
                    ]

                defaults = {
                    "component_type": component_type,
                    "parent_component": parent_component,
                    "name": data["name"],
                    "manufacturer_code": data.get(
                        "manufacturer_code",
                        "",
                    ),
                    "alternative_code": data.get(
                        "alternative_code",
                        "",
                    ),
                    "color": data.get(
                        "color",
                        EquipmentComponent.Color.NOT_APPLICABLE,
                    ),
                    "condition_control": data.get(
                        "condition_control",
                        EquipmentComponent.ConditionControl.NONE,
                    ),
                    "expected_life_meter": data.get(
                        "expected_life_meter"
                    ),
                    "expected_life_days": data.get(
                        "expected_life_days"
                    ),
                    "requires_individual_serial": data.get(
                        "requires_individual_serial",
                        False,
                    ),
                    "is_consumable": data.get(
                        "is_consumable",
                        False,
                    ),
                    "is_reusable": data.get(
                        "is_reusable",
                        False,
                    ),
                    "can_be_repaired": data.get(
                        "can_be_repaired",
                        False,
                    ),
                    "requires_removed_part_tracking": data.get(
                        "requires_removed_part_tracking",
                        False,
                    ),
                    "unit_of_measure": data.get(
                        "unit_of_measure",
                        "unit",
                    ),
                    "description": data.get(
                        "description",
                        "",
                    ),
                    "technical_notes": data.get(
                        "technical_notes",
                        "",
                    ),
                    "is_active": True,
                    "display_order": data.get(
                        "display_order",
                        0,
                    ),
                }

                component, created = (
                    EquipmentComponent.objects.update_or_create(
                        code=data["code"],
                        defaults=defaults,
                    )
                )

                created_components[
                    data["code"]
                ] = component

                pending_components.remove(
                    component_data
                )

                processed_in_cycle += 1

                action = (
                    "Creado"
                    if created
                    else "Actualizado"
                )

                self.stdout.write(
                    f"{action} componente: {component}"
                )

            if processed_in_cycle == 0:
                unresolved_codes = [
                    item["code"]
                    for item in pending_components
                ]

                raise RuntimeError(
                    (
                        "No se pudieron resolver los componentes "
                        "principales de: "
                        f"{', '.join(unresolved_codes)}"
                    )
                )

        self.stdout.write(
            self.style.SUCCESS(
                (
                    "Catálogo de componentes creado: "
                    f"{EquipmentComponent.objects.count()} "
                    "componentes registrados."
                )
            )
        )