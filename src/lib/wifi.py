# wifi.py – Minimaler WLAN-Connector, wie aus vanilla.zip

import network
import config
import time

def is_connected():
    wlan = network.WLAN(network.STA_IF)
    return wlan.isconnected()

def connect_wifi():
    print(f"🔌 Verbinde mit WLAN: {config.SSID}")
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.disconnect()
    time.sleep(1)
    wlan.connect(config.SSID, config.PASSWORD)

    for _ in range(10):
        if wlan.isconnected():
            print(f"✅ Verbunden – IP: {wlan.ifconfig()[0]}")
            return True
        print("⏳ warte auf Verbindung...")
        time.sleep(1)

    print("❌ Verbindung fehlgeschlagen.")
    return False

def sync_time():
    try:
        import ntptime
        ntptime.host = getattr(config, "NTP_SERVER", "pool.ntp.org")
        time.sleep(1)
        now = time.time() + int(getattr(config, "UTC_OFFSET", 0)) + int(getattr(config, "SUMMER_OFFSET", 0))
        tm = time.localtime(now)
        import machine
        machine.RTC().datetime((tm[0], tm[1], tm[2], tm[6]+1, tm[3], tm[4], tm[5], 0))
        print("[INFO] Zeit synchronisiert.")
        return True
    except Exception as e:
        print(f"[WARN] Zeitabgleich fehlgeschlagen: {e}")
        return False
