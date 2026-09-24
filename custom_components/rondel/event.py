"""Top-button and alarm events from a Rondel Spot."""

from __future__ import annotations

from typing import Any

from homeassistant.components.event import EventEntity
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import RondelConfigEntry
from .const import ALARM_EVENT_TYPES, BUTTON_EVENT_TYPES, SIGNAL_EVENT
from .entity import RondelEntity, setup_spot_platform


async def async_setup_entry(hass: HomeAssistant, entry: RondelConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    setup_spot_platform(hass, entry, async_add_entities, lambda hub, spot: [
        RondelEvent(hub, spot, "button", "button", BUTTON_EVENT_TYPES, "mdi:gesture-tap-button"),
        RondelEvent(hub, spot, "alarm", "alarm_event", ALARM_EVENT_TYPES, "mdi:alarm-note"),
    ])


class RondelEvent(RondelEntity, EventEntity):
    """Fires when the Spot reports a button press or an alarm stage."""

    def __init__(self, hub, spot, source: str, key: str, types: list[str], icon: str) -> None:
        super().__init__(hub, spot, key)
        self._source = source
        self._attr_translation_key = key
        self._attr_event_types = types
        self._attr_icon = icon

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        self.async_on_remove(
            async_dispatcher_connect(self.hass, f"{SIGNAL_EVENT}_{self._spot.spot_id}_{self._source}", self._fire)
        )

    @callback
    def _fire(self, event_type: str, data: dict[str, Any]) -> None:
        if event_type in self.event_types:
            self._trigger_event(event_type, data)
            self.async_write_ha_state()
