"""Platform for sensor integration."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, ClassVar

from homeassistant.components.event import (
    EventDeviceClass,
    EventEntity,
)
from homeassistant.components.mqtt.client import async_subscribe
from homeassistant.core import callback

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

if TYPE_CHECKING:
    from collections.abc import Callable

    from homeassistant.components.mqtt.models import ReceiveMessage
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback
    from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType


def setup_platform(
    hass: HomeAssistant,
    _: ConfigType,
    add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Set up the sensor platform."""
    # We only want this platform to be set up via discovery.
    if discovery_info is None:
        return

    config = hass.data[DOMAIN].get("doorbells", [])

    add_entities([IntegrationMQTTDoorbellEvent(hass, config) for config in config])


class IntegrationMQTTDoorbellEvent(EventEntity):
    """event class."""

    _attr_device_class = EventDeviceClass.DOORBELL
    _attr_event_types: ClassVar[list[str]] = ["ring"]
    _unsubscribe: Callable | None = None
    _topic: str

    def __init__(
        self,
        hass: HomeAssistant,
        config: ConfigType,
    ) -> None:
        """Initialize the event class."""
        super().__init__()
        self.hass = hass
        self._topic = config["topic"]
        self._attr_name = config.get("name", "MQTT Doorbell Event")

    @property
    def unique_id(self) -> str | None:
        """Return a unique ID."""
        if self._topic is None or self._attr_name is None:
            _LOGGER.error("unique_id: topic or name is None")
            return None

        return self._topic + self._attr_name + "_event"

    @callback
    def _async_handle_event(self, event: str) -> None:
        """Handle the demo button event."""
        self._trigger_event(event)
        self.async_write_ha_state()

    @callback
    async def _handle_ring(self, message: ReceiveMessage) -> None:
        """Handle ring."""
        payload = message.payload
        payload_str = (
            payload.decode("utf-8") if isinstance(payload, bytes) else str(payload)
        )

        is_ring = payload_str in ("1", "true")
        if is_ring:
            self._async_handle_event("ring")

    async def async_added_to_hass(self) -> None:
        """Register callbacks with your device API/library."""
        topic = self._topic
        self._unsubscribe = await async_subscribe(self.hass, topic, self._handle_ring)

    async def async_will_remove_from_hass(self) -> None:
        """Clean up when removed."""
        if self._unsubscribe:
            self._unsubscribe()
            self._unsubscribe = None
