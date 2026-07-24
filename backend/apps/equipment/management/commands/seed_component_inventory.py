# -*- coding: utf-8 -*-
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction

from apps.equipment.models import (
    ComponentInventory,
    EquipmentComponent,
)


class Command(BaseCommand):
    help = (
        "Crea el inventario inicial de componentes técnicos, "
        "repuestos, consumibles y accesorios."
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

        inventory_records = [
            {
                "component": "DRUM",
                "internal_code": "INV-DRUM-001",
                "lot_number": "LOTE-DRUM-001",
                "quantity": "20.00",
                "condition": "new",
                "warehouse": "Almacén principal",
                "location": "Estante A1",
                "supplier_name": "",
                "purchase_cost": "85.00",
                "notes": "Stock inicial de cilindros fotoconductores.",
            },
            {
                "component": "CLEANING_BLADE",
                "internal_code": "INV-BLADE-001",
                "lot_number": "LOTE-BLADE-001",
                "quantity": "30.00",
                "condition": "new",
                "warehouse": "Almacén principal",
                "location": "Estante A2",
                "supplier_name": "",
                "purchase_cost": "18.00",
                "notes": "Stock inicial de cuchillas de limpieza.",
            },
            {
                "component": "CHARGE_ROLLER",
                "internal_code": "INV-CHARGE-ROLLER-001",
                "lot_number": "LOTE-CR-001",
                "quantity": "15.00",
                "condition": "new",
                "warehouse": "Almacén principal",
                "location": "Estante A3",
                "supplier_name": "",
                "purchase_cost": "32.00",
                "notes": "",
            },
            {
                "component": "DEVELOPER",
                "internal_code": "INV-DEVELOPER-001",
                "lot_number": "LOTE-DEV-001",
                "quantity": "25.00",
                "condition": "new",
                "warehouse": "Almacén principal",
                "location": "Estante B1",
                "supplier_name": "",
                "purchase_cost": "60.00",
                "notes": "Developer genérico para pruebas iniciales.",
            },
            {
                "component": "MAGNETIC_ROLLER",
                "internal_code": "INV-MAGNETIC-ROLLER-001",
                "lot_number": "LOTE-MR-001",
                "quantity": "10.00",
                "condition": "new",
                "warehouse": "Almacén principal",
                "location": "Estante B2",
                "supplier_name": "",
                "purchase_cost": "90.00",
                "notes": "",
            },
            {
                "component": "HEATING_ROLLER",
                "internal_code": "INV-HEATING-ROLLER-001",
                "lot_number": "LOTE-HR-001",
                "quantity": "12.00",
                "condition": "new",
                "warehouse": "Almacén principal",
                "location": "Estante C1",
                "supplier_name": "",
                "purchase_cost": "115.00",
                "notes": "",
            },
            {
                "component": "PRESSURE_ROLLER",
                "internal_code": "INV-PRESSURE-ROLLER-001",
                "lot_number": "LOTE-PR-001",
                "quantity": "12.00",
                "condition": "new",
                "warehouse": "Almacén principal",
                "location": "Estante C2",
                "supplier_name": "",
                "purchase_cost": "95.00",
                "notes": "",
            },
            {
                "component": "FUSER_FILM",
                "internal_code": "INV-FUSER-FILM-001",
                "lot_number": "LOTE-FF-001",
                "quantity": "20.00",
                "condition": "new",
                "warehouse": "Almacén principal",
                "location": "Estante C3",
                "supplier_name": "",
                "purchase_cost": "75.00",
                "notes": "",
            },
            {
                "component": "FUSER_HEATING_ELEMENT",
                "internal_code": "INV-FUSER-HEATER-001",
                "lot_number": "LOTE-FHE-001",
                "quantity": "8.00",
                "condition": "new",
                "warehouse": "Almacén principal",
                "location": "Estante C4",
                "supplier_name": "",
                "purchase_cost": "120.00",
                "notes": "",
            },
            {
                "component": "THERMISTOR",
                "internal_code": "INV-THERMISTOR-001",
                "lot_number": "LOTE-THERM-001",
                "quantity": "15.00",
                "condition": "new",
                "warehouse": "Almacén principal",
                "location": "Estante C5",
                "supplier_name": "",
                "purchase_cost": "30.00",
                "notes": "",
            },
            {
                "component": "THERMOSTAT",
                "internal_code": "INV-THERMOSTAT-001",
                "lot_number": "LOTE-THST-001",
                "quantity": "15.00",
                "condition": "new",
                "warehouse": "Almacén principal",
                "location": "Estante C6",
                "supplier_name": "",
                "purchase_cost": "28.00",
                "notes": "",
            },
            {
                "component": "TRANSFER_BELT",
                "internal_code": "INV-TRANSFER-BELT-001",
                "lot_number": "LOTE-TB-001",
                "quantity": "8.00",
                "condition": "new",
                "warehouse": "Almacén principal",
                "location": "Estante D1",
                "supplier_name": "",
                "purchase_cost": "240.00",
                "notes": "",
            },
            {
                "component": "TRANSFER_CLEANING_BLADE",
                "internal_code": "INV-TRANSFER-BLADE-001",
                "lot_number": "LOTE-TCB-001",
                "quantity": "15.00",
                "condition": "new",
                "warehouse": "Almacén principal",
                "location": "Estante D2",
                "supplier_name": "",
                "purchase_cost": "45.00",
                "notes": "",
            },
            {
                "component": "PICKUP_ROLLER",
                "internal_code": "INV-PICKUP-ROLLER-001",
                "lot_number": "LOTE-PUR-001",
                "quantity": "40.00",
                "condition": "new",
                "warehouse": "Almacén principal",
                "location": "Estante E1",
                "supplier_name": "",
                "purchase_cost": "22.00",
                "notes": "",
            },
            {
                "component": "SEPARATION_ROLLER",
                "internal_code": "INV-SEPARATION-ROLLER-001",
                "lot_number": "LOTE-SR-001",
                "quantity": "30.00",
                "condition": "new",
                "warehouse": "Almacén principal",
                "location": "Estante E2",
                "supplier_name": "",
                "purchase_cost": "25.00",
                "notes": "",
            },
            {
                "component": "SEPARATION_PAD",
                "internal_code": "INV-SEPARATION-PAD-001",
                "lot_number": "LOTE-SP-001",
                "quantity": "30.00",
                "condition": "new",
                "warehouse": "Almacén principal",
                "location": "Estante E3",
                "supplier_name": "",
                "purchase_cost": "15.00",
                "notes": "",
            },
            {
                "component": "ADF_PICKUP_ROLLER",
                "internal_code": "INV-ADF-PICKUP-001",
                "lot_number": "LOTE-ADF-PU-001",
                "quantity": "20.00",
                "condition": "new",
                "warehouse": "Almacén principal",
                "location": "Estante E4",
                "supplier_name": "",
                "purchase_cost": "28.00",
                "notes": "",
            },
            {
                "component": "ADF_SEPARATION_ROLLER",
                "internal_code": "INV-ADF-SEPARATION-001",
                "lot_number": "LOTE-ADF-SR-001",
                "quantity": "20.00",
                "condition": "new",
                "warehouse": "Almacén principal",
                "location": "Estante E5",
                "supplier_name": "",
                "purchase_cost": "30.00",
                "notes": "",
            },
            {
                "component": "TONER_BLACK",
                "internal_code": "INV-TONER-K-001",
                "lot_number": "LOTE-TONER-K-001",
                "quantity": "50.00",
                "condition": "new",
                "warehouse": "Almacén principal",
                "location": "Zona de tóners K",
                "supplier_name": "",
                "purchase_cost": "70.00",
                "notes": "",
            },
            {
                "component": "TONER_CYAN",
                "internal_code": "INV-TONER-C-001",
                "lot_number": "LOTE-TONER-C-001",
                "quantity": "30.00",
                "condition": "new",
                "warehouse": "Almacén principal",
                "location": "Zona de tóners C",
                "supplier_name": "",
                "purchase_cost": "85.00",
                "notes": "",
            },
            {
                "component": "TONER_MAGENTA",
                "internal_code": "INV-TONER-M-001",
                "lot_number": "LOTE-TONER-M-001",
                "quantity": "30.00",
                "condition": "new",
                "warehouse": "Almacén principal",
                "location": "Zona de tóners M",
                "supplier_name": "",
                "purchase_cost": "85.00",
                "notes": "",
            },
            {
                "component": "TONER_YELLOW",
                "internal_code": "INV-TONER-Y-001",
                "lot_number": "LOTE-TONER-Y-001",
                "quantity": "30.00",
                "condition": "new",
                "warehouse": "Almacén principal",
                "location": "Zona de tóners Y",
                "supplier_name": "",
                "purchase_cost": "85.00",
                "notes": "",
            },
            {
                "component": "WASTE_TONER_CONTAINER",
                "internal_code": "INV-WASTE-TONER-001",
                "lot_number": "LOTE-WTC-001",
                "quantity": "15.00",
                "condition": "new",
                "warehouse": "Almacén principal",
                "location": "Estante F1",
                "supplier_name": "",
                "purchase_cost": "45.00",
                "notes": "",
            },
            {
                "component": "MAIN_DRIVE_MOTOR",
                "internal_code": "INV-MOTOR-001",
                "lot_number": "LOTE-MOTOR-001",
                "quantity": "5.00",
                "condition": "refurbished",
                "warehouse": "Almacén técnico",
                "location": "Zona de componentes reparables",
                "supplier_name": "",
                "purchase_cost": "180.00",
                "notes": "Motores revisados para pruebas.",
            },
            {
                "component": "POWER_SUPPLY",
                "internal_code": "INV-POWER-SUPPLY-001",
                "lot_number": "LOTE-PS-001",
                "quantity": "6.00",
                "condition": "refurbished",
                "warehouse": "Almacén técnico",
                "location": "Zona electrónica",
                "supplier_name": "",
                "purchase_cost": "220.00",
                "notes": "",
            },
            {
                "component": "MAIN_CONTROLLER_BOARD",
                "internal_code": "INV-MAIN-BOARD-001",
                "lot_number": "LOTE-MB-001",
                "quantity": "4.00",
                "condition": "refurbished",
                "warehouse": "Almacén técnico",
                "location": "Zona electrónica",
                "supplier_name": "",
                "purchase_cost": "350.00",
                "notes": "",
            },
            {
                "component": "HARD_DISK",
                "internal_code": "INV-HARD-DISK-001",
                "lot_number": "LOTE-HDD-001",
                "quantity": "8.00",
                "condition": "used",
                "warehouse": "Almacén técnico",
                "location": "Zona electrónica",
                "supplier_name": "",
                "purchase_cost": "80.00",
                "notes": "",
            },
            {
                "component": "CONTROL_PANEL",
                "internal_code": "INV-CONTROL-PANEL-001",
                "lot_number": "LOTE-CP-001",
                "quantity": "4.00",
                "condition": "refurbished",
                "warehouse": "Almacén técnico",
                "location": "Zona electrónica",
                "supplier_name": "",
                "purchase_cost": "280.00",
                "notes": "",
            },
        ]

        serialized_inventory = [
            {
                "component": "IMAGE_UNIT",
                "internal_code": "INV-IU-MONO-001",
                "serial_number": "IU-MONO-0001",
                "condition": "refurbished",
                "warehouse": "Almacén técnico",
                "location": "Zona de unidades técnicas",
                "purchase_cost": "350.00",
            },
            {
                "component": "IMAGE_UNIT_BLACK",
                "internal_code": "INV-IU-K-001",
                "serial_number": "IU-K-0001",
                "condition": "refurbished",
                "warehouse": "Almacén técnico",
                "location": "Zona de unidades técnicas",
                "purchase_cost": "380.00",
            },
            {
                "component": "IMAGE_UNIT_CYAN",
                "internal_code": "INV-IU-C-001",
                "serial_number": "IU-C-0001",
                "condition": "refurbished",
                "warehouse": "Almacén técnico",
                "location": "Zona de unidades técnicas",
                "purchase_cost": "380.00",
            },
            {
                "component": "IMAGE_UNIT_MAGENTA",
                "internal_code": "INV-IU-M-001",
                "serial_number": "IU-M-0001",
                "condition": "refurbished",
                "warehouse": "Almacén técnico",
                "location": "Zona de unidades técnicas",
                "purchase_cost": "380.00",
            },
            {
                "component": "IMAGE_UNIT_YELLOW",
                "internal_code": "INV-IU-Y-001",
                "serial_number": "IU-Y-0001",
                "condition": "refurbished",
                "warehouse": "Almacén técnico",
                "location": "Zona de unidades técnicas",
                "purchase_cost": "380.00",
            },
            {
                "component": "DEVELOPER_UNIT",
                "internal_code": "INV-DU-MONO-001",
                "serial_number": "DU-MONO-0001",
                "condition": "refurbished",
                "warehouse": "Almacén técnico",
                "location": "Zona de unidades técnicas",
                "purchase_cost": "320.00",
            },
            {
                "component": "FUSER_UNIT",
                "internal_code": "INV-FUSER-001",
                "serial_number": "FUSER-0001",
                "condition": "refurbished",
                "warehouse": "Almacén técnico",
                "location": "Zona de fusores",
                "purchase_cost": "450.00",
            },
            {
                "component": "TRANSFER_UNIT",
                "internal_code": "INV-TRANSFER-001",
                "serial_number": "TRANSFER-0001",
                "condition": "refurbished",
                "warehouse": "Almacén técnico",
                "location": "Zona de transferencia",
                "purchase_cost": "420.00",
            },
            {
                "component": "DUPLEX_UNIT",
                "internal_code": "INV-DUPLEX-001",
                "serial_number": "DUPLEX-0001",
                "condition": "used",
                "warehouse": "Almacén técnico",
                "location": "Zona de unidades técnicas",
                "purchase_cost": "200.00",
            },
            {
                "component": "PAPER_FEED_UNIT",
                "internal_code": "INV-PAPER-FEED-001",
                "serial_number": "PAPER-FEED-0001",
                "condition": "used",
                "warehouse": "Almacén técnico",
                "location": "Zona de unidades técnicas",
                "purchase_cost": "180.00",
            },
            {
                "component": "ADF_UNIT",
                "internal_code": "INV-ADF-001",
                "serial_number": "ADF-0001",
                "condition": "used",
                "warehouse": "Almacén técnico",
                "location": "Zona de alimentadores",
                "purchase_cost": "250.00",
            },
            {
                "component": "FINISHER",
                "internal_code": "INV-FINISHER-001",
                "serial_number": "FINISHER-0001",
                "condition": "used",
                "warehouse": "Almacén de accesorios",
                "location": "Zona de finalizadores",
                "purchase_cost": "750.00",
            },
            {
                "component": "BOOKLET_FINISHER",
                "internal_code": "INV-BOOKLET-001",
                "serial_number": "BOOKLET-0001",
                "condition": "used",
                "warehouse": "Almacén de accesorios",
                "location": "Zona de finalizadores",
                "purchase_cost": "950.00",
            },
            {
                "component": "PAPER_DECK",
                "internal_code": "INV-PAPER-DECK-001",
                "serial_number": "PAPER-DECK-0001",
                "condition": "used",
                "warehouse": "Almacén de accesorios",
                "location": "Zona de bancos de papel",
                "purchase_cost": "600.00",
            },
            {
                "component": "DOCUMENT_FEEDER",
                "internal_code": "INV-DOC-FEEDER-001",
                "serial_number": "DOC-FEEDER-0001",
                "condition": "used",
                "warehouse": "Almacén de accesorios",
                "location": "Zona de alimentadores",
                "purchase_cost": "350.00",
            },
        ]

        created_count = 0
        updated_count = 0

        for item in inventory_records:
            component_code = item["component"]
            component = components.get(
                component_code
            )

            if not component:
                self.stdout.write(
                    self.style.WARNING(
                        (
                            "Componente no encontrado, se omitió: "
                            f"{component_code}"
                        )
                    )
                )
                continue

            inventory, created = (
                ComponentInventory.objects.update_or_create(
                    internal_code=item["internal_code"],
                    defaults={
                        "component": component,
                        "serial_number": "",
                        "lot_number": item.get(
                            "lot_number",
                            "",
                        ),
                        "quantity": Decimal(
                            item.get(
                                "quantity",
                                "1.00",
                            )
                        ),
                        "reserved_quantity": Decimal(
                            "0.00"
                        ),
                        "condition": item.get(
                            "condition",
                            ComponentInventory.Condition.NEW,
                        ),
                        "status": (
                            ComponentInventory.Status.AVAILABLE
                        ),
                        "warehouse": item.get(
                            "warehouse",
                            "Almacén principal",
                        ),
                        "location": item.get(
                            "location",
                            "",
                        ),
                        "supplier_name": item.get(
                            "supplier_name",
                            "",
                        ),
                        "purchase_cost": Decimal(
                            item["purchase_cost"]
                        )
                        if item.get("purchase_cost")
                        else None,
                        "acquisition_date": None,
                        "initial_meter": None,
                        "notes": item.get(
                            "notes",
                            "",
                        ),
                        "is_active": True,
                    },
                )
            )

            if created:
                created_count += 1
                action = "Creado"
            else:
                updated_count += 1
                action = "Actualizado"

            self.stdout.write(
                f"{action} inventario: {inventory}"
            )

        for item in serialized_inventory:
            component_code = item["component"]
            component = components.get(
                component_code
            )

            if not component:
                self.stdout.write(
                    self.style.WARNING(
                        (
                            "Componente no encontrado, se omitió: "
                            f"{component_code}"
                        )
                    )
                )
                continue

            inventory, created = (
                ComponentInventory.objects.update_or_create(
                    internal_code=item["internal_code"],
                    defaults={
                        "component": component,
                        "serial_number": item[
                            "serial_number"
                        ],
                        "lot_number": "",
                        "quantity": Decimal("1.00"),
                        "reserved_quantity": Decimal("0.00"),
                        "condition": item.get(
                            "condition",
                            ComponentInventory.Condition.USED,
                        ),
                        "status": (
                            ComponentInventory.Status.AVAILABLE
                        ),
                        "warehouse": item.get(
                            "warehouse",
                            "Almacén técnico",
                        ),
                        "location": item.get(
                            "location",
                            "",
                        ),
                        "supplier_name": "",
                        "purchase_cost": Decimal(
                            item["purchase_cost"]
                        )
                        if item.get("purchase_cost")
                        else None,
                        "acquisition_date": None,
                        "initial_meter": item.get(
                            "initial_meter"
                        ),
                        "notes": (
                            "Registro inicial controlado "
                            "mediante serie individual."
                        ),
                        "is_active": True,
                    },
                )
            )

            if created:
                created_count += 1
                action = "Creado"
            else:
                updated_count += 1
                action = "Actualizado"

            self.stdout.write(
                f"{action} inventario serializado: {inventory}"
            )

        self.stdout.write(
            self.style.SUCCESS(
                (
                    "Inventario inicial procesado correctamente. "
                    f"Creados: {created_count}. "
                    f"Actualizados: {updated_count}. "
                    "Total de registros: "
                    f"{ComponentInventory.objects.count()}."
                )
            )
        )