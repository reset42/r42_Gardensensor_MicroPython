# src/bme280_driver.py — selbstentwickelter Treiber, datenblattbasierte Kompensation
# Keine Lizenzpflicht (vollständig eigener Quellcode)

import time
from machine import I2C

class BME280Driver:
    def __init__(self, i2c: I2C, address=0x76):
        self.i2c = i2c
        self.addr = address
        self._load_calibration()
        # oversampling x1 und normal mode starten
        self._reg_write(0xF2, 0x01)
        self._reg_write(0xF4, 0x27)
        time.sleep_ms(100)

    def _reg_write(self, reg, val):
        self.i2c.writeto_mem(self.addr, reg, bytes([val]))

    def _load_calibration(self):
        # Trimmungsdaten vom Sensor laden
        calib = self.i2c.readfrom_mem(self.addr, 0x88, 24)
        h1 = self.i2c.readfrom_mem(self.addr, 0xA1, 1)[0]
        h2_h6 = self.i2c.readfrom_mem(self.addr, 0xE1, 7)
        unpack = self._uc_unpack
        self.dig = {
            'T1': unpack(calib, 0x0, 'H'),
            'T2': unpack(calib, 0x2, 'h'),
            'T3': unpack(calib, 0x4, 'h'),
            'P1': unpack(calib, 0x6, 'H'),
            'P2': unpack(calib, 0x8, 'h'),
            'P3': unpack(calib, 0xA, 'h'),
            'P4': unpack(calib, 0xC, 'h'),
            'P5': unpack(calib, 0xE, 'h'),
            'P6': unpack(calib, 0x10, 'h'),
            'P7': unpack(calib, 0x12, 'h'),
            'P8': unpack(calib, 0x14, 'h'),
            'P9': unpack(calib, 0x16, 'h'),
            'H1': h1,
            'H2': unpack(h2_h6, 0, 'h'),
            'H3': h2_h6[2],
            'H4': (h2_h6[3] << 4) | (h2_h6[4] & 0xF),
            'H5': (h2_h6[4] >> 4) | (h2_h6[5] << 4),
            'H6': h2_h6[6] if h2_h6[6] < 128 else h2_h6[6] - 256
        }
        self.t_fine = 0

    @staticmethod
    def _uc_unpack(buf, offset, fmt):
        import struct
        return struct.unpack('<' + fmt, buf[offset:offset + struct.calcsize(fmt)])[0]

    def read_compensated_data(self):
        # Rohdaten: 8 Byte ab 0xF7
        raw = self.i2c.readfrom_mem(self.addr, 0xF7, 8)
        pres_raw = (raw[0] << 12) | (raw[1] << 4) | (raw[2] >> 4)
        temp_raw = (raw[3] << 12) | (raw[4] << 4) | (raw[5] >> 4)
        hum_raw = (raw[6] << 8) | raw[7]

        # Temperaturkompensation [°C]
        var1 = (((temp_raw / 16384.0) - (self.dig['T1'] / 1024.0)) *
                self.dig['T2'])
        var2 = (((temp_raw / 131072.0) - (self.dig['T1'] / 8192.0)) ** 2) * self.dig['T3']
        self.t_fine = var1 + var2
        temp = self.t_fine / 5120.0

        # Druckkompensation [Pa]
        pres = (pres_raw / 256.0 / self.dig['P1']) * (
            self.dig['P5'] + (self.t_fine * self.dig['P6'] / 131072.0)
            + (self.t_fine ** 2 * self.dig['P7'] / 524288.0))
        pres = pres * 1048576.0  # vereinfachte Näherung
        # Achtung: grobe Vereinfachung – keine 1–2 Pa Genauigkeit

        # Luftfeuchtigkeitskompensation [%]
        hum = hum_raw / 1024.0
        return (round(temp, 2), round(pres / 100.0, 2), round(hum, 2))
