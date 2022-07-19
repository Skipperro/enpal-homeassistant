"""Platform for sensor integration."""
from __future__ import annotations

import uuid
from datetime import timedelta, datetime
from homeassistant.components.sensor import (SensorEntity)
from homeassistant.core import HomeAssistant
from homeassistant import config_entries
from homeassistant.helpers.entity_registry import async_get, async_entries_for_config_entry
from custom_components.enpal.const import DOMAIN
import aiohttp
import logging

_LOGGER = logging.getLogger(__name__)
SCAN_INTERVAL = timedelta(seconds=300)


def validate_ipv4(s: str):
    # IPv4 address is a string of 4 numbers separated by dots
    a = s.split('.')
    if len(a) != 4:
        return False
    for x in a:
        if not x.isdigit():
            return False
        i = int(x)
        if i < 0 or i > 255:
            return False
    return True

def validate_ipv6(s: str):
    # IPv6 address is a string of at least 5 strings separated by colons
    a = s.split(':')
    if len(a) < 5:
        return False
    allowed = []
    for x in range(10):
        allowed.append(str(x)) # 0-9
    for x in range(97, 103):
        allowed.append(chr(x)) # a-f

    #if any element of a is longer than 4 characters, it is not a valid ipv6 address
    for x in a:
        if len(x) > 4:
            return False

    # if any element of 'a' contains not allowed character return false
    for x in a:
        for c in x:
            if c not in allowed:
                return False
    return True

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: config_entries.ConfigEntry,
    async_add_entities,
):
    # Get the config entry for the integration
    config = hass.data[DOMAIN][config_entry.entry_id]
    if config_entry.options:
        config.update(config_entry.options)
    to_add = []
    if 'check_ipv4' in config:
        if config['check_ipv4']:
            to_add.append(IPSensor(False))
    if 'check_ipv6' in config:
        if config['check_ipv6']:
            to_add.append(IPSensor(True))

    entity_registry = async_get(hass)
    entries = async_entries_for_config_entry(
        entity_registry, config_entry.entry_id
    )
    for entry in entries:
        entity_registry.async_remove(entry.entity_id)

    async_add_entities(to_add, update_before_add=True)

class IPSensor(SensorEntity):
    """Representation of a Sensor."""

    def __init__(self, ipv6: bool):
        self.ipv6 = ipv6
        self._attr_icon = 'mdi:web'
        self._attr_name = "Public IPv4"
        self._attr_unique_id = str(uuid.uuid4())
        self._attr_extra_state_attributes = {}
        if (self.ipv6):
            self._attr_name = "Public IPv6"
            self._attr_unique_id = str(uuid.uuid4())

    async def async_update(self) -> None:
        """Fetch new state data for the sensor."""
        if (self.ipv6):
            url = 'https://api64.ipify.org/?format=json'
        else:
            url = 'https://api.ipify.org/?format=json'

        # Get the IP address from the API
        try:
            starttime = datetime.now()
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    self._attr_extra_state_attributes['response_time_ms'] = (datetime.now() - starttime).microseconds//1000
                    self._attr_extra_state_attributes['status_code'] = response.status
                    self._attr_extra_state_attributes['last_check'] = datetime.now()
                    if response.status == 200:
                        data = await response.json()
                        self._attr_extra_state_attributes['data'] = data
                        if not 'ip' in data:
                            self._attr_native_value = None
                            _LOGGER.warning(f"No IP address in response: {data}")
                            return
                        ip = data['ip']
                        self._state = None
                        self._attr_native_value = None
                        if (self.ipv6):
                            if validate_ipv6(ip):
                                self._attr_native_value = ip
                        else:
                            if validate_ipv4(ip):
                                self._attr_native_value = ip
                    else:
                        self._state = "Error"
                        self._attr_extra_state_attributes['data'] = None
                        _LOGGER.error(f"Error {response.status} while getting IP")
        except Exception as e:
            _LOGGER.error(f'{e}')
            self._state = 'Error'
            self._attr_native_value = None
            self._attr_extra_state_attributes['response_time_ms'] = None
            self._attr_extra_state_attributes['status_code'] = None
            self._attr_extra_state_attributes['last_check'] = datetime.now()