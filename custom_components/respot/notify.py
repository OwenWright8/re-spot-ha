"""Send a text message to a re-spot Spot's screen."""

from __future__ import annotations

from homeassistant.components.notify import NotifyEntity
from homeassistant.exceptions import HomeAssistantError
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import RespotConfigEntry
from .const import EVENT_NOTIFY
from .entity import RespotEntity, setup_spot_platform


async def async_setup_entry(hass: HomeAssistant, entry: RespotConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    setup_spot_platform(hass, entry, async_add_entities, lambda hub, spot: [RespotNotify(hub, spot)])


class RespotNotify(RespotEntity, NotifyEntity):
    """notify.send_message → a pop-up with a chime on the Spot (it listens for respot_notify events)."""

    _attr_translation_key = "message"

    def __init__(self, hub, spot) -> None:
        super().__init__(hub, spot, "message")

    async def async_send_message(self, message: str, title: str | None = None) -> None:
        if not self._spot.online:
            raise HomeAssistantError("The Spot is offline; the message was not sent.")
        self.hass.bus.async_fire(EVENT_NOTIFY, {"spot_id": self._spot.spot_id, "message": message, "title": title})
