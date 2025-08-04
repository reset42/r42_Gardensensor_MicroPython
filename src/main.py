# main.py – Hauptlogik mit MQTT, WLAN und Sensoren

import uasyncio as asyncio
import wifi
import mqtt
import sensors
import leds
import state
import time
import config
import machine

async def main():
    print("🔧 Starte Hauptlogik...")

    fallback_mode = False
    fallback_check_timer = time.time()

    # WLAN-Verbindung beim Start herstellen
    for attempt in range(config.MAX_WIFI_RETRIES):
        print(f"🔌 Verbinde mit Primärnetzwerk SSID: {config.SSID} – Versuch {attempt + 1} von {config.MAX_WIFI_RETRIES}")
        wifi.use_fallback = False
        wifi_status = await wifi.connect()
        if wifi_status == state.SUCCESS:
            break
        await asyncio.sleep(config.WIFI_RETRY_DELAY)
    else:
        for attempt in range(config.MAX_WIFI_RETRIES):
            print(f"🔌 Verbinde mit Fallbacknetzwerk SSID: {config.SSID_FB} – Versuch {attempt + 1} von {config.MAX_WIFI_RETRIES}")
            wifi.use_fallback = True
            wifi_status = await wifi.connect()
            if wifi_status == state.SUCCESS:
                fallback_mode = True
                break
            await asyncio.sleep(config.WIFI_RETRY_DELAY)
        else:
            print("❌ WLAN konnte mit keinem Netzwerk verbunden werden – Neustart.")
            await leds.blink(leds.onboard_led, 10, 100)
            machine.reset()

    wifi.sync_time()
    mqtt_connected = False

    while True:
        # WLAN prüfen & ggf. reconnecten
        if not wifi.is_connected():
            print("🚫 WLAN getrennt – versuche Neuverbindung...")

            for attempt in range(config.MAX_WIFI_RETRIES):
                print(f"🔌 Verbinde mit Primärnetzwerk SSID: {config.SSID} – Versuch {attempt + 1} von {config.MAX_WIFI_RETRIES}")
                wifi.use_fallback = False
                wifi_status = await wifi.connect()
                if wifi_status == state.SUCCESS:
                    print("✅ Primärnetzwerk verbunden")
                    fallback_mode = False
                    break
                await asyncio.sleep(config.WIFI_RETRY_DELAY)
                import webrepl
                webrepl.start()
            else:
                for attempt in range(config.MAX_WIFI_RETRIES):
                    print(f"🔌 Verbinde mit Fallbacknetzwerk SSID: {config.SSID_FB} – Versuch {attempt + 1} von {config.MAX_WIFI_RETRIES}")
                    wifi.use_fallback = True
                    wifi_status = await wifi.connect()
                    if wifi_status == state.SUCCESS:
                        print("✅ Fallbacknetzwerk verbunden")
                        fallback_mode = True
                        break
                    await asyncio.sleep(config.WIFI_RETRY_DELAY)
                else:
                    print("❌ WLAN weiterhin getrennt – warte 10s")
                    await leds.blink(leds.onboard_led, 5, 100)
                    await asyncio.sleep(10)
                    continue

        # Primäres WLAN regelmäßig prüfen (wenn im Fallback)
        if fallback_mode and time.time() - fallback_check_timer >= config.WIFI_PRIMARY_CHECK:
            print("🔁 Prüfe primäres WLAN...")
            wifi.use_fallback = False
            wifi_status = await wifi.connect()
            if wifi_status == state.SUCCESS:
                print("✅ Zurück zum primären WLAN")
                fallback_mode = False
            else:
                print("❌ Primäres WLAN nicht verfügbar")
                fallback_mode = True
                wifi.use_fallback = True
            fallback_check_timer = time.time()

        # MQTT-Verbindung prüfen
        if not mqtt_connected:
            connect_result = mqtt.connect()
            if connect_result == mqtt.SUCCESS:
                mqtt_connected = True
                print("✅ MQTT-Verbindung hergestellt")
            else:
                print("❌ MQTT nicht erreichbar – Retry später")
                await leds.blink(leds.onboard_led, 3, 400)
                await asyncio.sleep(5)
                continue

        # Sensorwerte lesen
        sensor_status, sensor_data = sensors.read_all()
        if sensor_status != state.SUCCESS:
            print("⚠️ Sensorfehler – versuche VEML7700-Reset")
            await leds.blink(leds.onboard_led, 2, 150)
            sensors.reset_veml()
            await asyncio.sleep(5)
            continue

        # Daten senden
        send_result = mqtt.publish(sensor_data)

        if send_result == mqtt.SUCCESS:
            print("✅ Daten erfolgreich übertragen")
        elif send_result == mqtt.RECOVERED:
            print("🔁 Verbindung wiederhergestellt – nächster Zyklus")
        elif send_result == mqtt.FATAL_ERROR:
            print("❌ Senden fehlgeschlagen – MQTT getrennt")
            mqtt_connected = False
            await leds.blink(leds.onboard_led, 3, 400)
            await asyncio.sleep(5)
            continue

        await asyncio.sleep(config.UPDATE_INTERVAL)

# 🟢 Starte das asyncio-Event-Loop-System
try:
    asyncio.run(main())
finally:
    asyncio.new_event_loop()
