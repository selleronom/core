"""Sensor module contains the FortumSensor class for energy consumption."""
from datetime import timedelta
import logging

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the Fortum sensor entry.

    Args:
        hass: Home Assistant instance.
        entry: Config entry.
        async_add_entities: Function to add entities.

    Returns:
        None
    """
    api = hass.data[DOMAIN][entry.entry_id]
    coordinator = FortumDataUpdateCoordinator(
        hass,
        _LOGGER,
        name="sensor",
        update_method=api.get_data,
        update_interval=timedelta(minutes=5),
    )
    entities = [
        FortumEnergySensor(coordinator, entry, "kWh"),
        FortumCostSensor(coordinator, entry, "SEK"),
    ]

    await coordinator.async_config_entry_first_refresh()
    async_add_entities(entities)


class FortumDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the API."""

    def __init__(
        self, hass: HomeAssistant, logger, name, update_method, update_interval
    ) -> None:
        """Initialize the global scene coordinator."""
        super().__init__(
            hass,
            logger,
            name=name,
            update_method=update_method,
            update_interval=update_interval,
        )

    async def _async_update_data(self):
        """Update data via library."""
        try:
            return await super()._async_update_data()
        except ValueError as e:
            _LOGGER.error("Failed to update data: %s", e)
            return []


class FortumEnergySensor(CoordinatorEntity, SensorEntity):
    """Class representing the Fortum energy consumption sensor."""

    def __init__(self, coordinator, entry, unit_of_measurement) -> None:
        """Initialize the FortumSensor class."""
        super().__init__(coordinator)
        self._entry = entry
        self._unit_of_measurement = unit_of_measurement

    @property
    def unique_id(self) -> str:
        """Return the unique ID of the sensor."""
        return f"{self._entry.entry_id}_energy_consumption"

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return "MittFortum Energy Consumption"

    @property
    def native_value(self) -> float | None:
        """Return the state of the sensor."""
        data = self.coordinator.data
        if data:
            return data[0]["value"]
        return None

    @property
    def device_state_attributes(self):
        """Return the state attributes."""
        data = self.coordinator.data
        if data:
            return {
                "temperature": data[0]["temp"],
                "date": data[0]["dateTime"],
            }
        return {}

    @property
    def native_unit_of_measurement(self) -> str:
        """Return the unit of measurement."""
        return self._unit_of_measurement

    @property
    def device_class(self) -> SensorDeviceClass:
        """Return the class of this device, from component DEVICE_CLASSES."""
        return SensorDeviceClass.ENERGY

    @property
    def state_class(self) -> SensorStateClass:
        """Return the state class of this device."""
        return SensorStateClass.TOTAL


class FortumCostSensor(CoordinatorEntity, SensorEntity):
    """Representation of a Fortum Cost Sensor."""

    def __init__(self, coordinator, entry, unit_of_measurement) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._entry = entry
        self._unit_of_measurement = unit_of_measurement

    @property
    def unique_id(self) -> str:
        """Return the unique ID of the sensor."""
        return f"{self._entry.entry_id}_cost"

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return "MittFortum Total Cost"

    @property
    def native_value(self) -> float | None:
        """Return the state of the sensor."""
        data = self.coordinator.data
        if data:
            return data[0]["cost"]
        return None

    @property
    def native_unit_of_measurement(self) -> str:
        """Return the unit of measurement."""
        return self._unit_of_measurement

    @property
    def device_class(self) -> SensorDeviceClass:
        """Return the class of this device, from component DEVICE_CLASSES."""
        return SensorDeviceClass.MONETARY

    @property
    def state_class(self) -> SensorStateClass:
        """Return the state class of this device."""
        return SensorStateClass.TOTAL
