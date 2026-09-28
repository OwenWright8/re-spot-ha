# re-spot for Home Assistant

Every Echo Spot (2017) running [re-spot](https://re-spot.org) shows up in Home Assistant as its own device, with all of its settings on one page.

| Entity | What it does |
| --- | --- |
| **Face** (select) | The face on screen. Change it from HA, or swipe on the Spot and it updates here. |
| **Screen** (switch) | Screen on/off. |
| **Brightness** (number) | Backlight brightness, 5–100 %. |
| **Alarm time** (time) / **Alarm** (switch) | The Spot's daily sunrise alarm. |
| **Auto-rotate** (switch) | Cycle through faces on its own, every so often (interval and which faces are set on the website). |
| **Sleep sound** (select) | Play Rainforest, Ocean or Thunderstorm, or Off. Switches the Spot to that face and starts/stops it. |
| **Sleep timer** (number) | Minutes left on whichever sleep sound is playing; 0 means no timer. Only does something while a sound is actually playing. |
| **Top button** (event) | `single`, `double` and `hold` presses of the Spot's top button. Use it to trigger automations. |
| **Alarm** (event) | `sunrise`, `ringing`, `dismissed`, `timeout`, `cancelled`. |
| **Last message** (sensor) | The latest icon a connected friend's Spot sent. |
| **Message** (notify) | `notify.send_message` shows a pop-up with a chime on the Spot. |
| **Connected** (binary sensor) | Whether the Spot has checked in during the last few minutes. |

## Install

1. In HACS, open **⋮ → Custom repositories**. Add `https://github.com/OwenWright8/re-spot-ha` with type **Integration**.
2. Search HACS for **re-spot**, download it, then restart Home Assistant.
3. Go to **Settings → Devices & services → Add integration → re-spot**.
4. On each Spot, hold the screen to open Settings and connect it to Home Assistant with a URL and a long-lived token. The Spot finds the integration and registers itself. Its device appears within a few seconds.

Any user's long-lived token works; it doesn't need to be an admin's. Older re-spot versions created `input_*` helpers such as `input_select.echo_spot_face`. Those are no longer used and can be deleted under **Settings → Devices & services → Helpers**.

## How it works

The Spot already keeps a websocket connection to Home Assistant for its Home dial, so nothing new connects to the Spot. The Spot calls `respot.report` to register, and then once a minute to check in and to report button presses, alarm stages and messages. The response tells the Spot which entities are its controls. It follows their state and sets them when you change something on the Spot. `notify` messages reach it as `respot_notify` events.

## Examples

```yaml
# Night face at 10 pm
- trigger: { trigger: time, at: "22:00:00" }
  action:
    - action: select.select_option
      target: { entity_id: select.bedroom_spot_face }
      data: { option: Night }

# Top button pressed twice → all lights off
- trigger: { trigger: state, entity_id: event.bedroom_spot_top_button }
  condition: "{{ trigger.to_state.attributes.event_type == 'double' }}"
  action:
    - action: light.turn_off
      target: { entity_id: all }

# Message on the screen
- action: notify.send_message
  target: { entity_id: notify.bedroom_spot_message }
  data: { title: Laundry, message: The dryer is done }

# Play Rainforest with a 45-minute sleep timer, from a bedtime routine
- action: select.select_option
  target: { entity_id: select.bedroom_spot_sleep_sound }
  data: { option: Rainforest }
- action: number.set_value
  target: { entity_id: number.bedroom_spot_sleep_timer }
  data: { value: 45 }
```
