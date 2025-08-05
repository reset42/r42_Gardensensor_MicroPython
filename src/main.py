# main.py – Main control logic for MQTT, WiFi and sensor handling (synchrones robustes WLAN-Setup)

import wifi
import mqtt
import sensors
import leds
import state
import time
import config
import machine

soft_error_count = 0
MAX_SOFT_ERRORS = 5

fallback_mode = False
fallback_check_timer = time.time()
mqtt_connected = False

def log(msg, level="INFO"):
    t = time.localtime()
    ts = f"{t[3]:02}:{t[4]:02}:{t[5]:02}"
    print(f"[{level}] {ts} – {msg}")

def connect_wifi_blocking():
    wifi.use_fallback = False
    log("🔌 Verbinde mit primärem WLAN...")
    if wifi.connect_wifi():
        return state.SUCCESS
    # Falls Primär fehlschlägt → Fallback versuchen
    for attempt in range(config.MAX_WIFI_RETRIES):
        log(f"🔌 Connecting to fallback SSID: {config.SSID_FB} – attempt {attempt + 1}")
        wifi.use_fallback = True
        if wifi.connect_wifi():
            global fallback_mode
            fallback_mode = True
            return state.SUCCESS
        time.sleep(config.WIFI_RETRY_DELAY)
    log("❌ Failed to connect to any network – rebooting.", "FATAL")
    error_blink("WIFI_FAIL")
    machine.reset()
    return state.FATAL_ERROR

def handle_wifi():
    global fallback_mode, fallback_check_timer
    if not wifi.is_connected():
        log("🚫 WiFi disconnected – trying to reconnect...", "WARN")
        connect_wifi_blocking()
    if fallback_mode and time.time() - fallback_check_timer >= config.WIFI_PRIMARY_CHECK:
        log("🔁 Checking for primary WiFi availability...")
        wifi.use_fallback = False
        if wifi.connect_wifi():
            log("✅ Switched back to primary WiFi")
            fallback_mode = False
        else:
            log("❌ Primary still unavailable – remain in fallback")
            wifi.use_fallback = True
        fallback_check_timer = time.time()

def handle_mqtt():
    global mqtt_connected
    if not mqtt_connected:
        if mqtt.connect() == mqtt.SUCCESS:
            mqtt_connected = True
            log("✅ MQTT connection established")
        else:
            log("❌ MQTT unreachable – will retry", "ERROR")
            error_blink("MQTT_FAIL")
            time.sleep(5)
            return False
    return True

def handle_sensors():
    sensor_status, sensor_data = sensors.read_all()
    if sensor_status != state.SUCCESS:
        log("⚠️ Sensor error – attempting VEML7700 reset", "WARN")
        error_blink("SENSOR_FAIL")
        sensors.reset_veml()
        time.sleep(5)
        return None
    return sensor_data

def handle_publish(data):
    global soft_error_count, mqtt_connected
    result = mqtt.publish(data)
    if result == mqtt.SUCCESS:
        log("✅ Data published successfully")
        soft_error_count = 0
    elif result == mqtt.RECOVERED:
        log("🔁 MQTT reconnected – continuing")
        soft_error_count = 0
    elif result == mqtt.FATAL_ERROR:
        log("❌ Publish failed – MQTT disconnected", "ERROR")
        mqtt_connected = False
        soft_error_count += 1
        if soft_error_count >= MAX_SOFT_ERRORS:
            log("🚨 Too many publish errors – rebooting.", "FATAL")
            machine.reset()
        leds.blink(leds.onboard_led, 3, 400)
        time.sleep(5)

def main():
    log("🔧 Starting main loop...")
    wifi_result = connect_wifi_blocking()
    if wifi_result != state.SUCCESS:
        return

    if not wifi.sync_time():
        log("⚠️ Time sync failed – continuing without NTP.", "WARN")
        leds.blink(leds.onboard_led, 4, 100)

    while True:
        handle_wifi()
        mqtt_ok = handle_mqtt()

        if not wifi.is_connected() or not mqtt_ok:
            log("📡 Network or broker unavailable – reconnect only.", "WARN")
            time.sleep(5)
            continue

        sensor_data = handle_sensors()
        if sensor_data:
            handle_publish(sensor_data)

        time.sleep(config.UPDATE_INTERVAL)

ERROR_PATTERNS = {
    "WIFI_FAIL": (10, 100),
    "MQTT_FAIL": (3, 400),
    "SENSOR_FAIL": (2, 150),
    "PUBLISH_FAIL": (3, 400),
    "NTP_FAIL": (4, 100),
}

def error_blink(reason):
    pattern = ERROR_PATTERNS.get(reason)
    if pattern:
        return leds.blink(leds.onboard_led, *pattern)
    return None

if __name__ == "__main__":
    main()
