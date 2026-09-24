"""Last message received by a Rondel Spot."""

from __future__ import annotations

from homeassistant.components.sensor import SensorEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import RondelConfigEntry
from .entity import RondelEntity, setup_spot_platform


async def async_setup_entry(hass: HomeAssistant, entry: RondelConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    setup_spot_platform(hass, entry, async_add_entities, lambda hub, spot: [RondelLastMessage(hub, spot)])


class RondelLastMessage(RondelEntity, SensorEntity):
    """The latest icon a friend's Spot sent (e.g. "❤️ from Alex's Spot")."""

    _attr_translation_key = "last_message"
    _attr_icon = "mdi:email-heart-outline"

    def __init__(self, hub, spot) -> None:
        super().__init__(hub, spot, "last_message")

    @property
    def native_value(self) -> str | None:
        return self._spot.last_message
