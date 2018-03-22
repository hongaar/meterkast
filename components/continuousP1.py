#!/usr/bin/env python

import datetime
import serial
import time
from multiprocessing import Process
from rebooter import reboot


class P1:
    FAIL_THRESHOLD = 100

    ELECTRICITY_1_WITHDRAWAL_CUMULATIVE = '1.8.1'
    ELECTRICITY_2_WITHDRAWAL_CUMULATIVE = '1.8.2'
    ELECTRICITY_1_SUPPLY_CUMULATIVE = '2.8.1'
    ELECTRICITY_2_SUPPLY_CUMULATIVE = '2.8.2'
    ELECTRICITY_CURRENT_WITHDRAWAL = '1.7.0'
    ELECTRICITY_CURRENT_SUPPLY = '2.7.0'
    GAS_CUMULATIVE = '24.2.1'

    TELEGRAM_MAP = {
        ELECTRICITY_1_WITHDRAWAL_CUMULATIVE: {
            'unit': 'kWh 1 (+P)',
            'map': [0, 10]
        },
        ELECTRICITY_2_WITHDRAWAL_CUMULATIVE: {
            'unit': 'kWh 2 (+P)',
            'map': [0, 10]
        },
        ELECTRICITY_CURRENT_WITHDRAWAL: {
            'unit': 'kW (+P)',
            'map': [0, 5]
        },
        ELECTRICITY_1_SUPPLY_CUMULATIVE: {
            'unit': 'kWh 1 (-P)',
            'map': [0, 10]
        },
        ELECTRICITY_2_SUPPLY_CUMULATIVE: {
            'unit': 'kWh 2 (-P)',
            'map': [0, 10]
        },
        ELECTRICITY_CURRENT_SUPPLY: {
            'unit': 'kW (+P)',
            'map': [0, 5]
        },
        GAS_CUMULATIVE: {
            'unit': 'm3',
            'map': [15, 24]
        }
    }

    callback = None
    timer = None

    def __init__(self, debug=False):
        ser = serial.Serial()
        ser.baudrate = 115200
        ser.bytesize = serial.EIGHTBITS
        ser.parity = serial.PARITY_NONE
        ser.stopbits = serial.STOPBITS_ONE
        ser.xonxoff = 0
        ser.rtscts = 0
        ser.timeout = 20
        ser.port = "/dev/ttyUSB0"

        self.debug = debug
        self.ser = ser

    def ser_open(self):
        # Open COM port
        try:
            self.ser.open()
        except:
            reboot(1)
            raise RuntimeError("[P1] Error opening %s" % self.ser.name)

    def ser_close(self):
        # Close port and show status
        try:
            self.ser.close()
        except:
            reboot(1)
            raise RuntimeError("[P1] Can't close serial port %s" % self.ser.name)

    def wakeup(self):
        pass

    def hibernate(self):
        pass

    def event_setup(self, callback):
        self.callback = callback

    def event_start(self):
        self.ser_open()
        self.timer = Process(target=self.event_loop)
        self.timer.start()

    def event_stop(self):
        if self.timer is not None and self.timer.is_alive():
            try:
                self.timer.terminate()
                self.ser_close()
            except AttributeError:
                print("[CONTINUOUS_P1] Could not terminate timer")

    def event_loop(self):
        data = {}
        fail_counter = 0

        # Read telegram
        while True:
            try:
                p1_raw = self.ser.readline()
            except:
                self.debug_log("Can't read serial port %s" % self.ser.name)
                fail_counter = fail_counter + 1
                if fail_counter > self.FAIL_THRESHOLD:
                    print("[CONTINUOUS_P1] Giving up reading serial port %s" % self.ser.name)
                    reboot()

                time.sleep(1)
                continue

            fail_counter = 0

            p1_str = str(p1_raw)
            p1_line = p1_str.strip()

            self.debug_log(p1_line)

            if p1_line[:1] == '!':
                self.event_callback(data)
                self.debug_log("^^^ end")
                data = {}

            p1_line = p1_line[p1_line.find(":") + 1:]
            p1_key = p1_line[:p1_line.find("(")]
            p1_line = p1_line[p1_line.find("(") + 1:]

            if p1_key not in self.TELEGRAM_MAP:
                self.debug_log("^^^ skip")
                continue

            try:
                p1_value = p1_line[
                           self.TELEGRAM_MAP[p1_key]['map'][0]: self.TELEGRAM_MAP[p1_key]['map'][
                               1]]
                p1_value = float(p1_value)

                data[p1_key] = p1_value
                self.debug_log("^^^ save")
            except ValueError:
                self.debug_log("^^^ incomplete")

    def event_callback(self, data):
        # only fire callback if we get all the data we need
        if len(data) >= len(self.TELEGRAM_MAP):
            self.callback(data)

    def debug_log(self, message):
        # Log debug messages
        if self.debug:
            with open("/home/pi/code/var/p1.log", "a") as log:
                log.write(datetime.datetime.utcnow().isoformat() + ": " + message + "\n")
