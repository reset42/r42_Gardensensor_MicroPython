# config.py – zentrale Konfiguration / central configuration

# ========== WLAN-Konfiguration (primär) / WiFi configuration (primary) ==========
SSID            = "PN"           		 # Name des primären WLANs / Primary WiFi SSID
PASSWORD        = "5667361407102283a!"   # Passwort / Primary WiFi password
STATIC_IP       = ""               		 # Statische IP-Adresse (optional) / Static IP (optional)
NETMASK         = "255.255.255.0"        # Subnetzmaske / Subnet mask
GATEWAY         = "192.168.178.1"        # Gateway-Adresse / Default gateway
DNS             = "8.8.8.8"              # DNS-Server / DNS server

# ========== WLAN-Konfiguration (Fallback) / WiFi configuration (fallback) ==========
SSID_FB         = "Your_Secondary_SSID"   # Fallback WLAN / Secondary WiFi SSID
PASSWORD_FB     = "your_fallback_pass"    # Fallback Passwort / Password for fallback network
STATIC_IP_FB    = ""                      # Leer für DHCP / Leave empty for DHCP
NETMASK_FB      = "255.255.255.0"
GATEWAY_FB      = "192.168.1.1"
DNS_FB          = "1.1.1.1"

# ========== Zeitsynchronisation / Time sync settings ==========
NTP_SERVER      = "192.168.178.1"         # NTP-Server / NTP server
UTC_OFFSET      = "3600"                  # Zeitzonenoffset in Sekunden / Timezone offset (seconds, e.g. UTC+1)
SUMMER_OFFSET   = "3600"                  # Sommerzeit-Offset (Sekunden) / DST offset (seconds)

# ========== WLAN-Verbindungsversuche / WiFi retry logic ==========
MAX_WIFI_RETRIES    = 10                  # Maximale Versuche / Max connection retries
WIFI_RETRY_DELAY    = 0.5                 # Pause zwischen Versuchen (s) / Delay between retries (s)
WIFI_PRIMARY_CHECK  = 10                  # Prüfintervall Primärnetz / Loops before checking primary WiFi
WIFI_CONNECT_TIMEOUT = 3                  # Sekunden für WLAN-Timeout / Timeout for WiFi connect (seconds)

# ========== MQTT-Konfiguration / MQTT configuration ==========
MQTT_MODE       = "active"                 # "active", "dummy", "inactive"
MQTT_BROKER     = "192.168.178.100"       # MQTT-Broker IP / MQTT broker IP
MQTT_PORT       = 1883                    # Port
MQTT_CLIENT_ID  = "sensor_gh_1"           # Client-ID / Client ID
MQTT_TOPIC      = "sensor/gh/sensor_outdoor" # Topic
MQTT_USER       = None                    # Benutzer (optional) / User (optional)
MQTT_PASSWORD   = None                    # Passwort (optional) / Password (optional)

# ------- MQTT Payload Layout ---------------------------------
# Definiert die Felder und Reihenfolge des MQTT-Payloads.
# Defines fields and order of MQTT payload.
# → Einfach Felder ergänzen/entfernen, die in sensors.py erzeugt werden.
# → Just add/remove fields present in sensors.py.
MQTT_PAYLOAD_FIELDS = [
    "date",     # Datum / Date
    "time",     # Uhrzeit / Time
    "temp",     # Temperatur / Temperature (°C)
    "pressure",    # Luftdruck / Pressure (hPa)
    "humidity",      # Luftfeuchte / Humidity (%)
    "lux",      # Lichtstärke / Light intensity (Lux)
    # "soil",   # Beispiel: Bodenfeuchte / Example: Soil moisture
    # "co2",    # Beispiel: CO₂-Gehalt / Example: CO₂ level
]

# ========== Sensor-Update-Intervall / Sensor data send interval ==========
UPDATE_INTERVAL = 10                      # Sekunden / Seconds

# ========== LED-Konfiguration / LED pin setup ==========
ONBOARD_LED     = "LED"                   # Onboard-LED-Bezeichnung / Onboard LED name (constant in MicroPython)
STATUS_LED      = 16                      # GPIO für Status-LED / GPIO for external status LED

# ========================================================================
# === Sensor-Konfiguration mit Testmode / Sensor config with testmode ====
# ========================================================================

# ------ VEML7700 (Lichtsensor) / Light sensor ------
VEML_MODE           = "active"    # "active" (echt), "dummy" (simuliert), "inactive" (aus)
#                   # "active" (real), "dummy" (simulate), "inactive" (off)
VEML_SDA            = 0           # SDA-Pin für VEML7700 / SDA pin for VEML7700
VEML_SCL            = 1           # SCL-Pin / SCL pin
VEML_PWR            = 15          # Power-Pin / Power pin
VEML7700_ADDRESS    = 0x10        # I2C-Adresse / I2C address
VEML7700_IT         = 25          # Integrationszeit / Integration time (25, 50, 100, 200, 400, 800)
VEML7700_GAIN       = 1/8         # Gain: 1/8, 1/4, 1, 2

# ------ BME280 (Temp/RLF/Druck) / Temperature, humidity, pressure sensor ------
BME_MODE            = "active"    # "active" (echt), "dummy" (simuliert), "inactive" (aus)
#                   # "active" (real), "dummy" (simulate), "inactive" (off)
BME_SDA             = 2           # SDA-Pin / SDA pin
BME_SCL             = 3           # SCL-Pin / SCL pin
BME_PWR             = 14          # Power-Pin / Power pin
BME280_ADDRESS      = 0x76        # I2C-Adresse / I2C address
