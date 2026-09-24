"""Connected status for a Rondel Spot."""

from __future__ import annotations

from homeassistant.components.binary_sensor import BinarySensorDeviceClass, BinarySensorEntity
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import RondelConfigEntry
from .entity import RondelEntity, setup_spot_platform


async def async_setup_entry(hass: HomeAssistant, entry: RondelConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    setup_spot_platform(hass, entry, async_add_entities, lambda hub, spot: [RondelConnected(hub, spot)])


class RondelConnected(RondelEntity, BinarySensorEntity):
    """On while the Spot keeps reporting (it checks in every minute)."""

    _attr_translation_key = "connected"
    _attr_device_class = BinarySensorDeviceClass.CONNECTIVITY
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, hub, spot) -> None:
        super().__init__(hub, spot, "connected")

    @property
    def is_on(self) -> bool:
        return self._spot.online
