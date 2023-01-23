import datetime
from suntime import Sun
from datetime import datetime, timezone

import time


def datetime_from_utc_to_local(utc_datetime):
    now_timestamp = time.time()
    offset = datetime.fromtimestamp(now_timestamp) - datetime.utcfromtimestamp(now_timestamp)
    return utc_datetime + offset


latitude = 37.31
longitude = -8.58

sun = Sun(latitude, longitude)


def suns_up():
    today_sr = datetime_from_utc_to_local(sun.get_sunrise_time())
    today_ss = sun.get_sunset_time()
    current_time = datetime.now().replace(tzinfo=timezone.utc)
    if today_ss > current_time > today_sr:
        return True
    else:
        return False
