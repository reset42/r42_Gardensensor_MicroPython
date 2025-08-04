# wifi.py – WiFi connection and time sync logic (supports primary/fallback)

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

# Global interface handle
sta_if = network.WLAN(network.STA_IF)

# Controlled by main.py to determine which network to use
use_fallback = False

# Return static IP configuration if defined, else None for DHCP
def get_ifconfig():
    if use_fallback and config.STATIC_IP_FB:
        return (
            config.STATIC_IP_FB,
            config.NETMASK_FB,
            config.GATEWAY_FB,
            config.DNS_FB
        )
    elif not use_fallback and config.STATIC_IP:
        return (
            config.STATIC_IP,
            config.NETMASK,
            config.GATEWAY,
            config.DNS
        )
    return None

# Apply static or dynamic network configuration
def apply_network_config():
    cfg = get_ifconfig()
    if cfg:
        print("📡 Setting static IP (%s)" % ("fallback" if use_fallback else "primary"))
        sta_if.ifconfig(cfg)
    else:
        print("📡 DHCP enabled")

# Establish WiFi connection and wait for success or timeout
async def connect():
    if not sta_if.active():
        sta_if.active(True)

    apply_network_config()

    print("🔌 Connecting to WiFi...")
    ssid = config.SSID_FB if use_fallback else config.SSID
    password = config.PASSWORD_FB if use_fallback else config.PASSWORD
    sta_if.connect(ssid, password)

    retries = 0
    while not sta_if.isconnected() and retries < config.MAX_WIFI_RETRIES:
        await asyncio.sleep(config.WIFI_RETRY_DELAY)
        retries += 1
        print(".", end="")

    if sta_if.isconnected():
        print("\n✅ WiFi connected – IP:", sta_if.ifconfig()[0])
        return SUCCESS
    else:
        print("\n❌ WiFi connection failed.")
        return FATAL_ERROR

# Check if WiFi is currently connected
def is_connected():
    return sta_if.isconnected()

# Return IP address if connected
def get_ip():
    return sta_if.ifconfig()[0] if is_connected() else None

# Synchronize system time using NTP and apply local offset
def sync_time():
    if ntptime is None:
        print("❌ ntptime module not available.")
        return False

    try:
        ntptime.host = config.NTP_SERVER
        ntptime.settime()
        print("🕒 Time synchronized (UTC).")

        offset = int(config.UTC_OFFSET) + int(config.SUMMER_OFFSET)
        now = utime.time() + offset
        tm = utime.localtime(now)
        machine.RTC().datetime((tm[0], tm[1], tm[2], tm[6]+1, tm[3], tm[4], tm[5], 0))
        print("🕒 Local time applied:", "{:02d}:{:02d}:{:02d}".format(tm[3], tm[4], tm[5]))
        return True
    except Exception as e:
        print("⚠️ NTP sync error:", e)
        return False
