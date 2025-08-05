# sensors.py – Sensorlogik für BME280 und VEML7700 / Sensor logic for BME280 and VEML7700

from veml7700_driver import VEML7700
from bme280_driver import BME280
from machine import Pin, I2C
import time
import config
import state
import random
from collections import OrderedDict

veml = None
bme = None
veml_initialized = False
bme_initialized = False

# --- Sensorstrom aktivieren / Activate sensor power ---
def power_on():
    if hasattr(config, "VEML_PWR"):
        Pin(config.VEML_PWR, Pin.OUT).on()
    if hasattr(config, "BME_PWR"):
        Pin(config.BME_PWR, Pin.OUT).on()
    time.sleep(0.2)

# --- Sensorstrom deaktivieren / Deactivate sensor power ---
def power_off():
    if hasattr(config, "VEML_PWR"):
        Pin(config.VEML_PWR, Pin.OUT).off()
    if hasattr(config, "BME_PWR"):
        Pin(config.BME_PWR, Pin.OUT).off()

# --- Sensorinitialisierung / Sensor initialization ---
def init_sensors():
    global veml, bme, veml_initialized, bme_initialized

    if config.VEML_MODE == "off" and config.BME_MODE == "off":
        return state.SUCCESS  # nichts zu tun / nothing to do

    power_on()

    if config.VEML_MODE == "active":
        try:
            veml_i2c = I2C(0, sda=Pin(config.VEML_SDA), scl=Pin(config.VEML_SCL))
            veml = VEML7700(veml_i2c)
            veml_initialized = True
            print("📷 VEML7700 initialisiert / VEML7700 initialized.")
        except Exception as e:
            print("❌ VEML7700 Fehler / Error:", e)
            veml = None
            veml_initialized = False

    if config.BME_MODE == "active":
        try:
            bme_i2c = I2C(1, sda=Pin(config.BME_SDA), scl=Pin(config.BME_SCL))
            bme = BME280(i2c=bme_i2c)
            bme_initialized = True
            print("🌡️ BME280 initialisiert / BME280 initialized.")
        except Exception as e:
            print("❌ BME280 Fehler / Error:", e)
            bme = None
            bme_initialized = False

    return state.SUCCESS

# --- RTC-Zeit holen / Get RTC time ---
def get_formatted_rtc():
    now = time.localtime()
    datum = "{:02d}.{:02d}.{:04d}".format(now[2], now[1], now[0])
    uhrzeit = "{:02d}:{:02d}:{:02d}".format(now[3], now[4], now[5])
    return datum, uhrzeit

# --- Hilfsfunktion: Payload bauen nach config / Helper: Build payload from config ---
def build_payload(data):
    fields = getattr(config, "MQTT_PAYLOAD_FIELDS", None)
    if fields:
        payload = OrderedDict()
        for field in fields:
            payload[field] = data.get(field, None)
        missing = [f for f in fields if f not in data]
        if missing:
            print("⚠️ MQTT_PAYLOAD_FIELDS enthält unbekannte Felder / contains unknown fields:", missing)
        return payload
    return OrderedDict(data)  # fallback

# --- Gesamtsensor-Auslesung / Full sensor reading ---
def read_all():
    datum, uhrzeit = get_formatted_rtc()
    data = {"date": datum, "time": uhrzeit}

    # Lux-Wert lesen / Read lux
    if config.VEML_MODE == "active" and veml_initialized:
        try:
            data["lux"] = veml.read_lux()
        except:
            data["lux"] = None
    elif config.VEML_MODE == "dummy":
        data["lux"] = random.randint(100, 2000)
    else:
        data["lux"] = None

    # BME-Werte lesen / Read BME values
    if config.BME_MODE == "active" and bme_initialized:
        try:
            temp, pressure, humidity = bme.read_compensated_data()
            data["temp"] = round(temp, 1)
            data["pressure"] = round(pressure / 100, 1)
            data["humidity"] = round(humidity, 1)
        except:
            data["temp"] = None
            data["pressure"] = None
            data["humidity"] = None
    elif config.BME_MODE == "dummy":
        data["temp"] = round(random.uniform(18.0, 32.0), 1)
        data["pressure"] = round(random.uniform(980.0, 1020.0), 1)
        data["humidity"] = round(random.uniform(30.0, 60.0), 1)
    else:
        data["temp"] = None
        data["pressure"] = None
        data["humidity"] = None

    return state.SUCCESS, build_payload(data)

# --- VEML Reset über GPIO / VEML reset via GPIO ---
def veml_reset():
    if hasattr(config, "VEML_PWR"):
        Pin(config.VEML_PWR, Pin.OUT).off()
        time.sleep(0.2)
        Pin(config.VEML_PWR, Pin.OUT).on()
        time.sleep(0.5)
        return True
    return False

# --- BME Reset über GPIO / BME reset via GPIO ---
def bme_reset():
    if hasattr(config, "BME_PWR"):
        Pin(config.BME_PWR, Pin.OUT).off()
        time.sleep(0.2)
        Pin(config.BME_PWR, Pin.OUT).on()
        time.sleep(0.5)
        return True
    return False
