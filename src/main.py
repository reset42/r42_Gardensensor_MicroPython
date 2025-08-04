# main.py – Main control logic for MQTT, WiFi and sensor handling (modular, WiFi/MQTT-first policy)

import uasyncio as asyncio
import wifi
import mqtt
import sensors
import leds
import state
import time
import config
import machine

# Error tracking for MQTT failures
soft_error_count = 0
MAX_SOFT_ERRORS = 5

# State tracking
fallback_mode = False
fallback_check_timer = time.time()
mqtt_connected = False

# Unified logger with timestamp and level indicator
def log(msg, level="INFO"):
    t = time.localtime()
    ts = f"{t[3]:02}:{t[4]:02}:{t[5]:02}"
    print(f"[{level}] {ts} – {msg}")

# Establish WiFi connection with fallback logic
async def connect_wifi():
    global fallback_mode
    for attempt in range(config.MAX_WIFI_RETRIES):
        log(f"🔌 Connecting to primary SSID: {config.SSID} – attempt {attempt + 1}")
        wifi.use_fallback = False
        if await wifi.connect() == state.SUCCESS:
            return True
        await asyncio.sleep(config.WIFI_RETRY_DELAY)

    for attempt in range(config.MAX_WIFI_RETRIES):
        log(f"🔌 Connecting to fallback SSID: {config.SSID_FB} – attempt {attempt + 1}")
        wifi.use_fallback = True
        if await wifi.connect() == state.SUCCESS:
            fallback_mode = True
            return True
        await asyncio.sleep(config.WIFI_RETRY_DELAY)

    log("❌ Failed to connect to any network – rebooting.", "FATAL")
    await leds.blink(leds.onboard_led, 10, 100)
    machine.reset()

# Monitor and maintain WiFi connection; periodically check for primary recovery
async def handle_wifi():
    global fallback_mode, fallback_check_timer
    if not wifi.is_connected():
        log("🚫 WiFi disconnected – trying to reconnect...", "WARN")
        await connect_wifi()

    if fallback_mode and time.time() - fallback_check_timer >= config.WIFI_PRIMARY_CHECK:
        log("🔁 Checking for primary WiFi availability...")
        wifi.use_fallback = False
        if await wifi.connect() == state.SUCCESS:
            log("✅ Switched back to primary WiFi")
            fallback_mode = False
        else:
            log("❌ Primary still unavailable – remain in fallback")
            wifi.use_fallback = True
        fallback_check_timer = time.time()

# Ensure MQTT connection; retry if disconnected
async def handle_mqtt():
    global mqtt_connected
    if not mqtt_connected:
        if mqtt.connect() == mqtt.SUCCESS:
            mqtt_connected = True
            log("✅ MQTT connection established")
        else:
            log("❌ MQTT unreachable – will retry", "ERROR")
            await leds.blink(leds.onboard_led, 3, 400)
            await asyncio.sleep(5)
            return False
    return True

# Read sensor values; attempt VEML7700 reset if needed
async def handle_sensors():
    sensor_status, sensor_data = sensors.read_all()
    if sensor_status != state.SUCCESS:
        log("⚠️ Sensor error – attempting VEML7700 reset", "WARN")
        await leds.blink(leds.onboard_led, 2, 150)
        sensors.reset_veml()
        await asyncio.sleep(5)
        return None
    return sensor_data

# Send sensor data via MQTT, handle failures and automatic recovery
async def handle_publish(data):
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
        await leds.blink(leds.onboard_led, 3, 400)
        await asyncio.sleep(5)

# Main event loop
async def main():
    log("🔧 Starting main loop...")
    await connect_wifi()
    wifi.sync_time()

    while True:
        await handle_wifi()
        mqtt_ok = await handle_mqtt()

        # Skip sensor operations if no connectivity
        if not wifi.is_connected() or not mqtt_ok:
            log("📡 Network or broker unavailable – reconnect only.", "WARN")
            await asyncio.sleep(5)
            continue

        sensor_data = await handle_sensors()
        if sensor_data:
            await handle_publish(sensor_data)

        await asyncio.sleep(config.UPDATE_INTERVAL)

# Run the asyncio event loop
try:
    asyncio.run(main())
finally:
    asyncio.new_event_loop()
