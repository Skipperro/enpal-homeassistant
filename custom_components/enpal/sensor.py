"""Platform for sensor integration."""
from __future__ import annotations

import uuid
from datetime import timedelta, datetime
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

def get_tables(ip: str, port: int, token: str):
    client = InfluxDBClient(url=f'http://{ip}:{port}', token=token, org='my-new-org')
    query_api = client.query_api()

    query = 'from(bucket: "my-new-bucket") \
      |> range(start: -5m) \
      |> aggregateWindow(every: 2m, fn: last, createEmpty: false) \
      |> yield(name: "last")'

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

    tables = await hass.async_add_executor_job(get_tables, config['enpal_host_ip'], config['enpal_host_port'], config['enpal_token'])

    for table in tables:
        field = table.records[0].values['_field']
        measurement = table.records[0].values['_measurement']

        if measurement == "Gesamtleistung" and field == "Produktion":
            to_add.append(EnpalSensor(field, measurement, 'mdi:solar-power', 'Solar Production', config['enpal_host_ip'], config['enpal_host_port'], config['enpal_token'], 'power', 'W'))
        if measurement == "Gesamtleistung" and field == "Verbrauch":
            to_add.append(EnpalSensor(field, measurement, 'mdi:lightning-bolt', 'Power Consumption', config['enpal_host_ip'], config['enpal_host_port'], config['enpal_token'], 'power', 'W'))
        if measurement == "inverterTemperature" and field == "Temperature":
            to_add.append(EnpalSensor(field, measurement, 'mdi:thermometer', 'Inverter Temperature', config['enpal_host_ip'], config['enpal_host_port'], config['enpal_token'], 'temperature', '°C'))
        if measurement == "gridFrequency" and field == "Frequenz":
            to_add.append(EnpalSensor(field, measurement, 'mdi:lightning-bolt', 'Grid Frequency', config['enpal_host_ip'], config['enpal_host_port'], config['enpal_token'], 'frequency', 'Hz'))

        if measurement == "phasePowerAc" and field == "Phase1":
            to_add.append(EnpalSensor(field, measurement, 'mdi:lightning-bolt', 'AC Power Phase 1', config['enpal_host_ip'], config['enpal_host_port'], config['enpal_token'], 'power', 'W'))
        if measurement == "phasePowerAc" and field == "Phase2":
            to_add.append(EnpalSensor(field, measurement, 'mdi:lightning-bolt', 'AC Power Phase 2', config['enpal_host_ip'], config['enpal_host_port'], config['enpal_token'], 'power', 'W'))
        if measurement == "phasePowerAc" and field == "Phase3":
            to_add.append(EnpalSensor(field, measurement, 'mdi:lightning-bolt', 'AC Power Phase 3', config['enpal_host_ip'], config['enpal_host_port'], config['enpal_token'], 'power', 'W'))

        if measurement == "productionCurrentDc" and field == "String1":
            to_add.append(EnpalSensor(field, measurement, 'mdi:solar-power', 'DC Current String 1', config['enpal_host_ip'], config['enpal_host_port'], config['enpal_token'],'current', 'A'))
        if measurement == "productionCurrentDc" and field == "String2":
            to_add.append(EnpalSensor(field, measurement, 'mdi:solar-power', 'DC Current String 2', config['enpal_host_ip'], config['enpal_host_port'], config['enpal_token'],'current', 'A'))

        if measurement == "productionVoltageDc" and field == "String1":
            to_add.append(EnpalSensor(field, measurement, 'mdi:solar-power', 'DC Voltage String 1', config['enpal_host_ip'], config['enpal_host_port'], config['enpal_token'], 'voltage', 'V'))
        if measurement == "productionVoltageDc" and field == "String2":
            to_add.append(EnpalSensor(field, measurement, 'mdi:solar-power', 'DC Voltage String 2', config['enpal_host_ip'], config['enpal_host_port'], config['enpal_token'], 'voltage', 'V'))

    entity_registry = async_get(hass)
    entries = async_entries_for_config_entry(
        entity_registry, config_entry.entry_id
    )
    for entry in entries:
        entity_registry.async_remove(entry.entity_id)

    async_add_entities(to_add, update_before_add=True)

class EnpalSensor(SensorEntity):
    """Representation of a Sensor."""

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
        self._attr_unique_id = str(uuid.uuid4())
        self._attr_extra_state_attributes = {}

        self._attr_device_info = DeviceInfo(
            entry_type=DeviceEntryType.SERVICE,
            identifiers={(DOMAIN, 'enpal')},
            name="Enpal Solar Installation",
        )

    async def async_update(self) -> None:

        # Get the IP address from the API
        try:
            client = InfluxDBClient(url=f'http://{self.ip}:{self.port}', token=self.token, org="my-new-org")
            query_api = client.query_api()

            query = f'from(bucket: "my-new-bucket") \
              |> range(start: -5m) \
              |> filter(fn: (r) => r["_measurement"] == "{self.measurement}") \
              |> filter(fn: (r) => r["_field"] == "{self.field}") \
              |> aggregateWindow(every: 2m, fn: last, createEmpty: false) \
              |> yield(name: "last")'

            tables = await self.hass.async_add_executor_job(query_api.query, query)

            value = None
            if tables:
                value = tables[0].records[0].values['_value']
            self._attr_native_value = float(value)
            if self.measurement == 'productionCurrentDc' and self.unit == 'A':
                self._attr_native_value = float(value/1000)
            self._attr_device_class = self.enpal_device_class
            self._attr_native_unit_of_measurement	= self.unit
            self._attr_state_class = 'measurement'
            self._attr_extra_state_attributes['last_check'] = datetime.now()
            self._attr_extra_state_attributes['field'] = self.field
            self._attr_extra_state_attributes['measurement'] = self.measurement

        except Exception as e:
            _LOGGER.error(f'{e}')
            self._state = 'Error'
            self._attr_native_value = None
            self._attr_extra_state_attributes['last_check'] = datetime.now()