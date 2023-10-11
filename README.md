#  Enpal - Home Assistant integration (WiP)


<img src="images/logo.png" alt="enpal logo" width="512">

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)
[![GitHub release](https://img.shields.io/github/release/skipperro/enpal-homeassistant.svg)](https://GitHub.com/skipperro/enpal-homeassistant/releases/)
![](https://img.shields.io/badge/dynamic/json?color=41BDF5&logo=home-assistant&label=integration%20usage&suffix=%20installs&cacheSeconds=15600&url=https://analytics.home-assistant.io/custom_integrations.json&query=$.enpal.total)

## Disclaimer

This integration is created with acknowledgement and limited support from Enpal GmbH, but __it's not official software from Enpal__.<br>
It's a custom integration created entirely by me (gickowtf) and Skipperro, and thus Enapl GmbH is not responsible for any damage/issues caused by this integration, nor it offers any end-user support for it.

It is still a work in progress and is not guaranteed to work 100% or even work at all.<br>


## Features

- **Inverter measurements**:
  - Solar Production Power
  - Power House Total
  - Power External Total'
  - Energy Consumption
  - Production Day
  - Inverter temperature.
  - Energy External Out Day
  - Energy External In Day
  - Voltage, Current, Power Phase A, B and C
- **Battery estimation**:
  - Battery Power
  - Battery Percent
  - Battery Charge Day
  - Battery Discharge Day
  - Battery Charge Total
  - Battery Disharge Total
- **WallBox**:
  - Wallbox Charge Percent
  - Wallbox Charging Power
  - Wallbox Charging Total

![enpal measurements](images/measurements.png)

## Installation

1. Install this integration with HACS (adding repository required), or copy the contents of this
repository into the `custom_components/enpal` directory.
2. Restart Home Assistant.
3. Start the configuration flow:
   - [![Start Config Flow](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start?domain=enpal)
   - Or: Go to `Configuration` -> `Integrations` and click the `+ Add Integration`. Select `Enpal` from the list.
   - If the integration is not found try to refresh the HA page without using cache (Ctrl+F5).
4. Input the IP, Port and access token for access InfluxDB server of your Enpal solar installation.

![enpal config](images/enpal-config.png)

## How to get access token?

Look at the Solar Rel Web Interface on your Local Network under Config!

or you can contact Enpal support.<br>

## Credits
 
- Skipperro: Creating the integration for Home Assistant.
- gickowtf: Creating the integrartion for Home Assistant with the new Enpal Solar Rel Web Interface
