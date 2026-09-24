"""Backlight brightness for a Rondel Spot."""

from __future__ import annotations

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.const import PERCENTAGE
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import RondelConfigEntry
from .entity import RondelEntity, setup_spot_platform


async def async_setup_entry(hass: HomeAssistant, entry: RondelConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    setup_spot_platform(hass, entry, async_add_entities, lambda hub, spot: [RondelBrightness(hub, spot)])


class RondelBrightness(RondelEntity, NumberEntity):
    """Screen brightness while the screen is on (the Night face and "screen off" still dim it)."""

    _attr_translation_key = "brightness"
    _attr_icon = "mdi:brightness-6"
    _attr_native_min_value = 5
    _attr_native_max_value = 100
    _attr_native_step = 5
    _attr_native_unit_of_measurement = PERCENTAGE
    _attr_mode = NumberMode.SLIDER

    def __init__(self, hub, spot) -> None:
        super().__init__(hub, spot, "brightness")

    @property
    def native_value(self) -> float:
        return self._spot.brightness

    async def async_set_native_value(self, value: float) -> None:
        self._spot.brightness = value
        self._hub.changed(self._spot)
