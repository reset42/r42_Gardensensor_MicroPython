# Gardensensor by Reset42  
- for Micropython

---

**Plug & Play WLAN-Gartensensor für Maker, Bastler & Automatisierer – Raspberry Pi Pico W, BME280, VEML7700 und MQTT.**

---

## Features

- WiFi-fähig (kein Cloudzwang, volle Kontrolle)
- Echtzeitdaten: Temperatur, Luftfeuchte, Luftdruck, Helligkeit (Lux)
- Modular, erweiterbar & async-fähig
- MQTT-Unterstützung für Logging & Automatisierung
- Status-LED & Fehlercodes
- Vollständig Open Source (MIT)

---

## Hardware

- **Raspberry Pi Pico W** (MicroPython-fähig)
- **BME280** (I2C – Temperatur, Feuchte, Druck)
- **VEML7700** (I2C – Licht/Lux)
- **Status-LED** (optional, für Fehleranzeige)
- **(Optional) Weitere I2C-Sensoren einfach nachrüstbar**

---

## Installation

1. **MicroPython flashen:**  
   Lade das passende Image von [micropython.org/download/rp2-pico-w/](https://micropython.org/download/rp2-pico-w/), folge der dortigen Anleitung (drag&drop via USB).

2. **Dateien auf den Pico kopieren:**  
   - Kopiere den gesamten Inhalt aus `src/lib/` **in das Hauptverzeichnis** deines Pico W (z. B. via Thonny oder rshell/ampy).
   - Lege die `main.py` ins Hauptverzeichnis.
   - Achte darauf, dass alle benötigten Bibliotheken (s. u.) vorhanden sind.

3. **config.py anpassen:**  
   Trage deine WLAN-Daten, MQTT-Server, Sensor-Pins usw. in `config.py` ein.

4. **Start:**  
   - Starte den Pico neu, `main.py` läuft automatisch.
   - Status-LED zeigt Fehler an (siehe Troubleshooting).



## Beispiel: config.py
Siehe config.py im repo für weitere Informationen ! 

```python
# config.py – zentrale Konfiguration für WLAN, MQTT, Sensoren

SSID = "MeinWLAN"
PASSWORD = "supergeheim"
STATIC_IP = ""          # leer für DHCP
MQTT_BROKER = "192.168.1.50"
MQTT_PORT = 1883
MQTT_CLIENT_ID = "sensor_indoor"
VEML_SDA = 0
VEML_SCL = 1
BME_SDA = 2
BME_SCL = 3
ONBOARD_LED = "LED"

```
---

- **BME280** SDA/SCL: GPIO2 / GPIO3
- **BME280** (I2C – Temperatur, Feuchte, Druck)
- **VEML7700** (I2C – Licht/Lux)
- **Status-LED** (optional, für Fehleranzeige)
- **(Optional) Weitere I2C-Sensoren einfach nachrüstbar**

## Pinout (Standard)
- **BME280** |  SDA/SCL: GPIO2 / GPIO3
- **VEML7700** |  SDA/SCL: GPIO0 / GPIO1

## Status-LED: 
- **LED** (Onboard) oder frei wählbar (z. B. GPIO16)

---

## Troubleshooting
- **LED blinkt schnell:** Kein WLAN oder MQTT erreichbar.

- **LED blinkt langsam:** Sensorfehler (BME280 oder VEML7700 nicht gefunden).

- **Keine Werte:** Prüfe Verkabelung, I2C-Pins, MQTT-Konfiguration.

## Tipp:
- Du kannst via USB-Seriell mit screen/minicom/Thonny debuggen und Logs auslesen.


## Lizenz
**MIT License – siehe LICENSE**

## Fragen, Feedback, Bugs?
- Erstelle ein [GitHub Issue](https://github.com/reset42/r42_Gardensensor_MicroPython/issues)
- oder schreib an info@reset42.de 
