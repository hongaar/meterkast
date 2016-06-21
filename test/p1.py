import sys
import serial

ser = serial.Serial()
ser.baudrate = 115200
ser.bytesize=serial.EIGHTBITS
ser.parity=serial.PARITY_NONE
ser.stopbits=serial.STOPBITS_ONE
ser.xonxoff=0
ser.rtscts=0
ser.timeout=20
ser.port="/dev/ttyUSB0"

# Open COM port
try:
    ser.open()
except:
    sys.exit("[P1] Error opening %s" % ser.name)

# Telegram map
TELEGRAM_MAP = {
    '1.8.1': {
        'unit': 'kWh 1 (+P)',
        'map': [0, 10]
    },
    '1.8.2': {
        'unit': 'kWh 2 (+P)',
        'map': [0, 10]
    },
    '1.7.0': {
        'unit': 'kW (+P)',
        'map': [0, 5]
    },
    '2.8.1': {
        'unit': 'kWh 1 (-P)',
        'map': [0, 10]
    },
    '2.8.2': {
        'unit': 'kWh 2 (-P)',
        'map': [0, 10]
    },
    '2.7.0': {
        'unit': 'kW (+P)',
        'map': [0, 5]
    },
    '24.2.1': {
        'unit': 'm3',
        'map': [15, 24]
    }
}

# Read telegram
while True:

    try:
        p1_raw = ser.readline()
    except:
        sys.exit("[P1] Can't read serial port %s" % ser.name)

    p1_str = str(p1_raw)
    p1_line = p1_str.strip()

    if p1_line[:1] == '!':
        break

    p1_line = p1_line[p1_line.find(":")+1:]
    p1_key = p1_line[:p1_line.find("(")]
    p1_line = p1_line[p1_line.find("(") + 1:]

    if not p1_key in TELEGRAM_MAP:
        continue

    try:
        p1_value = p1_line[TELEGRAM_MAP[p1_key]['map'][0] : TELEGRAM_MAP[p1_key]['map'][1]]
        p1_value = float(p1_value)

        print TELEGRAM_MAP[p1_key]['unit']
        print p1_value
    except ValueError:
        pass

# Close port and show status
try:
    ser.close()
except:
    sys.exit("[P1] Can't close serial port %s" % ser.name)