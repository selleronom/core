"""The StecaGrid integration."""
from __future__ import annotations

import asyncio
from datetime import timedelta
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .api import InverterAPI
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up StecaGrid from a config entry."""

    host = entry.data["host"]
    session = hass.helpers.aiohttp_client.async_get_clientsession()
    api = InverterAPI(host, 80, session)  # Assuming the port is 80

    if not await api.validate_connection():
        _LOGGER.error("Could not validate connection to StecaGrid")
        await session.close()
        return False

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name="sensor",
        update_method=api.get_data,
        update_interval=timedelta(seconds=5),
    )

    await coordinator.async_refresh()  # Fetch data from the inverter

    if not coordinator.data:
        _LOGGER.error("Could not fetch data from StecaGrid")
        return False

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = {
        "coordinator": coordinator,
        "api": api,
    }

    for platform in PLATFORMS:
        hass.async_create_task(
            hass.config_entries.async_forward_entry_setup(entry, platform)
        )

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = all(
        await asyncio.gather(
            *[
                hass.config_entries.async_forward_entry_unload(entry, component)
                for component in PLATFORMS
            ]
        )
    )

    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
