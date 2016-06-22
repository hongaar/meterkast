import sys
import datetime
import serial
import random
import time

class P1:

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

    debug_cumulative = 0

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

    def probe(self):
        # read serial port until we get all the data we need
        while True:
            data = self.read_serial_port()

            if len(data) >= len(self.TELEGRAM_MAP):
                break

        return data

    def read_serial_port(self):

        if self.debug:
            self.debug_cumulative += random.uniform(0.0833333333333333, 0.0833333333333333)
            return {
                self.ELECTRICITY_CURRENT_WITHDRAWAL: random.uniform(0, .5),
                self.ELECTRICITY_1_WITHDRAWAL_CUMULATIVE: self.debug_cumulative,
                self.ELECTRICITY_2_WITHDRAWAL_CUMULATIVE: 0
            }

        data = {}

        # Open COM port
        try:
            self.ser.open()
        except:
            sys.exit("[P1] Error opening %s" % self.ser.name)

        # Read telegram
        while True:

            try:
                p1_raw = self.ser.readline()
            except:
                sys.exit("[P1] Can't read serial port %s" % self.ser.name)

            p1_str = str(p1_raw)
            p1_line = p1_str.strip()

            # raw log
            with open("/home/pi/code/var/p1.log", "a") as log:
                log.write(datetime.datetime.utcnow().isoformat() + ": " + p1_line + "\n")

            if p1_line[:1] == '!':
                break

            p1_line = p1_line[p1_line.find(":") + 1:]
            p1_key = p1_line[:p1_line.find("(")]
            p1_line = p1_line[p1_line.find("(") + 1:]

            if not p1_key in self.TELEGRAM_MAP:
                continue

            try:
                p1_value = p1_line[self.TELEGRAM_MAP[p1_key]['map'][0]: self.TELEGRAM_MAP[p1_key]['map'][1]]
                p1_value = float(p1_value)

                data[p1_key] = p1_value
            except ValueError:
                # incomplete telegram
                return {}

            time.sleep(.01)

        # Close port and show status
        try:
            self.ser.close()
        except:
            sys.exit("[P1] Can't close serial port %s" % self.ser.name)

        return data