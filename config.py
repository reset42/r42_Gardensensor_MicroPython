# config.py – zentrale Konfiguration

SSID = "Adomat"
PASSWORD = "7103550674337692a!"
STATIC_IP = "192.168.100.177"
NETMASK = "255.255.255.0"
GATEWAY = "192.168.100.1"
DNS = "8.8.8.8"

#SSID = "PN"
#PASSWORD = "5667361407102283a!"
#STATIC_IP = "192.168.178.101"
#NETMASK = "255.255.255.0"
#GATEWAY = "192.168.178.1"
#DNS = "8.8.8.8"

SSID_FB = "PN"
PASSWORD_FB = "5667361407102283a!"
STATIC_IP_FB = "192.168.178.101"
NETMASK_FB = "255.255.255.0"
GATEWAY_FB = "192.168.178.1"
DNS_FB = "192.168.178.1"

# Zeitsynchronisation
NTP_SERVER = "192.168.100.1"
UTC_OFFSET = "3600"            # Zeitzonenoffset in Sekunden (z. B. 3600 = UTC+1)
SUMMER_OFFSET = "3600"         # Zusätzliche Sommerzeitverschiebung (z. B. +1h)

MAX_WIFI_RETRIES = 10
WIFI_RETRY_DELAY = 0.5  # Sekunden
WIFI_PRIMARY_CHECK = 10  # Nach wie vielen Loops geprüft wird, ob primäres WLAN wieder verfügbar ist

MQTT_BROKER = "192.168.178.100"
MQTT_PORT = 1883
MQTT_CLIENT_ID = "sensor_indoor"
MQTT_TOPIC = "sensor/gh/sensor_indoor"

UPDATE_INTERVAL = 10

# LED-Pins
ONBOARD_LED = "LED"
STATUS_LED = 16
