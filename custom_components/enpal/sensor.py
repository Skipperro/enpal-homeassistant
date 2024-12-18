"""Platform for sensor integration."""
from __future__ import annotations

import asyncio
import uuid
from datetime import timedelta, datetime, timezone
from homeassistant.components.sensor import (SensorEntity)
from homeassistant.core import HomeAssistant
from homeassistant import config_entries
from homeassistant.helpers.device_registry import DeviceEntryType
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_registry import async_get, async_entries_for_config_entry
from custom_components.enpal.const import DOMAIN
import aiohttp
import logging
from influxdb_client import InfluxDBClient

_LOGGER = logging.getLogger(__name__)
SCAN_INTERVAL = timedelta(seconds=120)

VERSION= '0.3.1'

def get_tables(ip: str, port: int, token: str):
    client = InfluxDBClient(url=f'http://{ip}:{port}', token=token, org='enpal')
    query_api = client.query_api()

    query = 'from(bucket: "solar") \
      |> range(start: -24h) \
      |> last()'

    tables = query_api.query(query)
    return tables


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
    if not 'enpal_host_ip' in config:
        _LOGGER.error("No enpal_host_ip in config entry")
        return
    if not 'enpal_host_port' in config:
        _LOGGER.error("No enpal_host_port in config entry")
        return
    if not 'enpal_token' in config:
        _LOGGER.error("No enpal_token in config entry")
        return
    
    global_config = hass.data[DOMAIN]

    tables = await hass.async_add_executor_job(get_tables, config['enpal_host_ip'], config['enpal_host_port'], config['enpal_token'])


    for table in tables:
        field = table.records[0].values['_field']
        measurement = table.records[0].values['_measurement']

        if measurement == "system" and field == "Power.Production.Total":
            to_add.append(EnpalSensor(field, measurement, 'mdi:solar-power', 'Enpal Solar Production Power', config['enpal_host_ip'], config['enpal_host_port'], config['enpal_token'], 'power', 'W'))
        if measurement == "system" and field == "Power.Consumption.Total":
            to_add.append(EnpalSensor(field, measurement, 'mdi:home-lightning-bolt', 'Enpal Power House Total', config['enpal_host_ip'], config['enpal_host_port'], config['enpal_token'], 'power', 'W'))
        if measurement == "system" and field == "Power.External.Total":
            to_add.append(EnpalSensor(field, measurement, 'mdi:home-lightning-bolt', 'Enpal Power External Total', config['enpal_host_ip'], config['enpal_host_port'], config['enpal_token'], 'power', 'W'))

        # Consum Total per Day
        if measurement == "system" and field == "Energy.Consumption.Total.Day":
            to_add.append(EnpalSensor(field, measurement, 'mdi:home-lightning-bolt', 'Enpal Energy Consumption Day', config['enpal_host_ip'], config['enpal_host_port'], config['enpal_token'], 'energy', 'kWh'))

        # to the Grid and from the Grid
        if measurement == "system" and field == "Energy.External.Total.Out.Day":
            to_add.append(EnpalSensor(field, measurement, 'mdi:transmission-tower-export', 'Enpal Energy External Out Day', config['enpal_host_ip'], config['enpal_host_port'], config['enpal_token'], 'energy', 'kWh'))
        if measurement == "system" and field == "Energy.External.Total.In.Day":
            to_add.append(EnpalSensor(field, measurement, 'mdi:transmission-tower-import', 'Enpal Energy External In Day', config['enpal_host_ip'], config['enpal_host_port'], config['enpal_token'], 'energy', 'kWh'))

        # Solar Energy.Production.Total.Day
        if measurement == "system" and field == "Energy.Production.Total.Day":
            to_add.append(EnpalSensor(field, measurement, 'mdi:solar-power-variant', 'Enpal Production Day', config['enpal_host_ip'], config['enpal_host_port'], config['enpal_token'], 'energy', 'kWh'))

        # Grid frequency
        if measurement == "inverter" and field == "Frequency.Grid":
            to_add.append(EnpalSensor(field, measurement, 'mdi:solar-power-variant', 'Enpal Grid Frequency', config['enpal_host_ip'], config['enpal_host_port'], config['enpal_token'], 'frequency', 'Hz'))

        # Inverter Temperature
        if measurement == "inverter" and field == "Temperature.Housing.Inside":
            to_add.append(EnpalSensor(field, measurement, 'mdi:solar-power-variant', 'Enpal Inverter Temperature', config['enpal_host_ip'], config['enpal_host_port'], config['enpal_token'], 'temperature', '°C'))

        # Power phases
        if measurement == "inverter" and field == "Voltage.Phase.A":
            to_add.append(EnpalSensor(field, measurement, 'mdi:lightning-bolt', 'Enpal Voltage Phase A', config['enpal_host_ip'], config['enpal_host_port'], config['enpal_token'], 'voltage', 'V'))
        if measurement == "inverter" and field == "Power.AC.Phase.A":
            to_add.append(EnpalSensor(field, measurement, 'mdi:lightning-bolt', 'Enpal AC Power Phase A', config['enpal_host_ip'], config['enpal_host_port'], config['enpal_token'], 'power', 'W'))
        if measurement == "inverter" and field == "Voltage.Phase.B":
            to_add.append(EnpalSensor(field, measurement, 'mdi:lightning-bolt', 'Enpal Voltage Phase B', config['enpal_host_ip'], config['enpal_host_port'], config['enpal_token'], 'voltage', 'V'))
        if measurement == "inverter" and field == "Power.AC.Phase.B":
            to_add.append(EnpalSensor(field, measurement, 'mdi:lightning-bolt', 'Enpal AC Power Phase B', config['enpal_host_ip'], config['enpal_host_port'], config['enpal_token'], 'power', 'W'))
        if measurement == "inverter" and field == "Voltage.Phase.C":
            to_add.append(EnpalSensor(field, measurement, 'mdi:lightning-bolt', 'Enpal Voltage Phase C', config['enpal_host_ip'], config['enpal_host_port'], config['enpal_token'], 'voltage', 'V'))
        if measurement == "inverter" and field == "Power.AC.Phase.C":
            to_add.append(EnpalSensor(field, measurement, 'mdi:lightning-bolt', 'Enpal AC Power Phase C', config['enpal_host_ip'], config['enpal_host_port'], config['enpal_token'], 'power', 'W'))

        # String #1
        if measurement == "inverter" and field == "Current.String.1":
            to_add.append(EnpalSensor(field, measurement, 'mdi:lightning-bolt', 'Current String 1', config['enpal_host_ip'], config['enpal_host_port'], config['enpal_token'], 'current', 'A'))
        if measurement == "inverter" and field == "Power.DC.String.1":
            to_add.append(EnpalSensor(field, measurement, 'mdi:lightning-bolt', 'Power String 1', config['enpal_host_ip'], config['enpal_host_port'], config['enpal_token'], 'power', 'W'))
        if measurement == "inverter" and field == "Voltage.String.1":
            to_add.append(EnpalSensor(field, measurement, 'mdi:lightning-bolt', 'Voltage String 1', config['enpal_host_ip'], config['enpal_host_port'], config['enpal_token'], 'voltage', 'V'))

        # String #2
        if measurement == "inverter" and field == "Current.String.2":
            to_add.append( EnpalSensor(field, measurement, 'mdi:lightning-bolt', 'Current String 2', config['enpal_host_ip'], config['enpal_host_port'], config['enpal_token'], 'current', 'A'))
        if measurement == "inverter" and field == "Power.DC.String.2":
            to_add.append(EnpalSensor(field, measurement, 'mdi:lightning-bolt', 'Power String 2', config['enpal_host_ip'], config['enpal_host_port'], config['enpal_token'], 'power', 'W'))
        if measurement == "inverter" and field == "Voltage.String.2":
            to_add.append(EnpalSensor(field, measurement, 'mdi:lightning-bolt', 'Voltage String 2', config['enpal_host_ip'], config['enpal_host_port'], config['enpal_token'], 'voltage', 'V'))

        # Battery
        if measurement == "system" and field == "Percent.Storage.Level":
            to_add.append(EnpalSensor(field, measurement, 'mdi:battery', 'Enpal Battery Percent', config['enpal_host_ip'], config['enpal_host_port'], config['enpal_token'], 'battery', '%'))
        if measurement == "system" and field == "Power.Storage.Total":
            to_add.append(EnpalSensor(field, measurement, 'mdi:battery-charging', 'Enpal Battery Power', config['enpal_host_ip'], config['enpal_host_port'], config['enpal_token'], 'power', 'W'))
        if measurement == "system" and field == "Energy.Storage.Total.In.Day":
            to_add.append(EnpalSensor(field, measurement, 'mdi:battery-arrow-up', 'Enpal Battery Charge Day', config['enpal_host_ip'], config['enpal_host_port'], config['enpal_token'], 'energy', 'kWh'))
        if measurement == "system" and field == "Energy.Storage.Total.Out.Day":
            to_add.append(EnpalSensor(field, measurement, 'mdi:battery-arrow-down', 'Enpal Battery Discharge Day', config['enpal_host_ip'], config['enpal_host_port'], config['enpal_token'], 'energy', 'kWh'))

        # Wallbox
        if measurement == "wallbox" and field == "State.Wallbox.Connector.1.Charge":
            to_add.append(EnpalSensor(field, measurement, 'mdi:ev-station', 'Wallbox Charge Percent', config['enpal_host_ip'], config['enpal_host_port'], config['enpal_token'], 'battery', '%'))
        if measurement == "wallbox" and field == "Power.Wallbox.Connector.1.Charging":
            to_add.append(EnpalSensor(field, measurement, 'mdi:ev-station', 'Wallbox Charging Power', config['enpal_host_ip'], config['enpal_host_port'], config['enpal_token'], 'power', 'W'))
        if measurement == "wallbox" and field == "Energy.Wallbox.Connector.1.Charged.Total":
            to_add.append(EnpalSensor(field, measurement, 'mdi:ev-station', 'Wallbox Charging Total', config['enpal_host_ip'], config['enpal_host_port'], config['enpal_token'], 'energy', 'Wh'))

    entity_registry = async_get(hass)
    entries = async_entries_for_config_entry(
        entity_registry, config_entry.entry_id
    )
    for entry in entries:
        entity_registry.async_remove(entry.entity_id)

    async_add_entities(to_add, update_before_add=True)


