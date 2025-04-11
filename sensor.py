import aiofiles
import os
import subprocess
from homeassistant.components.network import async_get_source_ip
from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.core import callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import SENSOR
from datetime import timedelta

SCAN_INTERVAL = timedelta(seconds=1)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    sensors = [
            DINSensor(1, 123, "DIN 1"), 
            DINSensor(2, 120, "DIN 2"),
            DINSensor(3, 127, "DIN 3"),
            DINSensor(4, 124, "DIN 4"),
            DINSensor(5, 147, "FN") ]
    async_add_entities(sensors, True)


class DINSensor(SensorEntity):
    """A simple sensor."""
    _attr_has_entity_name = True

    def __init__(self, num, port, name) -> None:
        """Initialize the sensor."""
        self._attr_name = name
        self.num = num
        self.port = port
        self._attr_unique_id = f'evolga_in_{num}'
        self._scan_interval = 10
        self._attr_should_poll = True

    async def async_added_to_hass(self):
        ''' Check if pin is already exported, otherwise it could throw an error '''
        if os.path.isdir(f"/sys/class/gpio/gpio{self.port}") == False:
            async with aiofiles.open("/sys/class/gpio/export", "w") as file:
                file.write(self.port)
        ''' Now we should write direction of pin '''
        async with aiofiles.open(f"/sys/class/gpio/gpio{self.port}/direction", "w") as file:
            await file.write("in")

        # os.system(f'echo {self.port} > /sys/class/gpio/export')
        # os.system(f'echo in > /sys/class/gpio/gpio{self.port}/direction')

    
    @property
    def should_poll(self):
        return True


    @property
    def scan_interval(self):
        return self._scan_inverval


    async def async_update(self) -> None:
        ''' Idk how to work with python, let's just ckeck if directory exists '''
        if os.path.isdir(f"/sys/class/gpio/gpio{self.port}") == False:
            async with aiofiles.open("/sys/class/gpio/export", "w") as file:
                await file.write(f"{self.port}")

        ''' Now just open file and read '''
        res = ""
        async with aiofiles.open(f"/sys/class/gpio/gpio{self.port}/value", "r") as file:
            res = await file.read()
        
        self._attr_native_value = int(res) ^ 1 #invert state
