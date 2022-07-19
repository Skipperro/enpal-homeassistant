"""Config flow for IP check integration."""
from __future__ import annotations
import logging
from typing import Any, Dict, Optional
import homeassistant.helpers.config_validation as cv
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback

from .const import DOMAIN

big_int = vol.All(vol.Coerce(int), vol.Range(min=300))

_LOGGER = logging.getLogger(__name__)
CONFIG_SCHEMA = vol.Schema(
            {
                vol.Required('check_ipv4', default=True): cv.boolean,
                vol.Required('check_ipv6', default=False): cv.boolean,
            }
        )

class CustomFlow(config_entries.ConfigFlow, domain=DOMAIN):
    data: Optional[Dict[str, Any]]

    async def async_step_user(self, user_input: Optional[Dict[str, Any]] = None):
        errors: Dict[str, str] = {}
        if user_input is not None:
            self.data = user_input
            if not self.data['check_ipv4'] and not self.data['check_ipv6']:
                errors['base'] = 'nothing_selected'
            if not errors:
                return self.async_create_entry(title="Ipify.org Public IP Check", data=self.data)

        return self.async_show_form(step_id="user", data_schema=CONFIG_SCHEMA, errors=errors)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Get the options flow for this handler."""
        return OptionsFlowHandler(config_entry)

class OptionsFlowHandler(config_entries.OptionsFlow):
    """Handles options flow for the component."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        errors: Dict[str, str] = {}

        if user_input is not None:
            self.data = user_input
            if not self.data['check_ipv4'] and not self.data['check_ipv6']:
                errors['base'] = 'nothing_selected'
            if not errors:
                return self.async_create_entry(title="Ipify.org Public IP Check", data={'check_ipv4': user_input['check_ipv4'], 'check_ipv6': user_input['check_ipv6']})

        default_ipv4 = True
        if 'check_ipv4' in self.config_entry.data:
            default_ipv4 = self.config_entry.data['check_ipv4']
        if 'check_ipv4' in self.config_entry.options:
            default_ipv4 = self.config_entry.options['check_ipv4']
        default_ipv6 = False
        if 'check_ipv6' in self.config_entry.data:
            default_ipv6 = self.config_entry.data['check_ipv6']
        if 'check_ipv6' in self.config_entry.options:
            default_ipv6 = self.config_entry.options['check_ipv6']

        OPTIONS_SCHEMA = vol.Schema(
            {
                vol.Required('check_ipv4', default=default_ipv4): cv.boolean,
                vol.Required('check_ipv6', default=default_ipv6): cv.boolean,
            }
        )
        return self.async_show_form(step_id="init", data_schema=OPTIONS_SCHEMA, errors=errors)
