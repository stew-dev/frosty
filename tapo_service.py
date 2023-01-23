from PyP100 import PyP100
import os


def initialise_tapo(device):
    try:
        device.tapo = PyP100.P100(device.ip_address, os.getenv("tapo_user"), os.getenv("tapo_password"))
        device.tapo.handshake()  # Creates the cookies required for further methods
        device.tapo.login()  # Sends credentials to the plug and creates AES Key and IV for further methods
        device.is_on = device.tapo.getDeviceInfo()["result"]["device_on"]
    except Exception as e:
        print(e)


def remove_tapo(device_copy):
    if hasattr(device_copy, "tapo"):
        del device_copy.tapo


def turn_on_device(device):
    device.tapo.turnOn()
    device.is_on = True
    return device.is_on


def turn_off_device(device):
    device.tapo.turnOff()
    device.is_on = False
    return device.is_on


def set_manual(device, manual_control):
    device.manual_control = manual_control
