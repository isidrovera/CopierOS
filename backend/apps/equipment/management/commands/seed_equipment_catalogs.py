# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from django.db import transaction

from apps.equipment.models import (
    ComponentType,
    EquipmentBrand,
    EquipmentFamily,
    EquipmentModel,
    EquipmentType,
)


class Command(BaseCommand):
    help = (
        "Crea los catálogos iniciales de tipos, marcas, "
        "familias, modelos y tipos de componentes."
    )

    @transaction.atomic
    def handle(self, *args, **options):
        equipment_types = [
            {
                "code": "MULTIFUNCTION",
                "name": "Multifuncional",
                "description": (
                    "Equipo con funciones de impresión, "
                    "copia y escaneo."
                ),
                "requires_color_definition": True,
                "requires_meter": True,
                "allows_accessories": True,
                "display_order": 10,
            },
            {
                "code": "PHOTOCOPIER",
                "name": "Fotocopiadora",
                "description": (
                    "Equipo destinado principalmente "
                    "a la reproducción de documentos."
                ),
                "requires_color_definition": True,
                "requires_meter": True,
                "allows_accessories": True,
                "display_order": 20,
            },
            {
                "code": "PRINTER",
                "name": "Impresora",
                "description": (
                    "Equipo destinado principalmente "
                    "a la impresión."
                ),
                "requires_color_definition": True,
                "requires_meter": True,
                "allows_accessories": True,
                "display_order": 30,
            },
            {
                "code": "PRODUCTION_PRINTER",
                "name": "Impresora de producción",
                "description": (
                    "Equipo de alto volumen para "
                    "impresión profesional."
                ),
                "requires_color_definition": True,
                "requires_meter": True,
                "allows_accessories": True,
                "display_order": 40,
            },
            {
                "code": "DIGITAL_DUPLICATOR",
                "name": "Duplicadora digital",
                "description": (
                    "Equipo de duplicación digital "
                    "para alto volumen."
                ),
                "requires_color_definition": True,
                "requires_meter": True,
                "allows_accessories": True,
                "display_order": 50,
            },
            {
                "code": "PLOTTER",
                "name": "Plotter",
                "description": (
                    "Equipo de impresión de gran formato."
                ),
                "requires_color_definition": True,
                "requires_meter": True,
                "allows_accessories": True,
                "display_order": 60,
            },
            {
                "code": "SCANNER",
                "name": "Escáner",
                "description": (
                    "Equipo destinado a la digitalización "
                    "de documentos."
                ),
                "requires_color_definition": False,
                "requires_meter": True,
                "allows_accessories": True,
                "display_order": 70,
            },
            {
                "code": "FAX",
                "name": "Fax",
                "description": (
                    "Equipo de transmisión de documentos."
                ),
                "requires_color_definition": False,
                "requires_meter": False,
                "allows_accessories": False,
                "display_order": 80,
            },
            {
                "code": "OTHER",
                "name": "Otro",
                "description": (
                    "Tipo de equipo no incluido "
                    "en las categorías anteriores."
                ),
                "requires_color_definition": False,
                "requires_meter": False,
                "allows_accessories": True,
                "display_order": 999,
            },
        ]

        created_types = {}

        for data in equipment_types:
            equipment_type, created = (
                EquipmentType.objects.update_or_create(
                    code=data["code"],
                    defaults={
                        **data,
                        "is_active": True,
                    },
                )
            )

            created_types[data["code"]] = equipment_type
            action = "Creado" if created else "Actualizado"

            self.stdout.write(
                f"{action} tipo: {equipment_type.name}"
            )

        brands = [
            {
                "code": "CANON",
                "name": "Canon",
                "legal_name": "Canon Inc.",
                "country_code": "JP",
                "country_name": "Japón",
                "display_order": 10,
            },
            {
                "code": "RICOH",
                "name": "Ricoh",
                "legal_name": "Ricoh Company, Ltd.",
                "country_code": "JP",
                "country_name": "Japón",
                "display_order": 20,
            },
            {
                "code": "KONICA_MINOLTA",
                "name": "Konica Minolta",
                "legal_name": "Konica Minolta, Inc.",
                "country_code": "JP",
                "country_name": "Japón",
                "display_order": 30,
            },
            {
                "code": "KYOCERA",
                "name": "Kyocera",
                "legal_name": "Kyocera Corporation",
                "country_code": "JP",
                "country_name": "Japón",
                "display_order": 40,
            },
            {
                "code": "XEROX",
                "name": "Xerox",
                "legal_name": "Xerox Corporation",
                "country_code": "US",
                "country_name": "Estados Unidos",
                "display_order": 50,
            },
            {
                "code": "SHARP",
                "name": "Sharp",
                "legal_name": "Sharp Corporation",
                "country_code": "JP",
                "country_name": "Japón",
                "display_order": 60,
            },
            {
                "code": "RISO",
                "name": "Riso",
                "legal_name": "RISO Kagaku Corporation",
                "country_code": "JP",
                "country_name": "Japón",
                "display_order": 70,
            },
            {
                "code": "HP",
                "name": "HP",
                "legal_name": "HP Inc.",
                "country_code": "US",
                "country_name": "Estados Unidos",
                "display_order": 80,
            },
            {
                "code": "EPSON",
                "name": "Epson",
                "legal_name": "Seiko Epson Corporation",
                "country_code": "JP",
                "country_name": "Japón",
                "display_order": 90,
            },
            {
                "code": "BROTHER",
                "name": "Brother",
                "legal_name": "Brother Industries, Ltd.",
                "country_code": "JP",
                "country_name": "Japón",
                "display_order": 100,
            },
            {
                "code": "TOSHIBA",
                "name": "Toshiba",
                "legal_name": "Toshiba Tec Corporation",
                "country_code": "JP",
                "country_name": "Japón",
                "display_order": 110,
            },
            {
                "code": "LEXMARK",
                "name": "Lexmark",
                "legal_name": "Lexmark International, Inc.",
                "country_code": "US",
                "country_name": "Estados Unidos",
                "display_order": 120,
            },
        ]

        created_brands = {}

        for data in brands:
            brand, created = (
                EquipmentBrand.objects.update_or_create(
                    code=data["code"],
                    defaults={
                        **data,
                        "is_active": True,
                    },
                )
            )

            created_brands[data["code"]] = brand
            action = "Creada" if created else "Actualizada"

            self.stdout.write(
                f"{action} marca: {brand.name}"
            )

        families = [
            {
                "code": "CANON_IR_ADV_C5500_SERIES",
                "brand": "CANON",
                "equipment_type": "MULTIFUNCTION",
                "name": "iR-ADV C5500 Series",
                "display_order": 10,
            },
            {
                "code": "CANON_IR_ADV_C350_SERIES",
                "brand": "CANON",
                "equipment_type": "MULTIFUNCTION",
                "name": "iR-ADV C350 Series",
                "display_order": 20,
            },
            {
                "code": "RICOH_MP_C3004_SERIES",
                "brand": "RICOH",
                "equipment_type": "MULTIFUNCTION",
                "name": "MP C3004 Series",
                "display_order": 30,
            },
            {
                "code": "RICOH_IM_350_430_SERIES",
                "brand": "RICOH",
                "equipment_type": "MULTIFUNCTION",
                "name": "IM 350 / IM 430 Series",
                "display_order": 40,
            },
            {
                "code": "KONICA_BIZHUB_C_SERIES",
                "brand": "KONICA_MINOLTA",
                "equipment_type": "MULTIFUNCTION",
                "name": "bizhub C Series",
                "display_order": 50,
            },
            {
                "code": "KONICA_BIZHUB_I_SERIES",
                "brand": "KONICA_MINOLTA",
                "equipment_type": "MULTIFUNCTION",
                "name": "bizhub i-Series",
                "display_order": 60,
            },
            {
                "code": "RISO_COMCOLOR_GD_SERIES",
                "brand": "RISO",
                "equipment_type": "PRODUCTION_PRINTER",
                "name": "ComColor GD Series",
                "display_order": 70,
            },
            {
                "code": "HP_DESIGNJET_SERIES",
                "brand": "HP",
                "equipment_type": "PLOTTER",
                "name": "DesignJet Series",
                "display_order": 80,
            },
        ]

        created_families = {}

        for data in families:
            family_data = data.copy()

            brand_code = family_data.pop(
                "brand"
            )
            equipment_type_code = family_data.pop(
                "equipment_type"
            )

            family, created = (
                EquipmentFamily.objects.update_or_create(
                    code=family_data["code"],
                    defaults={
                        **family_data,
                        "brand": created_brands[
                            brand_code
                        ],
                        "equipment_type": created_types[
                            equipment_type_code
                        ],
                        "is_active": True,
                    },
                )
            )

            created_families[data["code"]] = family
            action = "Creada" if created else "Actualizada"

            self.stdout.write(
                f"{action} familia: {family}"
            )

        models = [
            {
                "code": "CANON_IR_ADV_C5535I_III",
                "brand": "CANON",
                "equipment_type": "MULTIFUNCTION",
                "equipment_family": (
                    "CANON_IR_ADV_C5500_SERIES"
                ),
                "name": "iR-ADV C5535i III",
                "family": "iR-ADV C5500 Series",
                "color_mode": "color",
                "technology": "laser",
                "maximum_paper_size": "a3",
                "is_multifunction": True,
                "has_color_meter": True,
                "has_scan_meter": True,
            },
            {
                "code": "CANON_IR_ADV_C5560I_III",
                "brand": "CANON",
                "equipment_type": "MULTIFUNCTION",
                "equipment_family": (
                    "CANON_IR_ADV_C5500_SERIES"
                ),
                "name": "iR-ADV C5560i III",
                "family": "iR-ADV C5500 Series",
                "color_mode": "color",
                "technology": "laser",
                "maximum_paper_size": "a3",
                "is_multifunction": True,
                "has_color_meter": True,
                "has_scan_meter": True,
            },
            {
                "code": "CANON_IR_ADV_C356IF_III",
                "brand": "CANON",
                "equipment_type": "MULTIFUNCTION",
                "equipment_family": (
                    "CANON_IR_ADV_C350_SERIES"
                ),
                "name": "iR-ADV C356iF III",
                "family": "iR-ADV C350 Series",
                "color_mode": "color",
                "technology": "laser",
                "maximum_paper_size": "a4",
                "is_multifunction": True,
                "has_color_meter": True,
                "has_scan_meter": True,
            },
            {
                "code": "RICOH_MP_C3004",
                "brand": "RICOH",
                "equipment_type": "MULTIFUNCTION",
                "equipment_family": (
                    "RICOH_MP_C3004_SERIES"
                ),
                "name": "MP C3004",
                "family": "MP C3004 Series",
                "color_mode": "color",
                "technology": "laser",
                "maximum_paper_size": "a3",
                "is_multifunction": True,
                "has_color_meter": True,
                "has_scan_meter": True,
            },
            {
                "code": "RICOH_MP_C3504",
                "brand": "RICOH",
                "equipment_type": "MULTIFUNCTION",
                "equipment_family": (
                    "RICOH_MP_C3004_SERIES"
                ),
                "name": "MP C3504",
                "family": "MP C3004 Series",
                "color_mode": "color",
                "technology": "laser",
                "maximum_paper_size": "a3",
                "is_multifunction": True,
                "has_color_meter": True,
                "has_scan_meter": True,
            },
            {
                "code": "RICOH_MP_C4504EX",
                "brand": "RICOH",
                "equipment_type": "MULTIFUNCTION",
                "equipment_family": (
                    "RICOH_MP_C3004_SERIES"
                ),
                "name": "MP C4504ex",
                "family": "MP C3004 Series",
                "color_mode": "color",
                "technology": "laser",
                "maximum_paper_size": "a3",
                "is_multifunction": True,
                "has_color_meter": True,
                "has_scan_meter": True,
            },
            {
                "code": "RICOH_MP_C6004EX",
                "brand": "RICOH",
                "equipment_type": "MULTIFUNCTION",
                "equipment_family": (
                    "RICOH_MP_C3004_SERIES"
                ),
                "name": "MP C6004ex",
                "family": "MP C3004 Series",
                "color_mode": "color",
                "technology": "laser",
                "maximum_paper_size": "a3",
                "is_multifunction": True,
                "has_color_meter": True,
                "has_scan_meter": True,
            },
            {
                "code": "RICOH_IM_350",
                "brand": "RICOH",
                "equipment_type": "MULTIFUNCTION",
                "equipment_family": (
                    "RICOH_IM_350_430_SERIES"
                ),
                "name": "IM 350",
                "family": "IM 350 / IM 430 Series",
                "color_mode": "monochrome",
                "technology": "laser",
                "maximum_paper_size": "a4",
                "is_multifunction": True,
                "has_color_meter": False,
                "has_scan_meter": True,
            },
            {
                "code": "RICOH_IM_430",
                "brand": "RICOH",
                "equipment_type": "MULTIFUNCTION",
                "equipment_family": (
                    "RICOH_IM_350_430_SERIES"
                ),
                "name": "IM 430",
                "family": "IM 350 / IM 430 Series",
                "color_mode": "monochrome",
                "technology": "laser",
                "maximum_paper_size": "a4",
                "is_multifunction": True,
                "has_color_meter": False,
                "has_scan_meter": True,
            },
            {
                "code": "KONICA_MINOLTA_BIZHUB_C258",
                "brand": "KONICA_MINOLTA",
                "equipment_type": "MULTIFUNCTION",
                "equipment_family": (
                    "KONICA_BIZHUB_C_SERIES"
                ),
                "name": "bizhub C258",
                "family": "bizhub C Series",
                "color_mode": "color",
                "technology": "laser",
                "maximum_paper_size": "a3",
                "is_multifunction": True,
                "has_color_meter": True,
                "has_scan_meter": True,
            },
            {
                "code": "KONICA_MINOLTA_BIZHUB_C450I",
                "brand": "KONICA_MINOLTA",
                "equipment_type": "MULTIFUNCTION",
                "equipment_family": (
                    "KONICA_BIZHUB_I_SERIES"
                ),
                "name": "bizhub C450i",
                "family": "bizhub i-Series",
                "color_mode": "color",
                "technology": "laser",
                "maximum_paper_size": "a3",
                "is_multifunction": True,
                "has_color_meter": True,
                "has_scan_meter": True,
            },
            {
                "code": "KONICA_MINOLTA_BIZHUB_550I",
                "brand": "KONICA_MINOLTA",
                "equipment_type": "MULTIFUNCTION",
                "equipment_family": (
                    "KONICA_BIZHUB_I_SERIES"
                ),
                "name": "bizhub 550i",
                "family": "bizhub i-Series",
                "color_mode": "monochrome",
                "technology": "laser",
                "maximum_paper_size": "a3",
                "is_multifunction": True,
                "has_color_meter": False,
                "has_scan_meter": True,
            },
            {
                "code": "RISO_COMCOLOR_GD9630",
                "brand": "RISO",
                "equipment_type": "PRODUCTION_PRINTER",
                "equipment_family": (
                    "RISO_COMCOLOR_GD_SERIES"
                ),
                "name": "ComColor GD9630",
                "family": "ComColor GD Series",
                "color_mode": "color",
                "technology": "inkjet",
                "maximum_paper_size": "a3",
                "is_multifunction": False,
                "supports_copying": False,
                "supports_scanning": False,
                "has_color_meter": True,
                "has_scan_meter": False,
            },
            {
                "code": "HP_DESIGNJET_T830",
                "brand": "HP",
                "equipment_type": "PLOTTER",
                "equipment_family": (
                    "HP_DESIGNJET_SERIES"
                ),
                "name": "DesignJet T830",
                "family": "DesignJet Series",
                "color_mode": "color",
                "technology": "inkjet",
                "maximum_paper_size": "large_format",
                "is_multifunction": True,
                "has_color_meter": True,
                "has_scan_meter": True,
            },
        ]

        for data in models:
            model_data = data.copy()

            brand_code = model_data.pop(
                "brand"
            )
            equipment_type_code = model_data.pop(
                "equipment_type"
            )
            equipment_family_code = model_data.pop(
                "equipment_family"
            )

            model, created = (
                EquipmentModel.objects.update_or_create(
                    code=model_data["code"],
                    defaults={
                        **model_data,
                        "brand": created_brands[
                            brand_code
                        ],
                        "equipment_type": created_types[
                            equipment_type_code
                        ],
                        "equipment_family": created_families[
                            equipment_family_code
                        ],
                        "supports_printing": model_data.get(
                            "supports_printing",
                            True,
                        ),
                        "supports_copying": model_data.get(
                            "supports_copying",
                            True,
                        ),
                        "supports_scanning": model_data.get(
                            "supports_scanning",
                            True,
                        ),
                        "supports_network": True,
                        "supports_duplex": True,
                        "supports_accessories": True,
                        "supports_technical_units": True,
                        "has_total_meter": True,
                        "has_black_meter": True,
                        "is_active": True,
                    },
                )
            )

            action = "Creado" if created else "Actualizado"

            self.stdout.write(
                f"{action} modelo: {model}"
            )

        component_types = [
            {
                "code": "TECHNICAL_UNIT",
                "name": "Unidad técnica",
                "category": "technical_unit",
                "description": (
                    "Unidad principal interna del equipo."
                ),
                "requires_color": False,
                "requires_serial_number": True,
                "requires_meter": True,
                "controls_stock": True,
                "display_order": 10,
            },
            {
                "code": "COLORED_TECHNICAL_UNIT",
                "name": "Unidad técnica por color",
                "category": "technical_unit",
                "description": (
                    "Unidad técnica identificada por color."
                ),
                "requires_color": True,
                "requires_serial_number": True,
                "requires_meter": True,
                "controls_stock": True,
                "display_order": 20,
            },
            {
                "code": "SUBPART",
                "name": "Subparte",
                "category": "subpart",
                "description": (
                    "Pieza interna perteneciente a una unidad."
                ),
                "requires_color": False,
                "requires_serial_number": False,
                "requires_meter": False,
                "controls_stock": True,
                "display_order": 30,
            },
            {
                "code": "COLORED_SUBPART",
                "name": "Subparte por color",
                "category": "subpart",
                "description": (
                    "Subparte identificada por color."
                ),
                "requires_color": True,
                "requires_serial_number": False,
                "requires_meter": False,
                "controls_stock": True,
                "display_order": 40,
            },
            {
                "code": "ACCESSORY",
                "name": "Accesorio",
                "category": "accessory",
                "description": (
                    "Accesorio instalable o asignable al equipo."
                ),
                "requires_color": False,
                "requires_serial_number": True,
                "requires_meter": False,
                "controls_stock": True,
                "display_order": 50,
            },
            {
                "code": "TONER",
                "name": "Tóner",
                "category": "toner",
                "description": (
                    "Consumible de impresión identificado por color."
                ),
                "requires_color": True,
                "requires_serial_number": False,
                "requires_meter": False,
                "controls_stock": True,
                "display_order": 60,
            },
            {
                "code": "SPARE_PART",
                "name": "Repuesto",
                "category": "spare_part",
                "description": (
                    "Repuesto general utilizado en reparaciones."
                ),
                "requires_color": False,
                "requires_serial_number": False,
                "requires_meter": False,
                "controls_stock": True,
                "display_order": 70,
            },
        ]

        for data in component_types:
            component_type, created = (
                ComponentType.objects.update_or_create(
                    code=data["code"],
                    defaults={
                        **data,
                        "is_active": True,
                    },
                )
            )

            action = "Creado" if created else "Actualizado"

            self.stdout.write(
                f"{action} tipo de componente: "
                f"{component_type.name}"
            )

        self.stdout.write(
            self.style.SUCCESS(
                (
                    "Catálogos iniciales creados: "
                    f"{EquipmentType.objects.count()} tipos, "
                    f"{EquipmentBrand.objects.count()} marcas, "
                    f"{EquipmentFamily.objects.count()} familias, "
                    f"{EquipmentModel.objects.count()} modelos y "
                    f"{ComponentType.objects.count()} tipos "
                    "de componentes."
                )
            )
        )