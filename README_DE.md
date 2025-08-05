
<p align="center">
  <img src="https://reset42.de/reset42.svg" alt="reset42 Logo" width="180"/>
</p>

# reset42 Gartensensor

**Plug & Play WLAN-Gartensensor für Maker, Bastler & Automatisierer – mit Raspberry Pi Pico W, BME280, VEML7700 und MQTT.**  
**Läuft mit MicroPython – lokal, modular, ohne Cloud.**

---

## 🌱 Funktionen

- 📶 **WiFi-fähig** – inkl. Fallback-WLAN und statischer IP (optional)
- 🌡️ Echtzeitdaten: Temperatur, Luftfeuchte, Luftdruck, Helligkeit (Lux)
- 🔄 **Asynchrone Runtime** via `uasyncio`
- 📡 **MQTT-Support** für Logging, Smart Home & Automatisierung
- 💡 **Status-LED** zur Fehleranzeige
- 🛠️ Vollständig modular, quelloffen & leicht erweiterbar (MIT-Lizenz)

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

VEML_SDA = 0
VEML_SCL = 1
BME_SDA = 2
BME_SCL = 3
ONBOARD_LED = "LED"
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

## 🧠 Architektur (Kurzfassung)

- `main.py`: Zentrale Ablaufsteuerung (WLAN, MQTT, Sensoren, LED)
- `lib/`:
  - `wifi.py`: Verbindet mit primärem oder Fallback-WLAN
  - `mqtt.py`: Verbindet zum Broker, sendet JSON-Daten
  - `sensors.py`: Liest BME280 + VEML7700, kann Reset auslösen
  - `leds.py`: Ansteuerung der Onboard-LED für Statusanzeigen
  - `config.py`: Konfiguration
  - `state.py`: Zustandscodes (z. B. `SUCCESS`, `FATAL_ERROR`)

---

## 🚨 Fehlersuche

| Fehler | LED blinkt | Beschreibung |
|--------|------------|--------------|
| WiFi-Fehler | 1× langsam | Keine Verbindung zu WLAN |
| MQTT-Fehler | 2× mittel | Broker nicht erreichbar |
| Sensorfehler | 3× schnell | Sensorantwort fehlerhaft |

---

## 🔒 Lizenz

reset42 Gardensensor ist Open Source und unter der **MIT-Lizenz** veröffentlicht.  
Nutzung für private & kommerzielle Projekte erlaubt – siehe `LICENSE`.

---

**Projektstatus:** aktiv gepflegt – weitere Sensoren, Web-Oberfläche & Sleep-Modus geplant.

Fragen, Ideen oder Feedback? → [reset42.de](https://reset42.de)
