
<p align="center">
  <img src="https://reset42.de/reset42.svg" alt="reset42 Logo" width="180"/>
</p>

# reset42 Gardensensor

**Plug & Play WLAN-Gartensensor für Maker, Bastler & Automatisierer – mit Raspberry Pi Pico W, BME280, VEML7700 und MQTT.**  
**Läuft mit MicroPython – lokal, modular, ohne Cloud.**

---

## 🌱 Features

- 📶 **WiFi-fähig** – inkl. Fallback-WLAN und statischer IP (optional)
- 🌡️ Echtzeitdaten: Temperatur, Luftfeuchte, Luftdruck, Helligkeit (Lux)
- 🔄 **Test- und Demo-Modus:** Sensorwerte und MQTT-Publishing können in der `config.py` simuliert werden (ideal für Entwicklung & Unit-Tests)
- 🔄 **Asynchrone Runtime** via `uasyncio`
- 🧩 **Flexibles MQTT-Payload-Layout:** Felder und Reihenfolge per Konfiguration steuerbar
- 📡 **MQTT-Support** für Logging, Smart Home & Automatisierung
- 💡 **Status-LED** zur Fehleranzeige
- 🛠️ Vollständig modular, quelloffen & leicht erweiterbar (MIT-Lizenz)

---

## 🌍 Key Features (EN summary)

- 📶 **WiFi (w/ fallback), static IP possible**
- 🌡️ Real-time: temperature, humidity, pressure, light (Lux)
- 🔄 **Test/Demo mode:** Simulate sensors & MQTT from config for dev/unit tests
- 📡 **MQTT support** for automation/logging (fully customizable JSON payload)
- 💡 **Status LED** error indication
- 🧩 **Modular, open source, easily extendable**
- **No cloud required** – runs 100% local, fully offline capable

---

## 🔧 Hardware

- [x] **Raspberry Pi Pico W** (MicroPython-fähig)
- [x] **BME280** (I2C – Temperatur, Feuchtigkeit, Luftdruck)
- [x] **VEML7700** (I2C – Lichtstärke in Lux)
- [ ] **Status-LED** (ansteuerbar, optional)
- [ ] **weitere I2C-Sensoren optional integrierbar**

---

## ⚙️ Installation

1. **MicroPython flashen**  
   Lade das passende `.uf2`-Image für den Pico W von  
   👉 [micropython.org/download/rp2-pico-w](https://micropython.org/download/rp2-pico-w)

2. **Dateien übertragen**  
   - Kopiere den Inhalt von `src/lib/` in das Hauptverzeichnis des Pico W  
     (z. B. mit Thonny, `rshell`, `ampy` oder WebREPL)
   - Kopiere `main.py` ebenfalls ins Hauptverzeichnis

3. **`config.py` anpassen**  
   - WLAN-Daten, MQTT-Broker, Sensor-Pins etc.
   - Sensor-Modi ("active", "dummy", "inactive") und MQTT-Felder einstellen

4. **Los geht's!**  
   - Reboot → `main.py` startet automatisch  
   - Status-LED blinkt bei Fehlern (siehe Troubleshooting)

---

## 🧾 Beispiel `config.py`

Siehe [src/lib/config.py](src/lib/config.py) im Repo für Details:

```python
SSID = "MeinWLAN"
PASSWORD = "supergeheim"
STATIC_IP = ""  # leer = DHCP

MQTT_BROKER = "192.168.1.50"
MQTT_PORT = 1883
MQTT_CLIENT_ID = "sensor_indoor"

# Sensor- und MQTT-Testmodi
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

## 📌 Standard-Pinout

| Komponente   | SDA | SCL |
|--------------|-----|-----|
| VEML7700     | GP0 | GP1 |
| BME280       | GP2 | GP3 |

| Funktion         | Pin        |
|------------------|------------|
| Onboard-LED      | "LED"      |
| VEML Reset GPIO  | GP15       |

---

## 🧠 Architektur (Kurzfassung / Architecture overview)

- `main.py`: Zentrale Ablaufsteuerung (WLAN, MQTT, Sensoren, LED)
- `lib/`:
  - `wifi.py`: Verbindet mit primärem oder Fallback-WLAN / WiFi with fallback logic
  - `mqtt.py`: Brokerverbindung, JSON-Publishing, Dummy-Modus möglich
  - `sensors.py`: Liest BME280 & VEML7700, kann Dummy/Inaktiv-Modus
  - `leds.py`: Status-LED für Fehler (verschiedene Blinkmuster)
  - `config.py`: Vollständige Konfiguration (WLAN, MQTT, Sensoren, Payload-Felder)
  - `state.py`: Zustandscodes (SUCCESS, FATAL_ERROR, ...)

---

## 🚨 Troubleshooting

| Fehler | LED blinkt | Beschreibung |
|--------|------------|--------------|
| WiFi-Fehler | 1× langsam | Keine Verbindung zu WLAN |
| MQTT-Fehler | 2× mittel | Broker nicht erreichbar |
| Sensorfehler | 3× schnell | Sensorantwort fehlerhaft |

---

## 🖼️ Gehäuse, STL & Montage

- **Gehäusedateien (STL) und eine ausführliche Montageanleitung folgen in Kürze!**
- Das Projekt ist für "Maker" gedacht – Feedback zu mechanischer Integration gern als Issue/PR.

---

## 🔒 Lizenz

reset42 Gardensensor ist Open Source und unter der **MIT-Lizenz** veröffentlicht.  
Nutzung für private & kommerzielle Projekte erlaubt – siehe `LICENSE`.

---

**Projektstatus:** aktiv gepflegt – weitere Sensoren, Web-Oberfläche & Sleep-Modus geplant.  
**STL-Dateien und Aufbauanleitung folgen in Kürze!**

Fragen, Ideen oder Feedback? → [reset42.de](https://reset42.de)
