
<p align="center">
  <img src="https://reset42.de/reset42.svg" alt="reset42 Logo" width="180"/>
</p>

# reset42 Gardensensor

**Plug & Play Wi-Fi garden sensor for makers, tinkerers & automation fans – powered by Raspberry Pi Pico W, BME280, VEML7700 and MQTT.**  
**Runs on MicroPython – local, modular, no cloud required.**

---

## 🌱 Features

- 📶 **WiFi capable** – including fallback network and optional static IP
- 🌡️ Real-time data: temperature, humidity, pressure, light (Lux)
- 🔄 **Test & demo mode:** simulate sensor values and MQTT publishing via `config.py` (ideal for dev & unit tests)
- 🔄 **Async runtime** with `uasyncio`
- 🧩 **Flexible MQTT payload format:** fields & order configurable
- 📡 **MQTT support** for logging, smart home & automation
- 💡 **Status LED** for error indication
- 🛠️ Fully modular, open source & easily extendable (MIT license)

---

## 📘 Deutsche Version

👉 For the German version, see: [README_DE.md](README_DE.md)

---

## 🔧 Hardware

- [x] **Raspberry Pi Pico W** (MicroPython compatible)
- [x] **BME280** (I2C – temperature, humidity, pressure)
- [x] **VEML7700** (I2C – light intensity in Lux)
- [ ] **Status LED** (controllable, optional)
- [ ] **Optional** additional I2C sensors

---

## ⚙️ Installation

1. **Flash MicroPython**  
   Download the matching `.uf2` image for Pico W from  
   👉 [micropython.org/download/rp2-pico-w](https://micropython.org/download/rp2-pico-w)

2. **Upload files**  
   - Copy everything from `src/lib/` to the root directory of the Pico W  
     (e.g., via Thonny, `rshell`, `ampy`, or WebREPL)
   - Also copy `main.py` to the root directory

3. **Edit `config.py`**  
   - Wi-Fi credentials, MQTT broker settings, sensor GPIOs etc.
   - Configure sensor modes ("active", "dummy", "inactive") and MQTT fields

4. **Go!**  
   - Reboot → `main.py` starts automatically  
   - Status LED blinks on error (see Troubleshooting)

---

## 🧾 Sample `config.py`

See [src/lib/config.py](src/lib/config.py) in the repo for details:

```python
SSID = "MyWiFi"
PASSWORD = "supersecret"
STATIC_IP = ""  # leave empty for DHCP

MQTT_BROKER = "192.168.1.50"
MQTT_PORT = 1883
MQTT_CLIENT_ID = "sensor_indoor"

# Sensor & MQTT test modes
VEML_MODE = "dummy"      # "active", "dummy", "inactive"
BME_MODE  = "inactive"   # "active", "dummy", "inactive"
MQTT_MODE = "active"     # "active", "dummy", "inactive"

# MQTT Payload Fields
MQTT_PAYLOAD_FIELDS = [
    "date",
    "time",
    "temp",
    "pressure",
    "humidity",
    "lux",
]
```

---

## 📌 Default Pinout

| Component   | SDA | SCL | PWR (Power) |
|-------------|-----|-----|-------------|
| VEML7700    | GP0 | GP1 | GP15        |
| BME280      | GP2 | GP3 | GP14        |

| Function         | Pin        |
|------------------|------------|
| Onboard LED      | "LED"      |
| VEML Reset GPIO  | GP15       |

---

## 🧠 Architecture Overview

- `main.py`: Main loop control (WiFi, MQTT, sensors, LED)
- `lib/`:
  - `wifi.py`: Connects to primary or fallback WiFi
  - `mqtt.py`: Handles broker connection, JSON publishing, dummy mode
  - `sensors.py`: Reads BME280 & VEML7700 (real or dummy mode)
  - `leds.py`: Status LED control (blinking patterns)
  - `config.py`: Full configuration (WiFi, MQTT, sensors, payload fields)
  - `state.py`: Return codes (SUCCESS, FATAL_ERROR, ...)

---

## 🚨 Troubleshooting

| Problem        | LED Blinks       | Description               |
|----------------|------------------|---------------------------|
| WiFi Error     | 1× slow          | No connection to WiFi     |
| MQTT Error     | 2× medium        | Broker not reachable      |
| Sensor Error   | 3× fast          | Sensor not responding     |

---

## 🖼️ Case, STL & Assembly

- **Case files (STL) and full assembly instructions coming soon!**
- This is a "maker" project – feel free to contribute mechanical ideas via issue or PR.

---

## 🔒 License

reset42 Gardensensor is open source and licensed under the **MIT license**.  
Private & commercial use allowed – see `LICENSE`.

---

**Project status:** actively maintained – more sensors, web interface & sleep mode planned.  
**STL files and assembly guide will follow soon.**

Questions, ideas or feedback? → [reset42.de](https://reset42.de)
