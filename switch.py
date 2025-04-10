import os
from homeassistant.components.network import async_get_source_ip
from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    switches = [
            RelaySwitch(1, 121),
            RelaySwitch(2, 122),
            RelaySwitch(3, 125) ]
    async_add_entities(switches, True)


class RelaySwitch(SwitchEntity):
    _attr_has_entity_name = True

    def __init__(self, num, port) -> None:
        self._is_on = False
        self._attr_name = f'Relay {num}'
        self.port = port
        self._attr_unique_id = f'evolga_relay_{port}'

    async def async_added_to_hass(self):
        os.system(f'echo {self.port} > /sys/class/gpio/export')
        os.system(f'echo out > /sys/class/gpio/gpio{self.port}/direction')

    @property
    def is_on(self):
        return self._is_on

    def turn_on(self):
        self._is_on = 1
        os.system(f'echo 1 > /sys/class/gpio/gpio{self.port}/value')

    def turn_off(self):
        self._is_on = 0
        os.system(f'echo 0 > /sys/class/gpio/gpio{self.port}/value')

