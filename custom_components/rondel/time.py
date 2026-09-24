"""Alarm time for a Rondel Spot."""

from __future__ import annotations

from datetime import time

from homeassistant.components.time import TimeEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import RondelConfigEntry
from .entity import RondelEntity, setup_spot_platform


async def async_setup_entry(hass: HomeAssistant, entry: RondelConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    setup_spot_platform(hass, entry, async_add_entities, lambda hub, spot: [RondelAlarmTime(hub, spot)])


class RondelAlarmTime(RondelEntity, TimeEntity):
    """When the Spot's daily alarm goes off (its 10-minute sunrise starts before this)."""

    _attr_translation_key = "alarm_time"
    _attr_icon = "mdi:alarm"

    def __init__(self, hub, spot) -> None:
        super().__init__(hub, spot, "alarm_time")

    @property
    def native_value(self) -> time | None:
        try:
            return time.fromisoformat(self._spot.alarm_time)
        except (TypeError, ValueError):
            return None

    async def async_set_value(self, value: time) -> None:
        self._spot.alarm_time = value.strftime("%H:%M:%S")
        self._hub.changed(self._spot)
