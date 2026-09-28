"""Boolean settings on a re-spot Spot: screen, alarm enabled, and auto-rotate enabled."""

from __future__ import annotations

from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import RespotConfigEntry
from .entity import RespotEntity, setup_spot_platform

# key -> translation key (the display name comes from strings.json's entity.switch.<translation key>)
SWITCH_KEYS = {"screen": "screen", "alarm_on": "alarm", "rotate_on": "rotate"}
SWITCH_ICONS = {"screen": "mdi:tablet", "alarm_on": "mdi:alarm", "rotate_on": "mdi:rotate-3d-variant"}


async def async_setup_entry(hass: HomeAssistant, entry: RespotConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    setup_spot_platform(hass, entry, async_add_entities,
                        lambda hub, spot: [RespotSwitch(hub, spot, key, SWITCH_ICONS[key]) for key in SWITCH_KEYS])


class RespotSwitch(RespotEntity, SwitchEntity):
    """A boolean setting on the Spot, keyed by its attribute name on Spot (see hub.py)."""

    def __init__(self, hub, spot, key: str, icon: str) -> None:
        super().__init__(hub, spot, key)
        self._key = key
        self._attr_translation_key = SWITCH_KEYS[key]
        self._attr_icon = icon

    @property
    def is_on(self) -> bool:
        return bool(getattr(self._spot, self._key))

    async def _set(self, value: bool) -> None:
        setattr(self._spot, self._key, value)
        self._hub.changed(self._spot)

    async def async_turn_on(self, **kwargs: Any) -> None:
        await self._set(True)

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self._set(False)
