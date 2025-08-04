# config.py – zentrale Konfiguration / central configuration

# WLAN-Konfiguration (primär)
SSID = "Your_Primary_SSID"          # Name des primären WLANs / Primary WiFi SSID
PASSWORD = "Your_Password"          # Passwort des primären WLANs / Primary WiFi password
STATIC_IP = "Your_Static_IP"        # Statische IP-Adresse (optional) / Static IP (optional)
NETMASK = "255.255.255.0"            # Subnetzmaske / Subnet mask
GATEWAY = "192.168.1.1"              # Gateway-Adresse / Default gateway
DNS = "8.8.8.8"                      # DNS-Server / DNS server

# WLAN-Konfiguration (Fallback)
SSID_FB = "Your_Secondary_SSID"      # Zweites WLAN als Fallback / Secondary WiFi SSID (fallback)
PASSWORD_FB = "your_fallback_pass"   # Passwort für Fallback-WLAN / Password for fallback network
STATIC_IP_FB = "192.168.1.101"       # Statische IP im Fallback-Netz / Static IP in fallback network
NETMASK_FB = "255.255.255.0"
GATEWAY_FB = "192.168.1.1"
DNS_FB = "1.1.1.1"

# Zeitsynchronisation / Time sync settings
NTP_SERVER = "pool.ntp.org"           # Öffentlicher NTP-Server / Public NTP server
UTC_OFFSET = "3600"                  # Zeitzonenoffset in Sekunden / Timezone offset in seconds (e.g. UTC+1)
SUMMER_OFFSET = "3600"               # Sommerzeit-Offset in Sekunden / Daylight saving offset in seconds

# WLAN-Verbindungsversuche / WiFi retry logic
MAX_WIFI_RETRIES = 10                # Maximale Versuche für Verbindung / Max WiFi connection retries
WIFI_RETRY_DELAY = 0.5               # Verzögerung zwischen Versuchen (Sekunden) / Delay between retries (s)
WIFI_PRIMARY_CHECK = 10              # Prüfintervall für Rückkehr ins Primärnetz / Loops before checking primary WiFi

# MQTT-Konfiguration / MQTT configuration
MQTT_BROKER = "mqtt.example.com"      # IP-Adresse oder Hostname des MQTT-Brokers / MQTT broker IP or hostname
MQTT_PORT = 1883                     # Standardport für MQTT / MQTT default port
MQTT_CLIENT_ID = "sensor_indoor"     # Eindeutiger Name des Geräts / Unique client ID
MQTT_TOPIC = "sensor/gh/sensor_indoor" # Topic für Sensordaten / Topic to publish sensor data

# Sensor-Update-Intervall / Sensor data send interval
UPDATE_INTERVAL = 10                 # Sekunden / in seconds

# LED-Konfiguration / LED pin setup
ONBOARD_LED = "LED"                  # Onboard-LED-Bezeichnung / Onboard LED name (constant in MicroPython)
STATUS_LED = 16                      # GPIO für Status-LED / GPIO for external status LED
