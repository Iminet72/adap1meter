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

# Itt a SENSOR_MAPPING-ből csak pár példát hagyok meg, egészítsd ki a teljes listával
SENSOR_MAPPING = {
    "os_version": ("ADA firmware verzió", None, None),
    "local_ip": ("Local IP", None, None),
    "voltage_phase_l1": ("Feszültség L1", "V", SensorDeviceClass.VOLTAGE),
    "current_phase_l1": ("Áramerősség L1", "A", SensorDeviceClass.CURRENT),
    # ... folytasd a saját teljes listáddal
}

async def async_setup_entry(hass, config_entry, async_add_entities):
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
                    "active_export_energy_total",
                    "total_active_energy",
                ]
                else None
            )
            sensors.append(
                AdaOkosMeroSensor(
                    coordinator,
                    config_entry.entry_id,  # ← Ezt használjuk az egyediséghez
                    sensor_name,
                    friendly_name,
                    unit_of_measurement,
                    device_info,
                    device_class=device_class,
                    state_class=state_class,
                )
            )

    async_add_entities(sensors)


class AdaOkosMeroSensor(CoordinatorEntity, SensorEntity):
    def __init__(
        self,
        coordinator,
        entry_id,
        sensor_name,
        friendly_name,
        unit_of_measurement,
        device_info,
        device_class=None,
        state_class=None,
    ):
        super().__init__(coordinator)
        self._entry_id = entry_id
        self._name = sensor_name
        self._friendly_name = friendly_name
        self._unit_of_measurement = unit_of_measurement
        self._device_info = device_info
        self._device_class = device_class
        self._state_class = state_class
        self._state = None

    @property
    def name(self):
        return self._friendly_name

    @property
    def state(self):
        return self.coordinator.data.get(self._name)

    @property
    def unit_of_measurement(self):
        return self._unit_of_measurement

    @property
    def device_class(self):
        return self._device_class

    @property
    def state_class(self):
        return self._state_class

    @property
    def device_info(self):
        return self._device_info

    @property
    def unique_id(self):
        return f"{DOMAIN}_{self._entry_id}_{self._name}"
