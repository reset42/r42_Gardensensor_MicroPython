# bme280_driver.py – BME280 Sensor-Treiber für MicroPython

import time
from machine import I2C, Pin
import config
import struct

class BME280:
    def __init__(self, i2c=None, address=None):
        self.address = address if address is not None else config.BME280_ADDRESS
        if i2c is None:
            self.i2c = I2C(0, scl=Pin(config.BME_SCL), sda=Pin(config.BME_SDA))
        else:
            self.i2c = i2c

        self.power_pin = Pin(config.BME_PWR, Pin.OUT)
        self.power_pin.value(1)

        self._load_calibration()
        self._reg_write(0xF2, 0x01)  # Humidity oversampling x1
        self._reg_write(0xF4, 0x27)  # Temp and pressure oversampling x1, normal mode
        time.sleep_ms(100)

    def _reg_write(self, reg, val):
        self.i2c.writeto_mem(self.address, reg, bytes([val]))

    def _load_calibration(self):
        calib = self.i2c.readfrom_mem(self.address, 0x88, 24)
        h1 = self.i2c.readfrom_mem(self.address, 0xA1, 1)[0]
        h2_h6 = self.i2c.readfrom_mem(self.address, 0xE1, 7)

        def u8(buf, offset): return struct.unpack('<B', buf[offset:offset+1])[0]
        def s8(buf, offset): return struct.unpack('<b', buf[offset:offset+1])[0]
        def u16(buf, offset): return struct.unpack('<H', buf[offset:offset+2])[0]
        def s16(buf, offset): return struct.unpack('<h', buf[offset:offset+2])[0]

        self.dig = {
            'T1': u16(calib, 0), 'T2': s16(calib, 2), 'T3': s16(calib, 4),
            'P1': u16(calib, 6), 'P2': s16(calib, 8), 'P3': s16(calib,10),
            'P4': s16(calib,12), 'P5': s16(calib,14), 'P6': s16(calib,16),
            'P7': s16(calib,18), 'P8': s16(calib,20), 'P9': s16(calib,22),
            'H1': h1,
            'H2': s16(h2_h6, 0), 'H3': u8(h2_h6, 2),
            'H4': (h2_h6[3] << 4) | (h2_h6[4] & 0xF),
            'H5': (h2_h6[5] << 4) | (h2_h6[4] >> 4),
            'H6': s8(h2_h6, 6)
        }
        self.t_fine = 0

    def read_compensated_data(self):
        raw = self.i2c.readfrom_mem(self.address, 0xF7, 8)
        pres_raw = (raw[0] << 12) | (raw[1] << 4) | (raw[2] >> 4)
        temp_raw = (raw[3] << 12) | (raw[4] << 4) | (raw[5] >> 4)
        hum_raw = (raw[6] << 8) | raw[7]

        # Temperatur [°C]
        var1 = (((temp_raw / 16384.0) - (self.dig['T1'] / 1024.0)) * self.dig['T2'])
        var2 = ((((temp_raw / 131072.0) - (self.dig['T1'] / 8192.0)) ** 2) * self.dig['T3'])
        self.t_fine = var1 + var2
        temp = self.t_fine / 5120.0

        # Druck [hPa] (vereinfachte Formel)
        pres = (pres_raw / 256.0 / self.dig['P1']) * (
            self.dig['P5'] + (self.t_fine * self.dig['P6'] / 131072.0)
            + (self.t_fine ** 2 * self.dig['P7'] / 524288.0))
        pres = pres * 1048576.0

        # Luftfeuchte [%] (grob)
        hum = hum_raw / 1024.0

        return round(temp, 2), round(pres / 100.0, 2), round(hum, 2)
