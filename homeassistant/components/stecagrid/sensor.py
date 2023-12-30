"""The module contains the StecaGrid sensor implementation."""
from datetime import datetime
import logging

from homeassistant.components.sensor import (
    RestoreSensor,
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    UnitOfElectricCurrent,
    UnitOfElectricPotential,
    UnitOfEnergy,
    UnitOfFrequency,
    UnitOfPower,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the StecaGrid sensor platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    api = hass.data[DOMAIN][entry.entry_id]["api"]

    # Fetch initial data so we have data when entities subscribe
    await coordinator.async_refresh()

    entities: list[StecaGridEntity] = []
    for type_ in coordinator.data:
        entities.append(StecaGridSensor(coordinator, api, type_))
        if type_ == "AC_Power":
            entities.append(StecaGridEnergySensor(coordinator, api, type_))

    async_add_entities(entities)


UNIT_OF_MEASUREMENT_MAP = {
    "A": UnitOfElectricCurrent.AMPERE,
    "V": UnitOfElectricPotential.VOLT,
    "W": UnitOfPower.WATT,
    "Hz": UnitOfFrequency.HERTZ,
    "Wh": UnitOfEnergy.WATT_HOUR,
}

DEVICE_CLASS_MAP = {
    "A": SensorDeviceClass.CURRENT,
    "V": SensorDeviceClass.VOLTAGE,
    "W": SensorDeviceClass.POWER,
    "Hz": SensorDeviceClass.FREQUENCY,
    "Wh": SensorDeviceClass.ENERGY,
}

STATE_CLASS_MAP = {
    "A": SensorStateClass.MEASUREMENT,
    "V": SensorStateClass.MEASUREMENT,
    "W": SensorStateClass.MEASUREMENT,
    "Hz": SensorStateClass.MEASUREMENT,
    "Wh": SensorStateClass.TOTAL_INCREASING,
}


class StecaGridEntity(CoordinatorEntity):
    """Base entity class for StecaGrid sensors."""

    @property
    def device_info(self):
        """Return information about the device that the sensor belongs to."""
        return {
            "identifiers": {(DOMAIN, self.coordinator.config_entry.entry_id)},
            "name": "StecaGrid Inverter",
            "manufacturer": "Steca",
            "model": "Grid",  # Replace with the actual model of the inverter
            "sw_version": "1.0",  # Replace with the actual software version of the inverter
        }


class StecaGridSensor(StecaGridEntity, SensorEntity):
    """Representation of a StecaGrid sensor."""

    def __init__(self, coordinator, api, type_):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.api = api
        self.type_ = type_

    @property
    def unique_id(self):
        """Return a unique ID for this sensor."""
        return f"{self.coordinator.config_entry.entry_id}_{self.type_}"

    @property
    def name(self):
        """Return the name of the sensor."""
        return f"StecaGrid {self.type_} Sensor"

    @property
    def state(self):
        """Return the state of the sensor."""
        return self.coordinator.data[self.type_]["value"]

    @property
    def device_state_attributes(self):
        """Return the state attributes of the sensor."""
        return {"unit": self.coordinator.data[self.type_]["unit"]}

    @property
    def native_unit_of_measurement(self):
        """Return the unit of measurement of the sensor."""
        unit = self.coordinator.data[self.type_]["unit"]
        return UNIT_OF_MEASUREMENT_MAP.get(unit, unit)

    @property
    def device_class(self):
        """Return the class of this device, from component DEVICE_CLASSES."""
        unit = self.coordinator.data[self.type_]["unit"]
        return DEVICE_CLASS_MAP.get(unit)

    @property
    def state_class(self):
        """Return the state class of this device, from component STATE_CLASSES."""
        unit = self.coordinator.data[self.type_]["unit"]
        return STATE_CLASS_MAP.get(unit)


class StecaGridEnergySensor(StecaGridEntity, RestoreSensor):
    """Representation of a StecaGrid sensor."""

    async def async_added_to_hass(self):
        """Run when entity about to be added to hass."""
        await super().async_added_to_hass()

        # Restore the state
        last_state = await self.async_get_last_state()
        if last_state is not None:
            self._energy = float(last_state.state)

    def __init__(self, coordinator, api, type_):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.api = api
        self.type_ = type_
        self._last_updated = datetime.now()
        self._last_value = 0
        self._energy = 0

    @property
    def unique_id(self):
        """Return a unique ID for this sensor."""
        return f"{self.coordinator.config_entry.entry_id}_{self.type_}_energy"

    @property
    def name(self):
        """Return the name of the sensor."""
        return f"StecaGrid {self.type_} Energy Sensor"

    @property
    def device_state_attributes(self):
        """Return the state attributes of the sensor."""
        return {"unit": "Wh"}

    @property
    def native_unit_of_measurement(self):
        """Return the unit of measurement of the sensor."""
        return UNIT_OF_MEASUREMENT_MAP.get("Wh", "Wh")

    @property
    def device_class(self):
        """Return the class of this device, from component DEVICE_CLASSES."""
        return DEVICE_CLASS_MAP.get("Wh")

    @property
    def state_class(self):
        """Return the state class of this device, from component STATE_CLASSES."""
        return STATE_CLASS_MAP.get("Wh")

    @property
    def state(self):
        """Return the state of the sensor."""
        current_value = self.coordinator.data[self.type_]["value"]
        if current_value is None:
            return self._energy  # return the last known state

        # Convert current_value to a float
        try:
            current_value = float(current_value)
        except ValueError:
            return (
                self._energy
            )  # return the last known state if current_value is not a number

        now = datetime.now()

        # Calculate the energy used since the last update
        time_difference = (now - self._last_updated).total_seconds() / 3600  # in hours
        power = (self._last_value + current_value) / 2  # average power
        energy = power * time_difference  # in Wh

        # Update the energy and the state
        self._energy += energy
        self._last_value = current_value
        self._last_updated = now

        return self._energy  # return energy in Wh