class EnpalSensor(SensorEntity):

    def __init__(self, field: str, measurement: str, icon:str, name: str, ip: str, port: int, token: str, device_class: str, unit: str):
        self.field = field
        self.measurement = measurement
        self.ip = ip
        self.port = port
        self.token = token
        self.enpal_device_class = device_class
        self.unit = unit
        self._attr_icon = icon
        self._attr_name = name
        self._attr_unique_id = f'enpal_{measurement}_{field}'
        self._attr_extra_state_attributes = {}


    async def async_update(self) -> None:

        # Get the IP address from the API
        try:
            client = InfluxDBClient(url=f'http://{self.ip}:{self.port}', token=self.token, org="enpal")
            query_api = client.query_api()

            query = f'from(bucket: "solar") \
              |> range(start: -15m) \
              |> filter(fn: (r) => r["_measurement"] == "{self.measurement}") \
              |> filter(fn: (r) => r["_field"] == "{self.field}") \
              |> aggregateWindow(every: 2m, fn: mean, createEmpty: true) \
              |> last()'

            tables = await self.hass.async_add_executor_job(query_api.query, query)

            value = 0
            if tables:
                value = tables[0].records[0].values['_value']

            # Sanity check for wallbox power - it should not be negative or greater than 30kW
            if self.field == 'Power.Wallbox.Connector.1.Charging':
                if value < 0 or value > 30000:
                    value = 0.0

            if self.field == 'Energy.Wallbox.Connector.1.Charged.Total':
                # Sanity check - value can't be lower than 1.0.
                # This is to prevent false readings that outputs 0 and restarts utility meters based on this sensor
                if value < 1.0:
                    return

            if self.field == 'Frequency.Grid':
                if value < 0 or value > 100:
                    return

            if self.field == 'Temperature.Housing.Inside':
                if value < -100 or value > 100:
                    return

            self._attr_native_value = round(float(value), 2)
            self._attr_device_class = self.enpal_device_class
            self._attr_native_unit_of_measurement	= self.unit
            self._attr_state_class = 'measurement'
            self._attr_extra_state_attributes['last_check'] = datetime.now()
            self._attr_extra_state_attributes['field'] = self.field
            self._attr_extra_state_attributes['measurement'] = self.measurement

            if self._attr_native_unit_of_measurement == "kWh":
                self._attr_extra_state_attributes['last_reset'] = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
                self._attr_state_class = 'total'
            if self._attr_native_unit_of_measurement == "Wh":
                self._attr_extra_state_attributes['last_reset'] = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
                self._attr_state_class = 'total'

            if self.field == 'Percent.Storage.Level':
                if self._attr_native_value < 10:
                    self._attr_icon = "mdi:battery-outline"
                if 19 >= self._attr_native_value >= 10:
                    self._attr_icon = "mdi:battery-10"
                if 29 >= self._attr_native_value >= 20:
                    self._attr_icon = "mdi:battery-20"
                if 39 >= self._attr_native_value >= 30:
                    self._attr_icon = "mdi:battery-30"
                if 49 >= self._attr_native_value >= 40:
                    self._attr_icon = "mdi:battery-40"
                if 59 >= self._attr_native_value >= 50:
                    self._attr_icon = "mdi:battery-50"    
                if 69 >= self._attr_native_value >= 60:
                    self._attr_icon = "mdi:battery-60"
                if 79 >= self._attr_native_value >= 70:
                    self._attr_icon = "mdi:battery-70"
                if 89 >= self._attr_native_value >= 80:
                    self._attr_icon = "mdi:battery-80"
                if 99 >= self._attr_native_value >= 90:
                    self._attr_icon = "mdi:battery-90"        
                if self._attr_native_value == 100:
                    self._attr_icon = "mdi:battery"
                
        except Exception as e:
            _LOGGER.error(f'{e}')
            self._state = 'Error'
            self._attr_native_value = None
            self._attr_extra_state_attributes['last_check'] = datetime.now()
