# sensors.py – Sensorinitialisierung und Auslesung

from machine import Pin, I2C
from veml7700_driver import VEML7700
from bme280_driver import BME280
import time
from collections import OrderedDict
import state
import config

veml = None
bme = None

# --- Sensor-Versorgung aktivieren ---
veml_power = Pin(config.VEML_PWR, Pin.OUT)
veml_power.value(1)

bme_power = Pin(config.BME_PWR, Pin.OUT)
bme_power.value(1)

# --- I2C-Initialisierung ---
i2c_veml = I2C(0, scl=Pin(config.VEML_SCL), sda=Pin(config.VEML_SDA))
i2c_bme = I2C(1, scl=Pin(config.BME_SCL), sda=Pin(config.BME_SDA))

# --- Initialisierung VEML7700 ---
def init_veml():
    global veml
    try:
        veml = VEML7700(i2c=i2c_veml)
        print("📷 VEML7700 initialisiert.")
        return state.SUCCESS
    except Exception as e:
        print("❌ VEML7700 Fehler bei Init:", e)
        return state.FATAL_ERROR

def reset_veml():
    print("🔄 VEML7700 wird neu gestartet...")
    veml_power.value(0)
    time.sleep(0.2)
    veml_power.value(1)
    time.sleep(0.2)
    return init_veml()

def read_veml():
    global veml
    try:
        if veml is None:
            if init_veml() != state.SUCCESS:
                return state.FATAL_ERROR, {}
        lux = veml.read_lux()
        if not isinstance(lux, (int, float)) or lux < 0:
            return state.FATAL_ERROR, {}
        return state.SUCCESS, lux
    except Exception as e:
        print("❌ VEML7700 Fehler beim Lesen:", e)
        return state.FATAL_ERROR, {}

# --- Initialisierung BME280 ---
def init_bme():
    global bme
    try:
        bme = BME280(i2c=i2c_bme, address=config.BME280_ADDRESS)
        print("🌡️ BME280 initialisiert.")
        return state.SUCCESS
    except Exception as e:
        print("❌ BME280 Fehler bei Init:", e)
        return state.FATAL_ERROR

def read_bme():
    global bme
    try:
        if bme is None:
            if init_bme() != state.SUCCESS:
                return state.FATAL_ERROR, {}
        temp, druck, rlf = bme.read_compensated_data()
        return state.SUCCESS, {
            "temp": round(temp, 1),
            "druck": round(druck, 1),
            "rlf": round(rlf, 1)
        }
    except Exception as e:
        print("❌ BME280 Fehler beim Lesen:", e)
        return state.FATAL_ERROR, {}

# --- RTC-Zeit holen ---
def get_formatted_rtc():
    now = time.localtime()
    datum = "{:02d}.{:02d}.{:04d}".format(now[2], now[1], now[0])
    uhrzeit = "{:02d}:{:02d}:{:02d}".format(now[3], now[4], now[5])
    return datum, uhrzeit

# --- Gesamtsensor-Auslesung ---
def read_all():
    datum, uhrzeit = get_formatted_rtc()

    status_lux, lux = read_veml()
    if status_lux != state.SUCCESS:
        return state.FATAL_ERROR, {}

    status_bme, bme_data = read_bme()
    if status_bme != state.SUCCESS:
        return state.FATAL_ERROR, {}

    payload = OrderedDict([
        ("date", datum),
        ("time", uhrzeit),
        ("temp", bme_data["temp"]),
        ("druck", bme_data["druck"]),
        ("rlf", bme_data["rlf"]),
        ("lux", lux)
    ])

    return state.SUCCESS, payload
