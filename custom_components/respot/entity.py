"""Base entity for a re-spot Spot."""

from __future__ import annotations

from collections.abc import Callable

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, SIGNAL_NEW_SPOT, SIGNAL_UPDATE
from .hub import RespotHub, Spot


class RespotEntity(Entity):
    """An entity belonging to one Spot's device."""

    _attr_has_entity_name = True
    _attr_should_poll = False

    def __init__(self, hub: RespotHub, spot: Spot, key: str) -> None:
        self._hub = hub
        self._spot = spot
        self._attr_unique_id = f"{spot.spot_id}_{key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, spot.spot_id)},
            name=spot.name,
            manufacturer="re-spot",
            model="Echo Spot (2017)",
            sw_version=spot.version,
        )

    async def async_added_to_hass(self) -> None:
        """Refresh whenever this Spot changes."""
        self.async_on_remove(
            async_dispatcher_connect(self.hass, f"{SIGNAL_UPDATE}_{self._spot.spot_id}", self.async_write_ha_state)
        )


def setup_spot_platform(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
    make: Callable[[RespotHub, Spot], list[Entity]],
) -> None:
    """Add a platform's entities for every known Spot, and for new ones as they register."""
    hub: RespotHub = entry.runtime_data

    @callback
    def add(spot: Spot) -> None:
        async_add_entities(make(hub, spot))

    for spot in hub.spots.values():
        add(spot)
    entry.async_on_unload(async_dispatcher_connect(hass, SIGNAL_NEW_SPOT, add))
