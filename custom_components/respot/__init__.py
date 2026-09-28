"""re-spot: Echo Spots running the re-spot player appear as devices with their settings.

The Spot keeps its own websocket connection to Home Assistant (as it does for its Home dial).
It calls ``respot.report`` to register, to send a heartbeat, and to report button/alarm events and
messages; the response tells it which entities are its controls. From then on it follows those
entities' state changes (face, screen, brightness, alarm, auto-rotate, sleep sound + its timer), and
changes made on the Spot are sent back through the entities' normal services. Nothing here connects
to the Spot directly.
"""

from __future__ import annotations

from datetime import timedelta
from time import monotonic

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall, ServiceResponse, SupportsResponse, callback
from homeassistant.helpers import config_validation as cv, device_registry as dr, entity_registry as er
from homeassistant.helpers.device_registry import DeviceEntry
from homeassistant.helpers.dispatcher import async_dispatcher_send
from homeassistant.helpers.event import async_track_time_interval

from .const import CONTROL_ENTITIES, DOMAIN, PLATFORMS, SIGNAL_EVENT, SIGNAL_NEW_SPOT, SOUND_OPTIONS
from .hub import RespotHub, Spot

type RespotConfigEntry = ConfigEntry[RespotHub]

REPORT_SCHEMA = vol.Schema(
    {
        vol.Required("spot_id"): vol.All(cv.string, vol.Match(r"^[a-f0-9]{8,32}$")),
        vol.Optional("name"): vol.All(cv.string, vol.Length(max=40)),
        vol.Optional("faces"): vol.All(cv.ensure_list, [cv.string]),
        vol.Optional("version"): cv.string,
        # Starting values, only used the first time a Spot registers.
        vol.Optional("init"): vol.Schema(
            {
                vol.Optional("face"): cv.string,
                vol.Optional("screen"): cv.boolean,
                vol.Optional("brightness"): vol.All(vol.Coerce(float), vol.Range(min=5, max=100)),
                vol.Optional("alarm_time"): cv.string,
                vol.Optional("alarm_on"): cv.boolean,
                vol.Optional("rotate_on"): cv.boolean,
                vol.Optional("sound"): vol.In(SOUND_OPTIONS),
                vol.Optional("sleep_timer"): vol.All(vol.Coerce(float), vol.Range(min=0, max=120)),
            },
            extra=vol.REMOVE_EXTRA,
        ),
        vol.Optional("message"): vol.All(cv.string, vol.Length(max=120)),
        vol.Optional("event"): vol.Schema(
            {
                vol.Required("entity"): vol.In(["button", "alarm"]),
                vol.Required("type"): cv.string,
                vol.Optional("data"): dict,
            }
        ),
    },
    extra=vol.REMOVE_EXTRA,
)


async def async_setup_entry(hass: HomeAssistant, entry: RespotConfigEntry) -> bool:
    """Set up re-spot from its (single) config entry."""
    hub = RespotHub(hass, entry)
    await hub.async_load()
    entry.runtime_data = hub

    async def report(call: ServiceCall) -> ServiceResponse:
        data = call.data
        spot_id = data["spot_id"]
        spot = hub.spots.get(spot_id)
        is_new = spot is None
        if is_new:
            init = data.get("init", {})
            spot = Spot(
                spot_id=spot_id,
                name=data.get("name") or "Echo Spot",
                faces=list(data.get("faces", [])),
                face=init.get("face"),
                screen=init.get("screen", True),
                brightness=init.get("brightness", 100),
                alarm_time=init.get("alarm_time", "07:00:00"),
                alarm_on=init.get("alarm_on", False),
                rotate_on=init.get("rotate_on", False),
                sound=init.get("sound", "Off"),
                sleep_timer=init.get("sleep_timer", 0),
            )
        else:
            if data.get("faces"):
                spot.faces = list(data["faces"])
            if data.get("name") and data["name"] != spot.name:
                spot.name = data["name"]
                devices = dr.async_get(hass)
                if device := devices.async_get_device(identifiers={(DOMAIN, spot_id)}):
                    devices.async_update_device(device.id, name=spot.name)
        spot.last_seen = monotonic()
        if "version" in data:
            spot.version = data["version"]
        if "message" in data:
            spot.last_message = data["message"]

        if is_new:
            # Only now, so a failure above can't leave a Spot without entities.
            hub.spots[spot_id] = spot
            async_dispatcher_send(hass, SIGNAL_NEW_SPOT, spot)
        hub.changed(spot)
        if event := data.get("event"):
            async_dispatcher_send(hass, f"{SIGNAL_EVENT}_{spot_id}_{event['entity']}", event["type"], event.get("data") or {})

        # Tell the Spot which entities to follow. Right after registering they may not exist yet;
        # the Spot asks again shortly if any are missing.
        registry = er.async_get(hass)
        entities = {
            key: registry.async_get_entity_id(platform, DOMAIN, f"{spot_id}_{key}")
            for key, platform in CONTROL_ENTITIES.items()
        }
        return {"entities": entities, "new": is_new}

    hass.services.async_register(DOMAIN, "report", report, schema=REPORT_SCHEMA, supports_response=SupportsResponse.OPTIONAL)

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    @callback
    def refresh_online(_now) -> None:
        # "Connected" turns off when a Spot stops reporting.
        for spot in hub.spots.values():
            hub.changed(spot, save=False)

    entry.async_on_unload(async_track_time_interval(hass, refresh_online, timedelta(seconds=30)))
    return True


async def async_unload_entry(hass: HomeAssistant, entry: RespotConfigEntry) -> bool:
    """Unload the config entry."""
    hass.services.async_remove(DOMAIN, "report")
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def async_remove_config_entry_device(hass: HomeAssistant, entry: RespotConfigEntry, device: DeviceEntry) -> bool:
    """Allow deleting a Spot's device; it comes back if that Spot reports again."""
    for domain, spot_id in device.identifiers:
        if domain == DOMAIN:
            entry.runtime_data.remove(spot_id)
    return True
