"""State for all re-spot Spots known to this Home Assistant."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field, fields
from time import monotonic
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.dispatcher import async_dispatcher_send
from homeassistant.helpers.storage import Store

from .const import DOMAIN, ONLINE_TIMEOUT, SIGNAL_UPDATE

STORAGE_VERSION = 1
SAVE_DELAY = 5


@dataclass
class Spot:
    """One Spot and the settings Home Assistant controls on it."""

    spot_id: str
    name: str = "Echo Spot"
    faces: list[str] = field(default_factory=list)
    face: str | None = None
    screen: bool = True
    brightness: float = 100
    alarm_time: str = "07:00:00"
    alarm_on: bool = False
    rotate_on: bool = False
    last_message: str | None = None
    version: str | None = None
    last_seen: float = 0  # monotonic; not stored

    @property
    def online(self) -> bool:
        """True if the Spot reported recently."""
        return self.last_seen > 0 and monotonic() - self.last_seen < ONLINE_TIMEOUT


class RespotHub:
    """Keeps the Spots, persists their settings, and tells entities when something changed."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        self.hass = hass
        self.entry = entry
        self.spots: dict[str, Spot] = {}
        self._store: Store[dict[str, Any]] = Store(hass, STORAGE_VERSION, f"{DOMAIN}.spots")

    async def async_load(self) -> None:
        """Restore Spots from storage so their devices exist right after a restart."""
        data = await self._store.async_load() or {}
        names = {f.name for f in fields(Spot)} - {"last_seen"}
        for spot_id, saved in data.get("spots", {}).items():
            self.spots[spot_id] = Spot(**{k: v for k, v in saved.items() if k in names})

    @callback
    def _data(self) -> dict[str, Any]:
        out = {}
        for spot_id, spot in self.spots.items():
            saved = asdict(spot)
            saved.pop("last_seen", None)
            out[spot_id] = saved
        return {"spots": out}

    @callback
    def changed(self, spot: Spot, save: bool = True) -> None:
        """Persist (debounced) and refresh this Spot's entities."""
        if save:
            self._store.async_delay_save(self._data, SAVE_DELAY)
        async_dispatcher_send(self.hass, f"{SIGNAL_UPDATE}_{spot.spot_id}")

    @callback
    def remove(self, spot_id: str) -> None:
        """Forget a Spot (its device was deleted)."""
        self.spots.pop(spot_id, None)
        self._store.async_delay_save(self._data, SAVE_DELAY)
