import logging

from homeassistant.components.sensor import (
    SensorEntity,
    SensorDeviceClass,
    SensorStateClass,
)
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.entity import DeviceInfo

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

# Szenzorok leképezése: név, mértékegység, device_class
SENSOR_MAPPING = {
    "os_version": ("ADA firmware verzió", None, None),
    "local_ip": ("Local IP", None, None),
    "timestamp": ("Az adatgyűjtés időbélyege", None, None),
    "cosem_logical_device_name": ("A logikai eszköz azonosító", None, None),
    "meter_serial_number": ("A mérő sorozatszáma", None, None),
    "current_tariff": ("Jelenlegi tarifa azonosítója", None, None),
    "circuit_breaker_status": ("A kismegszakító aktuális állapota", None, None),
    "limiter_threshold": ("A maximális áramfelvétel korlátja", "kW", SensorDeviceClass.POWER),
    "active_import_energy_total": ("Az összes importált energia", "kWh", SensorDeviceClass.ENERGY),
    "active_import_energy_tariff_1": ("Az első tarifán mért összes energia", "kWh", SensorDeviceClass.ENERGY),
    "active_import_energy_tariff_2": ("A második tarifán mért összes energia", "kWh", SensorDeviceClass.ENERGY),
    "active_import_energy_tariff_3": ("A harmadik tarifán mért összes energia", "kWh", SensorDeviceClass.ENERGY),
    "active_import_energy_tariff_4": ("A negyedik tarifán mért összes energia", "kWh", SensorDeviceClass.ENERGY),
    "active_export_energy_total": ("Az összes exportált aktív energia", "kWh", SensorDeviceClass.ENERGY),
    "active_export_energy_tariff_1": ("Az első tarifán mért exportált energia", "kWh", SensorDeviceClass.ENERGY),
    "active_export_energy_tariff_2": ("A második tarifán mért exportált energia", "kWh", SensorDeviceClass.ENERGY),
    "active_export_energy_tariff_3": ("A harmadik tarifán mért exportált energia", "kWh", SensorDeviceClass.ENERGY),
    "active_export_energy_tariff_4": ("A negyedik tarifán mért exportált energia", "kWh", SensorDeviceClass.ENERGY),
        "reactive_import_energy": ("Import meddő energia (+R)", "kVARh", SensorDeviceClass.ENERGY),
    "reactive_export_energy": ("Export meddő energia (-R)", "kVARh", SensorDeviceClass.ENERGY),
    "reactive_energy_qi": ("Import induktív energia", "kVARh", SensorDeviceClass.ENERGY),
    "reactive_energy_qii": ("Import kapacitív energia", "kVARh", SensorDeviceClass.ENERGY),
    "reactive_energy_qiii": ("Export induktív energia", "kVARh", SensorDeviceClass.ENERGY),
    "reactive_energy_qiv": ("Export kapacitív energia", "kVARh", SensorDeviceClass.ENERGY),
    "total_active_energy": ("Az összes energia", "kWh", SensorDeviceClass.ENERGY),
    "voltage_phase_l1": ("Feszültség L1", "V", SensorDeviceClass.VOLTAGE),
    "voltage_phase_l2": ("Feszültség L2", "V", SensorDeviceClass.VOLTAGE),
    "voltage_phase_l3": ("Feszültség L3", "V", SensorDeviceClass.VOLTAGE),
    "current_phase_l1": ("Áramerősség L1 (mérőóra adat)", "A", SensorDeviceClass.CURRENT),
    "current_phase_l2": ("Áramerősség L2 (mérőóra adat)", "A", SensorDeviceClass.CURRENT),
    "current_phase_l3": ("Áramerősség L3 (mérőóra adat)", "A", SensorDeviceClass.CURRENT),
    "current_phase_Bl1": ("Áramerősség L1 (kalkulált adat)", "A", SensorDeviceClass.CURRENT),
    "current_phase_Bl2": ("Áramerősség L2 (kalkulált adat)", "A", SensorDeviceClass.CURRENT),
    "current_phase_Bl3": ("Áramerősség L3 (kalkulált adat)", "A", SensorDeviceClass.CURRENT),
    "power_factor": ("Az összesített teljesítménytényező", None, SensorDeviceClass.POWER_FACTOR),
    "power_factor_l1": ("Teljesítménytényező L1", None, SensorDeviceClass.POWER_FACTOR),
    "power_factor_l2": ("Teljesítménytényező L2", None, SensorDeviceClass.POWER_FACTOR),
    "power_factor_l3": ("Teljesítménytényező L3", None, SensorDeviceClass.POWER_FACTOR),
    "frequency": ("A rendszer frekvenciája", "Hz", SensorDeviceClass.FREQUENCY),
    "instantaneous_power_import": ("Jelenlegi áramfelvétel", "kW", SensorDeviceClass.POWER),
    "instantaneous_power_export": ("Jelenlegi exportált teljesítmény", "kW", SensorDeviceClass.POWER),
    "instantaneous_reactive_power_qi": ("Pillanatnyi meddő teljesítmény (Import Induktív)", "kVAR", SensorDeviceClass.POWER),
    "instantaneous_reactive_power_qii": ("Pillanatnyi meddő teljesítmény (Import Kapacitív)", "kVAR", SensorDeviceClass.POWER),
    "instantaneous_reactive_power_qiii": ("Pillanatnyi meddő teljesítmény (Export Induktív)", "kVAR", SensorDeviceClass.POWER),
    "instantaneous_reactive_power_qiv": ("Pillanatnyi meddő teljesítmény (Export Kapacitív)", "kVAR", SensorDeviceClass.POWER),
    "current_limit_l1": ("Áramerősség korlátja L1", "A", SensorDeviceClass.CURRENT),
    "current_limit_l2": ("Áramerősség korlátja L2", "A", SensorDeviceClass.CURRENT),
    "current_limit_l3": ("Áramerősség korlátja L3", "A", SensorDeviceClass.CURRENT),
}

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Szenzor platform beállítása."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]

    device_info = DeviceInfo(
        identifiers={(DOMAIN, config_entry.entry_id)},
        manufacturer="GreenHESS",
        name="ADA P1 Meter",
        model="ADA P1 Meter",
        sw_version=coordinator.data.get("os_version", "N/A"),
        hw_version=coordinator.data.get("hardware_version", "N/A"),
        serial_number=coordinator.data.get("meter_serial_number", "N/A"),
        connections={("ip", coordinator.data.get("local_ip", "N/A"))},
    )

    sensors = []
    for sensor_name in coordinator.data.keys():
        if sensor_name in SENSOR_MAPPING:
            friendly_name, unit_of_measurement, device_class = SENSOR_MAPPING[sensor_name]
            state_class = (
                SensorStateClass.TOTAL_INCREASING
                if sensor_name in [
                    "active_import_energy_total",
                    "active_import_energy_tariff_1",
                    "active_import_energy_tariff_2",
                    "active_import_energy_tariff_3",
                    "active_import_energy_tariff_4",
                    "active_export_energy_total",
                    "active_export_energy_tariff_1",
                    "active_export_energy_tariff_2",
                    "active_export_energy_tariff_3",
                    "active_export_energy_tariff_4",
                    "total_active_energy",
                ]
                else None
            )
            sensors.append(
                AdaOkosMeroSensor(
                    coordinator,
                    config_entry.entry_id,  # ÚJDONSÁG: entry_id bekerül a szenzorba
                    sensor_name,
                    friendly_name,
                    unit_of_measurement,
                    device_info,
                    device_class=device_class,
                    state_class=state_class,
                )
            )

    async_add_entities(sensors)

