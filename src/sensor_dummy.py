# sensor_dummy.py

import time
import random
from collections import OrderedDict
import state

def get_formatted_rtc():
    now = time.localtime()
    datum = "{:02d}.{:02d}.{:04d}".format(now[2], now[1], now[0])
    uhrzeit = "{:02d}:{:02d}:{:02d}".format(now[3], now[4], now[5])
    return datum, uhrzeit

def read_all():
    """Simuliert das Auslesen aller Sensorwerte. Rückgabe: Tuple (status_code, payload)"""
    try:
        datum, uhrzeit = get_formatted_rtc()

        payload = OrderedDict([
            ("date", datum),
            ("time", uhrzeit),
            ("temp", round(random.uniform(20.0, 25.0), 1)),
            ("druck", round(random.uniform(990.0, 1010.0), 1)),
            ("rlf", round(random.uniform(40.0, 60.0), 1)),
            ("lux", random.randint(300, 800)),
        ])
        return state.SUCCESS, payload
    except Exception as e:
        print("❌ Fehler im Dummy-Sensor:", e)
        return state.FATAL_ERROR, {}
