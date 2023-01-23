from datetime import datetime, timedelta


class AppConfig:
    db_ip = '192.168.5.32'
    inverter_ip = '192.168.5.100'


class DeviceLoopConfig:
    delay = 20
    sleep = 60
    grid_power = 100


class Device:
    _id = id
    tapo = None
    ip_address = ''
    priority = 1
    power = 1000
    is_on = False
    last_updated = datetime.now() - timedelta(seconds=60)
    manual_control = False
    min_run_time = 60

    def __init__(self, device_dict=None):
        if device_dict is not None:
            self._id = device_dict['_id']
            # self.tapo = device_dict['tapo']
            self.ip_address = device_dict['ip_address']
            self.priority = device_dict['priority']
            self.power = device_dict['power']
            self.manual_control = device_dict['manual_control']
            self.min_run_time = device_dict['min_run_time']


class InverterData:
    current_load = 0
    max_load = 0
    current_grid_power = 0
    current_solar_power = 0
    excess_solar = current_solar_power - current_grid_power
    load = 0
