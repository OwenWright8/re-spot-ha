"""Constants for the Rondel integration."""

from homeassistant.const import Platform

DOMAIN = "rondel"

PLATFORMS = [
    Platform.BINARY_SENSOR,
    Platform.EVENT,
    Platform.NOTIFY,
    Platform.NUMBER,
    Platform.SELECT,
    Platform.SENSOR,
    Platform.SWITCH,
    Platform.TIME,
]

# Dispatcher signals
SIGNAL_NEW_SPOT = f"{DOMAIN}_new_spot"
SIGNAL_UPDATE = f"{DOMAIN}_update"  # + "_<spot_id>"
SIGNAL_EVENT = f"{DOMAIN}_event"  # + "_<spot_id>_<button|alarm>"

# Fired on the event bus for the Spot to pick up (it subscribes over the websocket API).
EVENT_NOTIFY = f"{DOMAIN}_notify"

# A Spot reports at least every minute while connected.
ONLINE_TIMEOUT = 150  # seconds

# Controls the Spot follows: key -> platform. Unique ids are "<spot_id>_<key>".
CONTROL_ENTITIES = {
    "face": "select",
    "screen": "switch",
    "brightness": "number",
    "alarm_time": "time",
    "alarm_on": "switch",
}

BUTTON_EVENT_TYPES = ["single", "double", "hold"]
ALARM_EVENT_TYPES = ["sunrise", "ringing", "dismissed", "timeout", "cancelled"]
