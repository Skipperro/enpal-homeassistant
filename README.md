#  Ipify.org Public IP Check Integration

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)
[![GitHub release](https://img.shields.io/github/release/skipperro/ipify-homeassistant.svg)](https://GitHub.com/skipperro/ipify-homeassistant/releases/)
![](https://img.shields.io/badge/dynamic/json?color=41BDF5&logo=home-assistant&label=integration%20usage&suffix=%20installs&cacheSeconds=15600&url=https://analytics.home-assistant.io/custom_integrations.json&query=$.ipify.total)


This integration allows you to check the public IP of your Home Assistant instance.

This is useful if you want to check if your Home Assistant instance is accessible from the outside 
and can be used for automations like updating your DNS records after a new IP is assigned.

![ipify entity](images/publicipv4.png)

## How it works

Every 5 minutes the public IP is checked and if it changed, the integration will trigger a value change.

This value can be used in automation scripts or displayed on dashboards.

## Installation

1. Install this integration with HACS (adding repository required), or copy the contents of this
repository into the `custom_components/ipify` directory.
2. Restart Home Assistant.
3. Start the configuration flow:
   - [![Start Config Flow](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start?domain=ipify)
   - Or: Go to `Configuration` -> `Integrations` and click the `+ Add Integration`. Select `Ipify` from the list.
   - If the integration is not found try to refresh the HA page without using cache (Ctrl+F5).
4. Select which IP protocol versions (IPv4 and/or IPv6) you want to check.

![ipify config](images/ipconfig.png)

## ToDo

- Add extra parameter to allow custom interval for checking IP.
- Promote this integration to `HACS Default` and/or `HA Core`.

## Credits

- Randall Degges (https://github.com/rdegges): Ipify-api code hosted on ipify.org that allows this integration to work. 
- Skipperro: Creating the integration for Home Assistant.