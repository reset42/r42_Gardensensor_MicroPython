<p align="center">
  <img src="https://reset42.de/reset42.svg" alt="reset42 Logo" width="180"/>
</p>

# reset42 Gardensensor

**Plug & Play WLAN-Gartensensor für Maker, Bastler und Automatisierungs-Fans – basierend auf Raspberry Pi Pico W, BME280, VEML7700 und MQTT.**  
**Läuft mit MicroPython – lokal, modular, ohne Cloud.**

---

## 🌱 Funktionen

- 📶 **WLAN-fähig** – inkl. Fallback-Netzwerk und optionaler statischer IP
- 🌡️ Live-Daten: Temperatur, Luftfeuchtigkeit, Luftdruck, Licht (Lux)
- 🧪 **Test- & Demo-Modus:** Sensordaten und MQTT-Publishing über `config.py` simulieren (ideal für Entwicklung & Tests)
- 🧩 **Flexibles MQTT-Format:** Felder & Reihenfolge konfigurierbar
- 📡 **MQTT-Unterstützung** für Logging, Smart Home & Automatisierung
- 💡 **Status-LED** für Fehlermeldungen
- 🛠️ Vollständig modular, quelloffen & einfach erweiterbar (MIT-Lizenz)

---

## 🔧 Hardware

- [x] **Raspberry Pi Pico W** (MicroPython-kompatibel)
- [x] **BME280** (I2C – Temperatur, Luftfeuchte, Luftdruck)
- [x] **VEML7700** (I2C – Lichtintensität in Lux)
- [ ] **Status-LED** (steuerbar, optional)
- [ ] **Optional** zusätzliche I2C-Sensoren

---

## ⚙️ Installation

1. **MicroPython flashen**  
   Passendes `.uf2`-Image für den Pico W herunterladen von:  
   👉 [micropython.org/download/rp2-pico-w](https://micropython.org/download/rp2-pico-w)

2. **Dateien hochladen**  
   - Alles aus `src/lib/` ins Hauptverzeichnis des Pico W kopieren  
     (z. B. mit Thonny, `rshell`, `ampy` oder WebREPL)
   - Zusätzlich `main.py` ins Hauptverzeichnis kopieren

3. **`config.py` anpassen**  
   - WLAN-Daten, MQTT-Broker, Sensor-Pins etc.
   - Sensor-Modi konfigurieren ("active", "dummy", "inactive") sowie MQTT-Felder

4. **Los geht’s!**  
   - Reboot → `main.py` startet automatisch  
   - Status-LED blinkt bei Fehlern (siehe Troubleshooting)

---

## 🧾 Beispiel `config.py`

Details siehe [src/lib/config.py](src/lib/config.py) im Repository:

```python
SSID = "MyWiFi"
PASSWORD = "supersecret"
STATIC_IP = ""  # leer lassen für DHCP

MQTT_BROKER = "192.168.1.50"
MQTT_PORT = 1883
MQTT_CLIENT_ID = "sensor_indoor"

# Sensor- & MQTT-Modi
VEML_MODE = "dummy"      # "active", "dummy", "inactive"
BME_MODE  = "inactive"   # "active", "dummy", "inactive"
MQTT_MODE = "active"     # "active", "dummy", "inactive"

# MQTT Payload-Felder
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

## 📌 Standard-Pinbelegung

| Komponente  | SDA | SCL | VCC (Power) |
|-------------|-----|-----|-------------|
| VEML7700    | GP0 | GP1 | GP15        |
| BME280      | GP2 | GP3 | GP14        |

| Funktion          | Pin        |
|-------------------|------------|
| Onboard-LED       | "LED"      |
| VEML Reset GPIO   | GP15       |

---

## 🧠 Architekturübersicht

- `main.py`: Hauptsteuerung (WLAN, MQTT, Sensoren, LED)
- `lib/`:
  - `wifi.py`: Verbindung zu primärem oder Fallback-WLAN
  - `mqtt.py`: Verbindet mit Broker, sendet JSON, Dummy-Modus
  - `sensors.py`: Liest BME280 & VEML7700 (real oder simuliert)
  - `leds.py`: LED-Ansteuerung für Statussignale
  - `config.py`: Zentrale Konfiguration (WLAN, MQTT, Sensoren, Payload)
  - `state.py`: Rückgabecodes (SUCCESS, FATAL_ERROR, …)

---

## 🚨 Fehlersignale (LED)

| Problem         | LED-Blinkmuster     | Bedeutung                  |
|-----------------|---------------------|----------------------------|
| WLAN-Fehler     | 1× langsam          | Keine Verbindung möglich   |
| MQTT-Fehler     | 2× mittel           | Broker nicht erreichbar    |
| Sensor-Fehler   | 3× schnell          | Sensor antwortet nicht     |

---

## 🖼️ Gehäuse, STL & Zusammenbau

- **STL-Dateien und Anleitung folgen in Kürze!**
- Das Projekt richtet sich an Maker – gerne Ideen via Issue oder PR beisteuern.

---

## 🔒 Lizenz

reset42 Gardensensor ist Open Source und steht unter der **MIT-Lizenz**.  
Private & kommerzielle Nutzung erlaubt – siehe `LICENSE`.

---

**Projektstatus:** aktiv gepflegt – weitere Sensoren, Webinterface & Sleep-Modus geplant.  
**STL-Dateien und Montageanleitung folgen bald.**

Fragen, Ideen oder Feedback? → [reset42.de](https://reset42.de)
