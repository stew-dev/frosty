from datetime import datetime, timedelta

from devices import optimise_power_use
from model import DeviceLoopConfig, InverterData, Device
import unittest


class FakeTapo:
    on = False

    def turnOn(self):
        self.on = True

    def turnOff(self):
        self.on = False


class Test(unittest.TestCase):
    def test_repeater(self):
        config = DeviceLoopConfig()
        config.delay = 2
        config.sleep = 3
        config.grid_power = 100

        inverter_data = InverterData()
        inverter_data.excess_solar = 0
        inverter_data.current_grid_power = 0

        devices = dict({
            "KITCHEN_PATIO": Device(device_dict={
                "_id": "KITCHEN_PATIO",
                "tapo": FakeTapo(),
                "ip_address": '',
                "priority": 2,
                "power": 1000,
                "is_on": False,
                "last_updated": datetime.now() - timedelta(seconds=60),
                "manual_control": False,
                "min_run_time": 1
            }),
            "HOT_TUB": Device(device_dict={
                "_id": "HOT_TUB",
                "tapo": FakeTapo(),
                "ip_address": '',
                "priority": 1,
                "power": 2000,
                "is_on": False,
                "last_updated": datetime.now() - timedelta(seconds=60),
                "manual_control": False,
                "min_run_time": 300
            }),
        })

        optimise_power_use(config=config, devices=devices, data_loader=lambda: inverter_data, suns_up=True)

        inverter_data.excess_solar = 2000
        inverter_data.current_grid_power = 0

        optimise_power_use(config=config, devices=devices, data_loader=lambda: inverter_data, suns_up=True)

        self.assertTrue(devices['KITCHEN_PATIO'].tapo.on)
        self.assertTrue(devices['KITCHEN_PATIO'].is_on)
