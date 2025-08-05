# veml7700_driver.py – VEML7700 Sensor-Treiber für MicroPython

from machine import I2C, Pin
import time
from micropython import const
import config

# --- Konstanten ---
ADDR = const(0x10)
ALS_CONF_0 = const(0x00)
ALS_WH = const(0x01)
ALS_WL = const(0x02)
POW_SAV = const(0x03)
ALS = const(0x04)
WHITE = const(0x05)
INTERRUPT = const(0x06)

CONF_VALUES = {
    25: {1/8: bytearray([0x00, 0x13]), 1/4: bytearray([0x00, 0x1B]), 1: bytearray([0x00, 0x01]), 2: bytearray([0x00, 0x0B])},
    50: {1/8: bytearray([0x00, 0x12]), 1/4: bytearray([0x00, 0x1A]), 1: bytearray([0x00, 0x02]), 2: bytearray([0x00, 0x0A])},
    100:{1/8: bytearray([0x00, 0x10]), 1/4: bytearray([0x00, 0x18]), 1: bytearray([0x00, 0x00]), 2: bytearray([0x00, 0x08])},
    200:{1/8: bytearray([0x40, 0x10]), 1/4: bytearray([0x40, 0x18]), 1: bytearray([0x40, 0x00]), 2: bytearray([0x40, 0x08])},
    400:{1/8: bytearray([0x80, 0x10]), 1/4: bytearray([0x80, 0x18]), 1: bytearray([0x80, 0x00]), 2: bytearray([0x80, 0x08])},
    800:{1/8: bytearray([0xC0, 0x10]), 1/4: bytearray([0xC0, 0x18]), 1: bytearray([0xC0, 0x00]), 2: bytearray([0xC0, 0x08])}
}

GAIN_VALUES = {
    25: {1/8: 1.8432, 1/4: 0.9216, 1: 0.2304, 2: 0.1152},
    50: {1/8: 0.9216, 1/4: 0.4608, 1: 0.1152, 2: 0.0576},
    100:{1/8: 0.4608, 1/4: 0.2304, 1: 0.0288, 2: 0.0144},
    200:{1/8: 0.2304, 1/4: 0.1152, 1: 0.0288, 2: 0.0144},
    400:{1/8: 0.1152, 1/4: 0.0576, 1: 0.0144, 2: 0.0072},
    800:{1/8: 0.0876, 1/4: 0.0288, 1: 0.0072, 2: 0.0036}
}

INTERRUPT_HIGH = bytearray([0x00, 0x00])
INTERRUPT_LOW = bytearray([0x00, 0x00])
POWER_SAVE_MODE = bytearray([0x00, 0x00])

class VEML7700:
    def __init__(self, i2c=None, address=None, it=None, gain=None):
        self.address = address if address is not None else config.VEML7700_ADDRESS
        if i2c is None:
            self.i2c = I2C(0, scl=Pin(config.VEML_SCL), sda=Pin(config.VEML_SDA))
        else:
            self.i2c = i2c

        self.power_pin = Pin(config.VEML_PWR, Pin.OUT)
        self.power_pin.value(1)

        self.it = it if it is not None else config.VEML7700_IT
        self.gain_factor = gain if gain is not None else config.VEML7700_GAIN

        confValuesForIt = CONF_VALUES.get(self.it)
        gainValuesForIt = GAIN_VALUES.get(self.it)

        if confValuesForIt is not None and gainValuesForIt is not None:
            confValueForGain = confValuesForIt.get(self.gain_factor)
            gainValueForGain = gainValuesForIt.get(self.gain_factor)
            if confValueForGain is not None and gainValueForGain is not None:
                self.confValues = confValueForGain
                self.gain = gainValueForGain
            else:
                raise ValueError("Ungültiger Gain-Wert. Erlaubt: 1/8, 1/4, 1, 2")
        else:
            raise ValueError("Ungültiger Integrationszeit-Wert. Erlaubt: 25, 50, 100, 200, 400, 800")

        self.init()

    def init(self):
        self.i2c.writeto_mem(self.address, ALS_CONF_0, self.confValues)
        self.i2c.writeto_mem(self.address, ALS_WH, INTERRUPT_HIGH)
        self.i2c.writeto_mem(self.address, ALS_WL, INTERRUPT_LOW)
        self.i2c.writeto_mem(self.address, POW_SAV, POWER_SAVE_MODE)

    def read_lux(self):
        self.lux = bytearray(2)
        time.sleep(0.04)  # 40 ms Wartezeit
        self.i2c.readfrom_mem_into(self.address, ALS, self.lux)
        raw = self.lux[0] + self.lux[1] * 256
        lux = raw * self.gain
        return int(round(lux))
