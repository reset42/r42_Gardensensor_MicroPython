# sensors.py – Sensorinitialisierung und Auslesung / Sensor initialization and data reading

from machine import Pin, I2C
from veml7700_driver import VEML7700
from bme280_driver import BME280
import time
from collections import OrderedDict
import state
import config

veml = None
bme = None

# --- Sensor-Versorgung aktivieren / Activate sensor power ---
veml_power = Pin(config.VEML_PWR, Pin.OUT)
veml_power.value(1)

bme_power = Pin(config.BME_PWR, Pin.OUT)
bme_power.value(1)

# --- I2C-Initialisierung / I2C initialization ---
i2c_veml = I2C(0, scl=Pin(config.VEML_SCL), sda=Pin(config.VEML_SDA))
i2c_bme = I2C(1, scl=Pin(config.BME_SCL), sda=Pin(config.BME_SDA))

# --- Initialisierung VEML7700 / VEML7700 initialization ---
def init_veml():
    global veml
    try:
        veml = VEML7700(i2c=i2c_veml)
        print("📷 VEML7700 initialisiert / VEML7700 initialized.")
        return state.SUCCESS
    except Exception as e:
        print("❌ VEML7700 Fehler bei Init / Init error:", e)
        return state.FATAL_ERROR

def reset_veml():
    print("🔄 VEML7700 wird neu gestartet / VEML7700 reset...")
    veml_power.value(0)
    time.sleep(0.2)
    veml_power.value(1)
    time.sleep(0.2)
    return init_veml()

def read_veml():
    # Unterstützt active, dummy und inactive / Supports active, dummy, inactive
    mode = getattr(config, "VEML_MODE", "active")
    if mode == "inactive":
        return state.SUCCESS, None
    if mode == "dummy":
        import random
        return state.SUCCESS, random.randint(0, 2000)
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
        print("❌ VEML7700 Fehler beim Lesen / Read error:", e)
        return state.FATAL_ERROR, {}

# --- Initialisierung BME280 / BME280 initialization ---
def init_bme():
    global bme
    try:
        bme = BME280(i2c=i2c_bme, address=config.BME280_ADDRESS)
        print("🌡️ BME280 initialisiert / BME280 initialized.")
        return state.SUCCESS
    except Exception as e:
        print("❌ BME280 Fehler bei Init / Init error:", e)
        return state.FATAL_ERROR

def read_bme():
    mode = getattr(config, "BME_MODE", "active")
    if mode == "inactive":
        return state.SUCCESS, {"temp": None, "pressure": None, "humidity": None}
    if mode == "dummy":
        import random
        return state.SUCCESS, {
            "temp": round(random.uniform(20.0, 35.0), 1),
            "pressure": round(random.uniform(980.0, 1050.0), 1),
            "humidity": round(random.uniform(20.0, 80.0), 1)
        }
    global bme
    try:
        if bme is None:
            if init_bme() != state.SUCCESS:
                return state.FATAL_ERROR, {}
        temp, pressure, humidity = bme.read_compensated_data()
        return state.SUCCESS, {
            "temp": round(temp, 1),
            "pressure": round(pressure, 1),
            "humidity": round(humidity, 1)
        }
    except Exception as e:
        print("❌ BME280 Fehler beim Lesen / Read error:", e)
        return state.FATAL_ERROR, {}

# --- RTC-Zeit holen / Get RTC time ---
def get_formatted_rtc():
    now = time.localtime()
    datum = "{:02d}.{:02d}.{:04d}".format(now[2], now[1], now[0])
    uhrzeit = "{:02d}:{:02d}:{:02d}".format(now[3], now[4], now[5])
    return datum, uhrzeit

# --- Hilfsfunktion: Payload bauen nach config / Build payload by config fields ---
def build_payload(data):
    fields = getattr(config, "MQTT_PAYLOAD_FIELDS", None)
    if fields:
        payload = OrderedDict()
        for field in fields:
            payload[field] = data.get(field, None)
        # Warnung, falls Felder fehlen
        missing = [f for f in fields if f not in data]
        if missing:
            print("⚠️ Warnung: Feld(er) in MQTT_PAYLOAD_FIELDS nicht im sensors.py erzeugt: / Warning: Field(s) in MQTT_PAYLOAD_FIELDS not produced in sensors.py:", missing)
        return payload
    # Fallback: alle Felder übernehmen / fallback: all fields
    return OrderedDict(data)

# --- Gesamtsensor-Auslesung / Read all sensors ---
def read_all():
    datum, uhrzeit = get_formatted_rtc()

    # VEML
    status_lux, lux = read_veml()
    if status_lux != state.SUCCESS:
        lux = None

    # BME280
    status_bme, bme_data = read_bme()
    if status_bme != state.SUCCESS or bme_data is None:
        bme_data = {"temp": None, "pressure": None, "humidity": None}

    # Alle Sensorwerte als Dict sammeln / Collect all sensor values as dict
    data = {
        "date": datum,
        "time": uhrzeit,
        "temp": bme_data["temp"],
        "pressure": bme_data["pressure"],
        "humidity": bme_data["humidity"],
        "lux": lux
        # → Hier beliebig um neue Felder erweitern! / Add more fields here as needed!
    }

    # Flexibler Payload je nach Config-Feldliste / Flexible payload according to config field list
    payload = build_payload(data)
    return state.SUCCESS, payload
