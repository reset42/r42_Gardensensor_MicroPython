from machine import Pin
import uasyncio as asyncio
import config

# Pins direkt aus config.py
onboard_led = Pin(config.ONBOARD_LED, Pin.OUT)
status_led = Pin(config.STATUS_LED, Pin.OUT)

def on(led: Pin):
    led.on()

def off(led: Pin):
    led.off()

async def blink(led: Pin, count=1, delay_ms=200):
    for _ in range(count):
        led.on()
        await asyncio.sleep_ms(delay_ms)
        led.off()
        await asyncio.sleep_ms(delay_ms)

# Shortcut für klassische Fehleranzeige
async def error_blink():
    await blink(onboard_led, count=5, delay_ms=150)
