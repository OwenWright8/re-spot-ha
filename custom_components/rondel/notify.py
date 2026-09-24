"""Send a text message to a Rondel Spot's screen."""

from __future__ import annotations

from homeassistant.components.notify import NotifyEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import RondelConfigEntry
from .const import EVENT_NOTIFY
from .entity import RondelEntity, setup_spot_platform


async def async_setup_entry(hass: HomeAssistant, entry: RondelConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    setup_spot_platform(hass, entry, async_add_entities, lambda hub, spot: [RondelNotify(hub, spot)])


class RondelNotify(RondelEntity, NotifyEntity):
    """notify.send_message → a pop-up with a chime on the Spot (it listens for rondel_notify events)."""

    _attr_translation_key = "message"

    def __init__(self, hub, spot) -> None:
        super().__init__(hub, spot, "message")

    async def async_send_message(self, message: str, title: str | None = None) -> None:
        self.hass.bus.async_fire(EVENT_NOTIFY, {"spot_id": self._spot.spot_id, "message": message, "title": title})
