"""Backlight brightness and sleep sound timer for a re-spot Spot."""

from __future__ import annotations

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.const import PERCENTAGE, UnitOfTime
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import RespotConfigEntry
from .entity import RespotEntity, setup_spot_platform


async def async_setup_entry(hass: HomeAssistant, entry: RespotConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    setup_spot_platform(hass, entry, async_add_entities, lambda hub, spot: [RespotBrightness(hub, spot), RespotSleepTimer(hub, spot)])


class RespotBrightness(RespotEntity, NumberEntity):
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


class RespotSleepTimer(RespotEntity, NumberEntity):
    """Minutes left on the current sleep sound's timer; 0 means it plays with no timer.

    Only takes effect while a sleep sound (see the Sound select) is actually playing - setting it
    with nothing playing has nowhere to apply the timer to.
    """

    _attr_translation_key = "sleep_timer"
    _attr_icon = "mdi:timer-outline"
    _attr_native_min_value = 0
    _attr_native_max_value = 120
    _attr_native_step = 1
    _attr_native_unit_of_measurement = UnitOfTime.MINUTES
    _attr_mode = NumberMode.BOX

    def __init__(self, hub, spot) -> None:
        super().__init__(hub, spot, "sleep_timer")

    @property
    def native_value(self) -> float:
        return self._spot.sleep_timer

    async def async_set_native_value(self, value: float) -> None:
        self._spot.sleep_timer = value
        self._hub.changed(self._spot)
