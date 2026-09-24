"""Screen and alarm switches for a Rondel Spot."""

from __future__ import annotations

from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import RondelConfigEntry
from .entity import RondelEntity, setup_spot_platform


async def async_setup_entry(hass: HomeAssistant, entry: RondelConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    setup_spot_platform(hass, entry, async_add_entities,
                        lambda hub, spot: [RondelSwitch(hub, spot, "screen", "mdi:tablet"), RondelSwitch(hub, spot, "alarm_on", "mdi:alarm")])


class RondelSwitch(RondelEntity, SwitchEntity):
    """A boolean setting on the Spot: "screen" (on/off) or "alarm_on" (alarm enabled)."""

    def __init__(self, hub, spot, key: str, icon: str) -> None:
        super().__init__(hub, spot, key)
        self._key = key
        self._attr_translation_key = "screen" if key == "screen" else "alarm"
        self._attr_icon = icon

    @property
    def is_on(self) -> bool:
        return bool(getattr(self._spot, "screen" if self._key == "screen" else "alarm_on"))

    async def _set(self, value: bool) -> None:
        setattr(self._spot, "screen" if self._key == "screen" else "alarm_on", value)
        self._hub.changed(self._spot)

    async def async_turn_on(self, **kwargs: Any) -> None:
        await self._set(True)

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self._set(False)
