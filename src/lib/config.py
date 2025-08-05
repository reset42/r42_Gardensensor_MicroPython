
# config.py – zentrale Konfiguration / central configuration

# ========== WLAN-Konfiguration (primär) / WiFi configuration (primary) ==========
SSID            = "Your_Primary_SSID"
PASSWORD        = "your_primary_password"
STATIC_IP       = ""
NETMASK         = "255.255.255.0"
GATEWAY         = "192.168.1.1"
DNS             = "8.8.8.8"

# ========== WLAN-Konfiguration (Fallback) / WiFi configuration (fallback) ==========
SSID_FB         = "Your_Secondary_SSID"
PASSWORD_FB     = "your_fallback_password"
STATIC_IP_FB    = ""
NETMASK_FB      = "255.255.255.0"
GATEWAY_FB      = "192.168.2.1"
DNS_FB          = "1.1.1.1"

# ========== Zeitsynchronisation / Time sync settings ==========
NTP_SERVER      = "pool.ntp.org"
UTC_OFFSET      = "3600"
SUMMER_OFFSET   = "3600"

# ========== WLAN-Verbindungsversuche / WiFi retry logic ==========
MAX_WIFI_RETRIES    = 10
WIFI_RETRY_DELAY    = 0.5
WIFI_PRIMARY_CHECK  = 10
WIFI_CONNECT_TIMEOUT = 3

# ========== MQTT-Konfiguration / MQTT configuration ==========
MQTT_MODE       = "active"
MQTT_BROKER     = "192.168.1.100"
MQTT_PORT       = 1883
MQTT_CLIENT_ID  = "sensor_default"
MQTT_TOPIC      = "sensor/default"
MQTT_USER       = None
MQTT_PASSWORD   = None

MQTT_PAYLOAD_FIELDS = [
    "date",
    "time",
    "temp",
    "pressure",
    "humidity",
    "lux",
]

# ========== Sensor-Update-Intervall / Sensor data send interval ==========
UPDATE_INTERVAL = 10

# ========== LED-Konfiguration / LED pin setup ==========
ONBOARD_LED     = "LED"
STATUS_LED      = 16

# === Sensor-Konfiguration mit Testmode / Sensor config with testmode ===

# ------ VEML7700 (Lichtsensor) / Light sensor ------
VEML_MODE           = "active"
VEML_SDA            = 0
VEML_SCL            = 1
VEML_PWR            = 15
VEML7700_ADDRESS    = 0x10
VEML7700_IT         = 25
VEML7700_GAIN       = 1/8

# ------ BME280 (Temp/RLF/Druck) / Temperature, humidity, pressure sensor ------
BME_MODE            = "active"
BME_SDA             = 2
BME_SCL             = 3
BME_PWR             = 14
BME280_ADDRESS      = 0x76