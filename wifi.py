# wifi.py

import network
import config
import uasyncio as asyncio
import machine
import utime

try:
    import ntptime
except:
    ntptime = None

from state import SUCCESS, FATAL_ERROR

sta_if = network.WLAN(network.STA_IF)

# Wird von main.py gesetzt
use_fallback = False

def get_ifconfig():
    if use_fallback:
        if config.STATIC_IP_FB:
            return (
                config.STATIC_IP_FB,
                config.NETMASK_FB,
                config.GATEWAY_FB,
                config.DNS_FB
            )
    else:
        if config.STATIC_IP:
            return (
                config.STATIC_IP,
                config.NETMASK,
                config.GATEWAY,
                config.DNS
            )
    return None  # DHCP verwenden

def apply_network_config():
    cfg = get_ifconfig()
    if cfg:
        if use_fallback:
            print("📡 Fallback: Statische IP wird gesetzt")
        else:
            print("📡 Primär: Statische IP wird gesetzt")
        sta_if.ifconfig(cfg)
    else:
        print("📡 DHCP aktiviert")

async def connect():
    if not sta_if.active():
        sta_if.active(True)

    apply_network_config()

    print("🔌 Verbinde mit WLAN...")
    ssid = config.SSID_FB if use_fallback else config.SSID
    password = config.PASSWORD_FB if use_fallback else config.PASSWORD
    sta_if.connect(ssid, password)

    retries = 0
    while not sta_if.isconnected() and retries < config.MAX_WIFI_RETRIES:
        await asyncio.sleep(config.WIFI_RETRY_DELAY)
        retries += 1
        print(".", end="")

    if sta_if.isconnected():
        print("\n✅ WLAN verbunden mit IP:", sta_if.ifconfig()[0])
        return SUCCESS
    else:
        print("\n❌ WLAN-Verbindung fehlgeschlagen.")
        return FATAL_ERROR

def is_connected():
    return sta_if.isconnected()

def get_ip():
    return sta_if.ifconfig()[0] if is_connected() else None

def sync_time():
    if ntptime is None:
        print("❌ ntptime nicht verfügbar.")
        return FATAL_ERROR

    try:
        ntptime.host = config.NTP_SERVER
        ntptime.settime()
        print("🕒 Zeit synchronisiert (UTC).")

        offset = int(config.UTC_OFFSET) + int(config.SUMMER_OFFSET)
        now = utime.time() + offset
        tm = utime.localtime(now)
        machine.RTC().datetime((tm[0], tm[1], tm[2], tm[6]+1, tm[3], tm[4], tm[5], 0))
        print("🕒 Zeit lokal eingestellt:", "{:02d}:{:02d}:{:02d}".format(tm[3], tm[4], tm[5]))
        return SUCCESS
    except Exception as e:
        print("⚠️ NTP-Fehler:", e)
        return FATAL_ERROR
