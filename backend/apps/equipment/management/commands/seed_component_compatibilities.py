# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from django.db import transaction

from apps.equipment.models import (
    ComponentCompatibility,
    EquipmentComponent,
    EquipmentFamily,
    EquipmentModel,
)


class Command(BaseCommand):
    help = (
        "Crea las compatibilidades iniciales entre componentes, "
        "familias y modelos de equipos."
    )

    @transaction.atomic
    def handle(self, *args, **options):
        components = {
            component.code: component
            for component in EquipmentComponent.objects.filter(
                archived_at__isnull=True,
                is_active=True,
            )
        }

        families = {
            family.code: family
            for family in EquipmentFamily.objects.filter(
                archived_at__isnull=True,
                is_active=True,
            )
        }

        models = {
            equipment_model.code: equipment_model
            for equipment_model in EquipmentModel.objects.filter(
                archived_at__isnull=True,
                is_active=True,
            )
        }

        required_families = {
            "CANON_IR_ADV_C5500_SERIES",
            "CANON_IR_ADV_C350_SERIES",
            "RICOH_MP_C3004_SERIES",
            "RICOH_IM_350_430_SERIES",
            "KONICA_BIZHUB_C_SERIES",
            "KONICA_BIZHUB_I_SERIES",
            "RISO_COMCOLOR_GD_SERIES",
            "HP_DESIGNJET_SERIES",
        }

        missing_families = sorted(
            required_families.difference(
                families.keys()
            )
        )

        if missing_families:
            self.stderr.write(
                self.style.ERROR(
                    (
                        "Faltan familias de equipos: "
                        f"{', '.join(missing_families)}. "
                        "Ejecuta primero seed_equipment_catalogs."
                    )
                )
            )
            return

        required_components = {
            "IMAGE_UNIT",
            "IMAGE_UNIT_BLACK",
            "IMAGE_UNIT_CYAN",
            "IMAGE_UNIT_MAGENTA",
            "IMAGE_UNIT_YELLOW",
            "DEVELOPER_UNIT",
            "DEVELOPER_UNIT_BLACK",
            "DEVELOPER_UNIT_CYAN",
            "DEVELOPER_UNIT_MAGENTA",
            "DEVELOPER_UNIT_YELLOW",
            "FUSER_UNIT",
            "TRANSFER_UNIT",
            "DUPLEX_UNIT",
            "PAPER_FEED_UNIT",
            "ADF_UNIT",
            "DRUM",
            "CLEANING_BLADE",
            "CHARGE_ROLLER",
            "DEVELOPER",
            "MAGNETIC_ROLLER",
            "HEATING_ROLLER",
            "PRESSURE_ROLLER",
            "FUSER_FILM",
            "FUSER_HEATING_ELEMENT",
            "THERMISTOR",
            "THERMOSTAT",
            "TRANSFER_BELT",
            "TRANSFER_CLEANING_BLADE",
            "PICKUP_ROLLER",
            "SEPARATION_ROLLER",
            "SEPARATION_PAD",
            "ADF_PICKUP_ROLLER",
            "ADF_SEPARATION_ROLLER",
            "FINISHER",
            "BOOKLET_FINISHER",
            "PAPER_DECK",
            "DOCUMENT_FEEDER",
            "TONER_BLACK",
            "TONER_CYAN",
            "TONER_MAGENTA",
            "TONER_YELLOW",
            "WASTE_TONER_CONTAINER",
            "MAIN_DRIVE_MOTOR",
            "POWER_SUPPLY",
            "MAIN_CONTROLLER_BOARD",
            "HARD_DISK",
            "CONTROL_PANEL",
            "DRUM_BLACK",
            "CLEANING_BLADE_BLACK",
            "CHARGE_ROLLER_BLACK",
            "DRUM_CYAN",
            "CLEANING_BLADE_CYAN",
            "CHARGE_ROLLER_CYAN",
            "DRUM_MAGENTA",
            "CLEANING_BLADE_MAGENTA",
            "CHARGE_ROLLER_MAGENTA",
            "DRUM_YELLOW",
            "CLEANING_BLADE_YELLOW",
            "CHARGE_ROLLER_YELLOW",
            "DEVELOPER_BLACK",
            "MAGNETIC_ROLLER_BLACK",
            "DEVELOPER_CYAN",
            "MAGNETIC_ROLLER_CYAN",
            "DEVELOPER_MAGENTA",
            "MAGNETIC_ROLLER_MAGENTA",
            "DEVELOPER_YELLOW",
            "MAGNETIC_ROLLER_YELLOW",
            "DUPLEX_ROLLER",
            "DUPLEX_SENSOR",
            "DUPLEX_GATE",
            "FINISHER_EXIT_ROLLER",
            "FINISHER_STAPLER",
            "FINISHER_EXIT_SENSOR",
            "FINISHER_MOTOR",
            "BOOKLET_FOLD_ROLLER",
            "BOOKLET_STAPLER",
            "BOOKLET_FOLD_SENSOR",
            "PAPER_DECK_PICKUP_ROLLER",
            "PAPER_DECK_SEPARATION_ROLLER",
            "PAPER_DECK_SENSOR",
            "PAPER_DECK_LIFT_MOTOR",
            "DOCUMENT_FEEDER_PICKUP_ROLLER",
            "DOCUMENT_FEEDER_SEPARATION_ROLLER",
            "DOCUMENT_FEEDER_SENSOR",
        }

        missing_components = sorted(
            required_components.difference(
                components.keys()
            )
        )

        if missing_components:
            self.stderr.write(
                self.style.ERROR(
                    (
                        "Faltan componentes: "
                        f"{', '.join(missing_components)}. "
                        "Ejecuta primero seed_equipment_components."
                    )
                )
            )
            return

        common_multifunction_components = [
            {
                "component": "FUSER_UNIT",
                "position": "main",
                "is_preferred": True,
                "display_order": 10,
            },
            {
                "component": "TRANSFER_UNIT",
                "position": "main",
                "is_preferred": True,
                "display_order": 20,
            },
            {
                "component": "DUPLEX_UNIT",
                "position": "main",
                "is_preferred": True,
                "display_order": 30,
            },
            {
                "component": "PAPER_FEED_UNIT",
                "position": "main",
                "is_preferred": True,
                "display_order": 40,
            },
            {
                "component": "ADF_UNIT",
                "position": "main",
                "is_preferred": True,
                "display_order": 50,
            },
            {
                "component": "DRUM",
                "position": "not_applicable",
                "is_preferred": True,
                "display_order": 60,
            },
            {
                "component": "CLEANING_BLADE",
                "position": "not_applicable",
                "is_preferred": True,
                "display_order": 70,
            },
            {
                "component": "CHARGE_ROLLER",
                "position": "not_applicable",
                "is_preferred": True,
                "display_order": 80,
            },
            {
                "component": "DEVELOPER",
                "position": "not_applicable",
                "is_preferred": True,
                "display_order": 90,
            },
            {
                "component": "MAGNETIC_ROLLER",
                "position": "not_applicable",
                "is_preferred": False,
                "display_order": 100,
            },
            {
                "component": "HEATING_ROLLER",
                "position": "not_applicable",
                "is_preferred": True,
                "display_order": 110,
            },
            {
                "component": "PRESSURE_ROLLER",
                "position": "not_applicable",
                "is_preferred": True,
                "display_order": 120,
            },
            {
                "component": "FUSER_FILM",
                "position": "not_applicable",
                "is_preferred": False,
                "display_order": 130,
            },
            {
                "component": "FUSER_HEATING_ELEMENT",
                "position": "not_applicable",
                "is_preferred": False,
                "display_order": 140,
            },
            {
                "component": "THERMISTOR",
                "position": "not_applicable",
                "is_preferred": False,
                "display_order": 150,
            },
            {
                "component": "THERMOSTAT",
                "position": "not_applicable",
                "is_preferred": False,
                "display_order": 160,
            },
            {
                "component": "TRANSFER_BELT",
                "position": "not_applicable",
                "is_preferred": True,
                "display_order": 170,
            },
            {
                "component": "TRANSFER_CLEANING_BLADE",
                "position": "not_applicable",
                "is_preferred": True,
                "display_order": 180,
            },
            {
                "component": "PICKUP_ROLLER",
                "position": "not_applicable",
                "is_preferred": True,
                "display_order": 190,
            },
            {
                "component": "SEPARATION_ROLLER",
                "position": "not_applicable",
                "is_preferred": True,
                "display_order": 200,
            },
            {
                "component": "SEPARATION_PAD",
                "position": "not_applicable",
                "is_preferred": False,
                "display_order": 210,
            },
            {
                "component": "ADF_PICKUP_ROLLER",
                "position": "not_applicable",
                "is_preferred": True,
                "display_order": 220,
            },
            {
                "component": "ADF_SEPARATION_ROLLER",
                "position": "not_applicable",
                "is_preferred": True,
                "display_order": 230,
            },
            {
                "component": "FINISHER",
                "position": "not_applicable",
                "is_preferred": False,
                "display_order": 240,
            },
            {
                "component": "BOOKLET_FINISHER",
                "position": "not_applicable",
                "is_preferred": False,
                "display_order": 250,
            },
            {
                "component": "PAPER_DECK",
                "position": "not_applicable",
                "is_preferred": False,
                "display_order": 260,
            },
            {
                "component": "DOCUMENT_FEEDER",
                "position": "not_applicable",
                "is_preferred": False,
                "display_order": 270,
            },
            {
                "component": "WASTE_TONER_CONTAINER",
                "position": "not_applicable",
                "is_preferred": True,
                "display_order": 280,
            },
            {
                "component": "MAIN_DRIVE_MOTOR",
                "position": "main",
                "is_preferred": False,
                "display_order": 290,
            },
            {
                "component": "POWER_SUPPLY",
                "position": "main",
                "is_preferred": False,
                "display_order": 300,
            },
            {
                "component": "MAIN_CONTROLLER_BOARD",
                "position": "main",
                "is_preferred": False,
                "display_order": 310,
            },
            {
                "component": "HARD_DISK",
                "position": "main",
                "is_preferred": False,
                "display_order": 320,
            },
            {
                "component": "CONTROL_PANEL",
                "position": "main",
                "is_preferred": False,
                "display_order": 330,
            },
            {
                "component": "DUPLEX_ROLLER",
                "position": "not_applicable",
                "is_preferred": True,
                "display_order": 340,
            },
            {
                "component": "DUPLEX_SENSOR",
                "position": "not_applicable",
                "is_preferred": True,
                "display_order": 350,
            },
            {
                "component": "DUPLEX_GATE",
                "position": "not_applicable",
                "is_preferred": True,
                "display_order": 360,
            },
            {
                "component": "FINISHER_EXIT_ROLLER",
                "position": "not_applicable",
                "is_preferred": True,
                "display_order": 370,
            },
            {
                "component": "FINISHER_STAPLER",
                "position": "not_applicable",
                "is_preferred": True,
                "display_order": 380,
            },
            {
                "component": "FINISHER_EXIT_SENSOR",
                "position": "not_applicable",
                "is_preferred": True,
                "display_order": 390,
            },
            {
                "component": "FINISHER_MOTOR",
                "position": "not_applicable",
                "is_preferred": True,
                "display_order": 400,
            },
            {
                "component": "BOOKLET_FOLD_ROLLER",
                "position": "not_applicable",
                "is_preferred": True,
                "display_order": 410,
            },
            {
                "component": "BOOKLET_STAPLER",
                "position": "not_applicable",
                "is_preferred": True,
                "display_order": 420,
            },
            {
                "component": "BOOKLET_FOLD_SENSOR",
                "position": "not_applicable",
                "is_preferred": True,
                "display_order": 430,
            },
            {
                "component": "PAPER_DECK_PICKUP_ROLLER",
                "position": "not_applicable",
                "is_preferred": True,
                "display_order": 440,
            },
            {
                "component": "PAPER_DECK_SEPARATION_ROLLER",
                "position": "not_applicable",
                "is_preferred": True,
                "display_order": 450,
            },
            {
                "component": "PAPER_DECK_SENSOR",
                "position": "not_applicable",
                "is_preferred": True,
                "display_order": 460,
            },
            {
                "component": "PAPER_DECK_LIFT_MOTOR",
                "position": "not_applicable",
                "is_preferred": True,
                "display_order": 470,
            },
            {
                "component": "DOCUMENT_FEEDER_PICKUP_ROLLER",
                "position": "not_applicable",
                "is_preferred": True,
                "display_order": 480,
            },
            {
                "component": "DOCUMENT_FEEDER_SEPARATION_ROLLER",
                "position": "not_applicable",
                "is_preferred": True,
                "display_order": 490,
            },
            {
                "component": "DOCUMENT_FEEDER_SENSOR",
                "position": "not_applicable",
                "is_preferred": True,
                "display_order": 500,
            },
        ]

        color_components = [
            {
                "component": "IMAGE_UNIT_BLACK",
                "position": "black",
                "display_order": 400,
            },
            {
                "component": "IMAGE_UNIT_CYAN",
                "position": "cyan",
                "display_order": 410,
            },
            {
                "component": "IMAGE_UNIT_MAGENTA",
                "position": "magenta",
                "display_order": 420,
            },
            {
                "component": "IMAGE_UNIT_YELLOW",
                "position": "yellow",
                "display_order": 430,
            },
            {
                "component": "DEVELOPER_UNIT_BLACK",
                "position": "black",
                "display_order": 440,
            },
            {
                "component": "DEVELOPER_UNIT_CYAN",
                "position": "cyan",
                "display_order": 450,
            },
            {
                "component": "DEVELOPER_UNIT_MAGENTA",
                "position": "magenta",
                "display_order": 460,
            },
            {
                "component": "DEVELOPER_UNIT_YELLOW",
                "position": "yellow",
                "display_order": 470,
            },
            {
                "component": "TONER_BLACK",
                "position": "black",
                "display_order": 480,
            },
            {
                "component": "TONER_CYAN",
                "position": "cyan",
                "display_order": 490,
            },
            {
                "component": "TONER_MAGENTA",
                "position": "magenta",
                "display_order": 500,
            },
            {
                "component": "TONER_YELLOW",
                "position": "yellow",
                "display_order": 510,
            },
            {
                "component": "DRUM_BLACK",
                "position": "black",
                "display_order": 520,
            },
            {
                "component": "CLEANING_BLADE_BLACK",
                "position": "black",
                "display_order": 530,
            },
            {
                "component": "CHARGE_ROLLER_BLACK",
                "position": "black",
                "display_order": 540,
            },
            {
                "component": "DRUM_CYAN",
                "position": "cyan",
                "display_order": 550,
            },
            {
                "component": "CLEANING_BLADE_CYAN",
                "position": "cyan",
                "display_order": 560,
            },
            {
                "component": "CHARGE_ROLLER_CYAN",
                "position": "cyan",
                "display_order": 570,
            },
            {
                "component": "DRUM_MAGENTA",
                "position": "magenta",
                "display_order": 580,
            },
            {
                "component": "CLEANING_BLADE_MAGENTA",
                "position": "magenta",
                "display_order": 590,
            },
            {
                "component": "CHARGE_ROLLER_MAGENTA",
                "position": "magenta",
                "display_order": 600,
            },
            {
                "component": "DRUM_YELLOW",
                "position": "yellow",
                "display_order": 610,
            },
            {
                "component": "CLEANING_BLADE_YELLOW",
                "position": "yellow",
                "display_order": 620,
            },
            {
                "component": "CHARGE_ROLLER_YELLOW",
                "position": "yellow",
                "display_order": 630,
            },
            {
                "component": "DEVELOPER_BLACK",
                "position": "black",
                "display_order": 640,
            },
            {
                "component": "MAGNETIC_ROLLER_BLACK",
                "position": "black",
                "display_order": 650,
            },
            {
                "component": "DEVELOPER_CYAN",
                "position": "cyan",
                "display_order": 660,
            },
            {
                "component": "MAGNETIC_ROLLER_CYAN",
                "position": "cyan",
                "display_order": 670,
            },
            {
                "component": "DEVELOPER_MAGENTA",
                "position": "magenta",
                "display_order": 680,
            },
            {
                "component": "MAGNETIC_ROLLER_MAGENTA",
                "position": "magenta",
                "display_order": 690,
            },
            {
                "component": "DEVELOPER_YELLOW",
                "position": "yellow",
                "display_order": 700,
            },
            {
                "component": "MAGNETIC_ROLLER_YELLOW",
                "position": "yellow",
                "display_order": 710,
            },
        ]

        monochrome_components = [
            {
                "component": "IMAGE_UNIT",
                "position": "monochrome",
                "display_order": 400,
            },
            {
                "component": "DEVELOPER_UNIT",
                "position": "monochrome",
                "display_order": 410,
            },
            {
                "component": "TONER_BLACK",
                "position": "black",
                "display_order": 420,
            },
        ]

        family_configurations = [
            {
                "family": "CANON_IR_ADV_C5500_SERIES",
                "components": (
                    common_multifunction_components
                    + color_components
                ),
            },
            {
                "family": "CANON_IR_ADV_C350_SERIES",
                "components": (
                    common_multifunction_components
                    + color_components
                ),
            },
            {
                "family": "RICOH_MP_C3004_SERIES",
                "components": (
                    common_multifunction_components
                    + color_components
                ),
            },
            {
                "family": "RICOH_IM_350_430_SERIES",
                "components": (
                    common_multifunction_components
                    + monochrome_components
                ),
            },
            {
                "family": "KONICA_BIZHUB_C_SERIES",
                "components": (
                    common_multifunction_components
                    + color_components
                ),
            },
            {
                "family": "KONICA_BIZHUB_I_SERIES",
                "components": (
                    common_multifunction_components
                    + color_components
                    + monochrome_components
                ),
            },
        ]

        created_count = 0
        updated_count = 0

        for configuration in family_configurations:
            family = families[
                configuration["family"]
            ]

            for item in configuration["components"]:
                component = components[
                    item["component"]
                ]

                compatibility, created = (
                    ComponentCompatibility.objects.update_or_create(
                        component=component,
                        equipment_family=family,
                        equipment_model=None,
                        position=item.get(
                            "position",
                            "not_applicable",
                        ),
                        defaults={
                            "compatibility_type": (
                                ComponentCompatibility
                                .CompatibilityType.COMPATIBLE
                            ),
                            "manufacturer_reference": "",
                            "requires_adjustment": False,
                            "adjustment_instructions": "",
                            "is_preferred": item.get(
                                "is_preferred",
                                True,
                            ),
                            "technical_notes": "",
                            "is_active": True,
                            "display_order": item.get(
                                "display_order",
                                0,
                            ),
                        },
                    )
                )

                if created:
                    created_count += 1
                    action = "Creada"
                else:
                    updated_count += 1
                    action = "Actualizada"

                self.stdout.write(
                    (
                        f"{action} compatibilidad: "
                        f"{compatibility}"
                    )
                )

        production_components = [
            "PAPER_FEED_UNIT",
            "DUPLEX_UNIT",
            "PICKUP_ROLLER",
            "SEPARATION_ROLLER",
            "POWER_SUPPLY",
            "MAIN_CONTROLLER_BOARD",
            "HARD_DISK",
            "CONTROL_PANEL",
            "TONER_BLACK",
            "TONER_CYAN",
            "TONER_MAGENTA",
            "TONER_YELLOW",
        ]

        for component_code in production_components:
            component = components[
                component_code
            ]

            position = "not_applicable"

            if component.color == "black":
                position = "black"
            elif component.color == "cyan":
                position = "cyan"
            elif component.color == "magenta":
                position = "magenta"
            elif component.color == "yellow":
                position = "yellow"

            compatibility, created = (
                ComponentCompatibility.objects.update_or_create(
                    component=component,
                    equipment_family=families[
                        "RISO_COMCOLOR_GD_SERIES"
                    ],
                    equipment_model=None,
                    position=position,
                    defaults={
                        "compatibility_type": (
                            ComponentCompatibility
                            .CompatibilityType.COMPATIBLE
                        ),
                        "manufacturer_reference": "",
                        "requires_adjustment": False,
                        "adjustment_instructions": "",
                        "is_preferred": True,
                        "technical_notes": "",
                        "is_active": True,
                        "display_order": 600,
                    },
                )
            )

            if created:
                created_count += 1
                action = "Creada"
            else:
                updated_count += 1
                action = "Actualizada"

            self.stdout.write(
                f"{action} compatibilidad: {compatibility}"
            )

        plotter_components = [
            "PAPER_FEED_UNIT",
            "PICKUP_ROLLER",
            "POWER_SUPPLY",
            "MAIN_CONTROLLER_BOARD",
            "HARD_DISK",
            "CONTROL_PANEL",
            "TONER_BLACK",
            "TONER_CYAN",
            "TONER_MAGENTA",
            "TONER_YELLOW",
        ]

        for component_code in plotter_components:
            component = components[
                component_code
            ]

            position = "not_applicable"

            if component.color == "black":
                position = "black"
            elif component.color == "cyan":
                position = "cyan"
            elif component.color == "magenta":
                position = "magenta"
            elif component.color == "yellow":
                position = "yellow"

            compatibility, created = (
                ComponentCompatibility.objects.update_or_create(
                    component=component,
                    equipment_family=families[
                        "HP_DESIGNJET_SERIES"
                    ],
                    equipment_model=None,
                    position=position,
                    defaults={
                        "compatibility_type": (
                            ComponentCompatibility
                            .CompatibilityType.COMPATIBLE
                        ),
                        "manufacturer_reference": "",
                        "requires_adjustment": False,
                        "adjustment_instructions": "",
                        "is_preferred": True,
                        "technical_notes": "",
                        "is_active": True,
                        "display_order": 700,
                    },
                )
            )

            if created:
                created_count += 1
                action = "Creada"
            else:
                updated_count += 1
                action = "Actualizada"

            self.stdout.write(
                f"{action} compatibilidad: {compatibility}"
            )

        model_specific_compatibilities = [
            {
                "component": "FUSER_UNIT",
                "equipment_model": "CANON_IR_ADV_C5560I_III",
                "position": "main",
                "technical_notes": (
                    "Compatibilidad específica registrada para "
                    "el modelo Canon iR-ADV C5560i III."
                ),
                "display_order": 800,
            },
            {
                "component": "FUSER_UNIT",
                "equipment_model": "RICOH_MP_C6004EX",
                "position": "main",
                "technical_notes": (
                    "Compatibilidad específica registrada para "
                    "el modelo Ricoh MP C6004ex."
                ),
                "display_order": 810,
            },
            {
                "component": "CONTROL_PANEL",
                "equipment_model": (
                    "KONICA_MINOLTA_BIZHUB_C450I"
                ),
                "position": "main",
                "technical_notes": (
                    "Panel de control correspondiente al "
                    "modelo bizhub C450i."
                ),
                "display_order": 820,
            },
        ]

        for item in model_specific_compatibilities:
            equipment_model = models.get(
                item["equipment_model"]
            )

            if not equipment_model:
                self.stdout.write(
                    self.style.WARNING(
                        (
                            "Modelo no encontrado, se omitió: "
                            f"{item['equipment_model']}"
                        )
                    )
                )
                continue

            component = components[
                item["component"]
            ]

            compatibility, created = (
                ComponentCompatibility.objects.update_or_create(
                    component=component,
                    equipment_family=None,
                    equipment_model=equipment_model,
                    position=item["position"],
                    defaults={
                        "compatibility_type": (
                            ComponentCompatibility
                            .CompatibilityType.ORIGINAL
                        ),
                        "manufacturer_reference": "",
                        "requires_adjustment": False,
                        "adjustment_instructions": "",
                        "is_preferred": True,
                        "technical_notes": item.get(
                            "technical_notes",
                            "",
                        ),
                        "is_active": True,
                        "display_order": item.get(
                            "display_order",
                            0,
                        ),
                    },
                )
            )

            if created:
                created_count += 1
                action = "Creada"
            else:
                updated_count += 1
                action = "Actualizada"

            self.stdout.write(
                f"{action} compatibilidad: {compatibility}"
            )

        self.stdout.write(
            self.style.SUCCESS(
                (
                    "Compatibilidades procesadas correctamente. "
                    f"Creadas: {created_count}. "
                    f"Actualizadas: {updated_count}. "
                    "Total registrado: "
                    f"{ComponentCompatibility.objects.count()}."
                )
            )
        )