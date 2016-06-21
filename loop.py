#!/usr/bin/python

import signal
import sys
import time
from components import rgb, pir, matrix, oled, p1, joystick

# Welcome
########################################################################################################################

print "Welcome to meterkast, starting loop now"

# Our main data
########################################################################################################################

data = {}

# Configuration
########################################################################################################################

SLEEP = 1 / 1 # x polls / second

STATE_AWAKE = 1
STATE_HIBERNATION = 0

STATE = None

MODE_NET = 0
MODE_WITHDRAWAL = 1
MODE_SUPPLY = 2

MODES = {
    MODE_NET: 'Net electricity',
    MODE_WITHDRAWAL: 'Consumption',
    MODE_SUPPLY: 'Production'
}

MODE = MODE_NET

RGB_BRIGHTNESS_AWAKE = 50# 0 ... 255
RGB_BRIGHTNESS_HIBERNATION = 30

MATRIX_BRIGHTNESS = 1 # 0 ... 15

WATT_MAX = 500

# Setup classes
########################################################################################################################

_matrix = matrix.Matrix()
_pir = pir.PIR()
_rgb = rgb.RGB()
_oled = oled.OLED()
_p1 = p1.P1()
_joystick = joystick.Joystick()

# Bye
########################################################################################################################

def signal_handler(signal, frame):
    shutdown()
    sys.exit(0)

def shutdown():
    global _rgb, _matrix, _oled

    _rgb.off()
    _rgb.cleanup()

    _matrix.clear()

    _oled.clear()

    print 'Bye'

signal.signal(signal.SIGINT, signal_handler)

# Hibernate
########################################################################################################################

def hibernate():
    global _rgb, _oled, _matrix, _p1, STATE

    STATE = STATE_HIBERNATION

    _rgb.brightness(RGB_BRIGHTNESS_HIBERNATION)
    _rgb.render()

    _oled.clear()

    _matrix.clear()

    _p1.hibernation_treshold()

# Wake up
########################################################################################################################

def wakeup():
    global _rgb, _oled, _p1, STATE

    STATE = STATE_AWAKE

    _rgb.brightness(RGB_BRIGHTNESS_AWAKE)
    _rgb.render()

    _matrix.brightness(MATRIX_BRIGHTNESS)

    _p1.default_treshold()

# Initial boot
########################################################################################################################

wakeup()
_oled.main_text("Welcome")

# The Loop
########################################################################################################################

while True:

    # Movement detection

    pir_output = _pir.probe()

    if STATE == STATE_HIBERNATION and pir_output == 1:
        wakeup()

    if STATE == STATE_AWAKE and pir_output == 0:
        hibernate()

    # Get command from joystick

    force_probe = False

    if STATE == STATE_AWAKE:

        command = _joystick.status()

        if command == _joystick.LEFT:
            MODE -= 1

        if command == _joystick.RIGHT:
            MODE += 1

        if command == _joystick.CLICK:
            force_probe = True

        if MODE < 0: MODE = 2
        if MODE > 2: MODE = 0

    # Get electricity usage

    probe_interval_passed = False

    if _p1.will_probe():
        probe_interval_passed = True

    if _p1.will_probe() or force_probe:
        if STATE == STATE_AWAKE:
            _oled.sub_text("Probing...")
        _rgb.color('blue')

    if force_probe:
        data = _p1.force_probe()
    else:
        data = _p1.probe()

    # Write output

    if _p1.ELECTRICITY_CURRENT_WITHDRAWAL in data:
        watt = data[_p1.ELECTRICITY_CURRENT_WITHDRAWAL] * 1000
        watt_relative = watt / WATT_MAX

        _rgb.rgb(watt_relative * 255, 255 - (watt_relative * 255), 0)

        if probe_interval_passed:
            _matrix.update_graph(watt_relative)

        if STATE == STATE_AWAKE:
            _oled.top_text(MODES[MODE])
            _oled.sub_text("")
            _oled.main_text(str(watt) + " W")

            _matrix.graph()


    # Sleep for a while

    time.sleep(SLEEP)
