"""The mqtt_doorbell component."""

from __future__ import annotations

from typing import TYPE_CHECKING

import voluptuous as vol
from homeassistant.components.mqtt.util import valid_subscribe_topic
from homeassistant.helpers.discovery import load_platform

from .const import DOMAIN, TOPIC

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.typing import ConfigType

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Required("doorbells"): [
                    vol.Schema(
                        {
                            vol.Required(TOPIC): valid_subscribe_topic,
                            vol.Optional("name"): str,
                        }
                    )
                ]
            }
        )
    },
    extra=vol.ALLOW_EXTRA,
)


def setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Your controller/hub specific code."""
    # Data that you want to share with your platforms
    hass.data[DOMAIN] = config[DOMAIN]

    load_platform(hass, "event", DOMAIN, {}, config)

    return True
