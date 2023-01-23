import requests

from model import InverterData


class Inverter:
    def __init__(self, ip):
        self.ip = ip

    def get_rt_power(self):
        r = requests.get('http://{}/solar_api/v1/GetPowerFlowRealtimeData.fcgi'.format(self.ip))
        response = r.json()

        data = InverterData()

        data.current_load = response['Body']['Data']['Site']['P_PV']
        data.max_load = 8000
        data.current_grid_power = round(max(0, response['Body']['Data']['Site']['P_Grid']), 2)
        data.current_solar_power = round(response['Body']['Data']['Site']['P_PV'], 2)
        data.current_load = round(response['Body']['Data']['Site']['P_Load'] * -1, 2)
        data.excess_solar = round(max(0, data.current_solar_power - data.current_load), 2)

        return data

    def get_ac_data(self):
        r = requests.get('http://{}/solar_api/v1/GetInverterRealtimeData.cgi?'
                         'Scope=Device&DataCollection=3PInverterData'.format(self.ip))
        response = r.json()
        ac_data = {
            'ac_1': {
                'c': response['Body']['Data']['IAC_L1']['Value'],
                'v': response['Body']['Data']['UAC_L1']['Value'],
            },
            'ac_2': {
                'c': response['Body']['Data']['IAC_L2']['Value'],
                'v': response['Body']['Data']['UAC_L2']['Value'],
            },
            'ac_3': {
                'c': response['Body']['Data']['IAC_L1']['Value'],
                'v': response['Body']['Data']['UAC_L3']['Value'],
            },
        }
        return ac_data

    def get_dc_data(self):
        r = requests.get('http://{}/solar_api/v1/GetInverterRealtimeData.cgi?'
                         'Scope=Device&DataCollection=CommonInverterData'.format(self.ip))
        response = r.json()
        dc_data = {
            'dc_1': {
                'c': response['Body']['Data']['IDC']['Value'],
                'v': response['Body']['Data']['UDC']['Value'],
            },
            'dc_2': {
                'c': response['Body']['Data']['IDC_2']['Value'],
                'v': response['Body']['Data']['UDC_2']['Value'],
            },
        }
        return dc_data

    def get_meter_data(self):
        r = requests.get('http://{}/solar_api/v1/GetMeterRealtimeData.cgi'.format(self.ip))
        response = r.json()
        meter_data = {
            'ac_1': {
                'c': response['Body']['Data']['0']['Current_AC_Phase_1'],
                'v': response['Body']['Data']['0']['Voltage_AC_Phase_1']
            },
            'ac_2': {
                'c': response['Body']['Data']['0']['Current_AC_Phase_2'],
                'v': response['Body']['Data']['0']['Voltage_AC_Phase_2']
            },
            'ac_3': {
                'c': response['Body']['Data']['0']['Current_AC_Phase_3'],
                'v': response['Body']['Data']['0']['Voltage_AC_Phase_3']
            }
        }
        return meter_data
