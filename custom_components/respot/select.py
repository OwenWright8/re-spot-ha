"""Face selector for a re-spot Spot."""

from __future__ import annotations

from homeassistant.components.select import SelectEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import RespotConfigEntry
from .entity import RespotEntity, setup_spot_platform


async def async_setup_entry(hass: HomeAssistant, entry: RespotConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    setup_spot_platform(hass, entry, async_add_entities, lambda hub, spot: [RespotFaceSelect(hub, spot)])


class RespotFaceSelect(RespotEntity, SelectEntity):
    """The face on screen, limited to the faces chosen for this Spot on the re-spot website.

    The Spot follows this entity and reports swipes through it.
    """

    _attr_translation_key = "face"
    _attr_icon = "mdi:clock-outline"

    def __init__(self, hub, spot) -> None:
        super().__init__(hub, spot, "face")

    @property
    def options(self) -> list[str]:
        return self._spot.faces or ([self._spot.face] if self._spot.face else ["Digital"])

    @property
    def current_option(self) -> str | None:
        return self._spot.face if self._spot.face in self.options else None

    async def async_select_option(self, option: str) -> None:
        self._spot.face = option
        self._hub.changed(self._spot)
