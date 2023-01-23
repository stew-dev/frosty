import uvicorn
from fastapi.staticfiles import StaticFiles
from starlette.responses import RedirectResponse

import tapo_service
import time_now
import time
from datetime import datetime, timedelta
from copy import copy
from typing import Optional

from api_utils import disable_security
from model import DeviceLoopConfig, AppConfig
from database import Database
from tapo_service import remove_tapo, turn_off_device, turn_on_device
from fastapi import FastAPI
from fastapi_utils.tasks import repeat_every

from model import Device
from inverter import Inverter

app_config = AppConfig()

api = FastAPI()
disable_security(api)

db = Database(app_config.db_ip)
inverter = Inverter(app_config.inverter_ip)

devices = dict()


@api.on_event("startup")
def startup():
    for device_dict in db.get_all('devices'):
        device = Device(device_dict)
        devices[device._id] = device
        tapo_service.initialise_tapo(device)


@api.on_event("startup")
@repeat_every(seconds=1)
def scheduler():
    optimise_power_use(DeviceLoopConfig(), devices=devices, data_loader=inverter.get_rt_power, suns_up=time_now.suns_up())


def optimise_power_use(config: DeviceLoopConfig, devices, data_loader, suns_up):
    max_priority_device: Optional[Device] = None
    min_priority_device: Optional[Device] = None
    inverter_rt_power_data = data_loader()
    grid_power = inverter_rt_power_data.current_grid_power
    excess_solar = inverter_rt_power_data.excess_solar

    print('suns up ? {}'.format(suns_up))

    if not suns_up:
        print('not sun up')
        return

    for device_id in devices:
        device = devices[device_id]
        last_switched_on = datetime.now() - device.last_updated
        # find highest priority device that is not already on, and is on Auto
        print(device.priority)
        if not device.is_on and not device.manual_control:
            if max_priority_device is None:
                max_priority_device = device
            if max_priority_device.priority > device.priority or \
                    (max_priority_device.priority == device.priority and max_priority_device.power > device.power):
                max_priority_device = device
        elif device.is_on and not device.manual_control and last_switched_on.total_seconds() > device.min_run_time:
            if min_priority_device is None:
                min_priority_device = device
            if min_priority_device.priority < device.priority or \
                    (min_priority_device.priority == device.priority and min_priority_device.power < device.power):
                min_priority_device = device

    min_priority_device and print('min = {}'.format(min_priority_device._id))
    max_priority_device and print('max = {}'.format(max_priority_device._id))

    if max_priority_device and excess_solar > max_priority_device.power:
        last_switched_on = datetime.now() - max_priority_device.last_updated

        if last_switched_on.total_seconds() < config.delay:
            print('switched on less than a {} secs ago'.format(config.delay))
            time.sleep(config.delay)
            return
        turn_on_device(devices[max_priority_device._id])

    if config.grid_power < grid_power and config.grid_power < min_priority_device.power:
        print('{} grid power maxed out'.format(grid_power))
        turn_off_device(devices[min_priority_device._id])


# Get the current information from the inverter

@api.get("/inverterInfo", tags=["inverter"])
async def current_inverter_info():
    return inverter.get_rt_power()


# Gets a list of devices, removes the tapo attribute is this is non-string able

@api.get("/devices/data", tags=["devices"])
async def get_devices():
    devices_copy = dict()
    for x in devices:
        device_copy = copy(devices[x])
        remove_tapo(device_copy)
        devices_copy[x] = device_copy
    return devices_copy


# Create a new device

@api.post("/device/create", tags=["devices"])
async def create_device(device_id, priority, power, ip_address, control="MANUAL"):
    new_device = Device()

    new_device.ip_address = ip_address
    new_device._id = device_id
    new_device.priority = int(priority)
    new_device.power = int(power)
    new_device.last_updated = datetime.now() - timedelta(seconds=60)
    new_device.manual_control = control

    db.insert('devices', [new_device.__dict__])
    devices[device_id] = new_device

    tapo_service.initialise_tapo(new_device)

    device_copy = copy(new_device)
    remove_tapo(device_copy)
    return device_copy


# Turn a device on/off

@api.post("/device/switch", tags=["devices"])
async def turn_on(data: dict):
    device = devices[data['_id']]
    tapo_service.set_manual(device, data['manual_control'])
    if data['is_on']:
        return turn_on_device(device)
    else:
        return turn_off_device(device)


@api.post("/device/control", tags=["devices"])
async def set_control(data: dict):
    device = devices[data['_id']]
    tapo_service.set_manual(device, data['manual_control'])


@api.get("/")
async def index():
    return RedirectResponse(url="/index.html")


api.mount("/", StaticFiles(directory="frontend/", html=True), name="ui")

if __name__ == "__main__":
    uvicorn.run("devices:api", host="0.0.0.0", port=8000, reload=True)
