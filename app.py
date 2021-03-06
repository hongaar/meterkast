#!/usr/bin/python

import datetime
import signal
import sys
import time

import RPi.GPIO as GPIO

from components import rebooter, rgb, pir, matrix, oled, continuousP1, joystick, writer, data

# Setup classes
###################################################################################################

debug = False

_data = data.Data()

_matrix = matrix.Matrix(_data)
_pir = pir.PIR()
_rgb = rgb.RGB()
_oled = oled.OLED()
_joystick = joystick.Joystick()

_p1 = continuousP1.P1()
_writer = writer.Writer(_data)


# SIGINT handler
###################################################################################################

def signal_handler(signal, frame):
    global main

    main.shutdown()
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)

# Loop vars
###################################################################################################

TICK_SECONDS = 1
TICK_RESTART_AFTER = (60 * 60 * 24) / TICK_SECONDS

tick_counter = 0


# The controller
###################################################################################################

class Controller:
    # State constants
    STATE_AWAKE = 1
    STATE_HIBERNATION = 0

    # Mode constants
    MODE_ELECTRICITY = 0
    MODE_GAS = 1
    MODES = {
        MODE_ELECTRICITY: 'Electriciteit',
        MODE_GAS: 'Gas'
    }

    # Time constants
    TIME_NOW = 0
    TIME_HOUR = 1
    TIME_DAY = 2
    TIME_WEEK = 3
    TIME_MONTH = 4
    TIME_YEAR = 5
    TIMES = {
        TIME_NOW: 'now',
        TIME_HOUR: 'hour',
        TIME_DAY: 'day',
        TIME_WEEK: 'week',
        TIME_MONTH: 'month',
        TIME_YEAR: 'year'
    }

    RGB_BRIGHTNESS_AWAKE = 50  # 0 ... 255
    RGB_BRIGHTNESS_HIBERNATION = 20

    MATRIX_BRIGHTNESS = 1  # 0 ... 15

    CONS_WATT_MIN = 100
    CONS_WATT_MAX = 500

    PROD_WATT_MIN = 0
    PROD_WATT_MAX = 1000

    state = None
    mode = MODE_ELECTRICITY
    time = TIME_NOW

    def __init__(self):
        self.p1 = _p1
        self.joystick = _joystick
        self.rgb = _rgb
        self.matrix = _matrix
        self.pir = _pir
        self.oled = _oled
        self.writer = _writer
        self.data = _data

    def bootstrap(self):
        self.log('Starting app')

        if self.pir.probe():
            self.wakeup()
        else:
            self.hibernate()

        self.pir.event_setup(self.pir_event)
        self.pir.event_start()

        self.joystick.event_setup(self.joystick_event)
        self.joystick.event_start()

        self.p1.event_setup(self.p1_probed)
        self.p1.event_start()

        self.log('Bootstrap success')

    def shutdown(self):
        self.joystick.event_stop()
        self.pir.event_stop()

        time.sleep(.1)

        self.p1.event_stop()

        self.rgb.off()
        self.rgb.cleanup()
        self.matrix.clear()
        self.oled.clear()

        time.sleep(.1)

        GPIO.cleanup()

        self.log('Bye')

    @staticmethod
    def log(message):
        print(datetime.datetime.utcnow().isoformat() + ": " + str(message))

    # Hibernation
    def hibernate(self):
        self.log('Hibernating')

        self.state = self.STATE_HIBERNATION

        self.rgb.brightness(self.RGB_BRIGHTNESS_HIBERNATION)
        self.rgb.render()

        self.oled.clear()

        self.matrix.clear()

        self.p1.hibernate()

    def wakeup(self):
        self.log('Waking up')

        self.state = self.STATE_AWAKE

        self.rgb.brightness(self.RGB_BRIGHTNESS_AWAKE)
        self.rgb.render()

        self.matrix.brightness(self.MATRIX_BRIGHTNESS)

        self.p1.wakeup()

        self.display()

    def is_awake(self):
        return self.state == self.STATE_AWAKE

    # Movement detection
    def pir_event(self, status):
        if not self.is_awake() and status == 1:
            self.log('PIR status changed to high')
            self.wakeup()

        if self.is_awake() and status == 0:
            self.log('PIR status changed to low')
            self.hibernate()

    # Get command from joystick
    def joystick_event(self, command):
        if not self.is_awake():
            self.wakeup()

        if command == self.joystick.CLICK:
            self.log('Got CLICK input')
            rebooter.restart()
            return

        if command == self.joystick.RIGHT:
            self.log('Got RIGHT input')
            self.mode += 1
            if self.mode > 1:
                self.mode = 0

        if command == self.joystick.LEFT:
            self.log('Got LEFT input')
            self.mode -= 1
            if self.mode < 0:
                self.mode = 1

        if command == self.joystick.BOTTOM:
            self.log('Got DOWN input')
            self.time += 1
            if self.time > 5:
                self.time = 0

        if command == self.joystick.TOP:
            self.log('Got UP input')
            self.time -= 1
            if self.time < 0:
                self.time = 5

        self.display()

    # Electricity usage
    def p1_probed(self, p1_data):
        self.log('P1 probing success')

        self.parse_data(p1_data)
        self.write_data()
        self.tick()
        self.display()

    def parse_data(self, p1_data):
        self.data.reset([
            'cons_w',
            'cons_w_rel',
            'cons_cnt',
            'prod_w',
            'prod_w_rel',
            'prod_cnt',
            'gas_cnt'
        ])

        if self.p1.ELECTRICITY_CURRENT_WITHDRAWAL in p1_data:
            self.data.set('cons_w', p1_data[self.p1.ELECTRICITY_CURRENT_WITHDRAWAL] * 1000)
            self.data.set('cons_w_rel', (self.data.get('cons_w') - self.CONS_WATT_MIN) / (
                    self.CONS_WATT_MAX - self.CONS_WATT_MIN))

        if self.p1.ELECTRICITY_CURRENT_SUPPLY in p1_data:
            self.data.set('prod_w', p1_data[self.p1.ELECTRICITY_CURRENT_SUPPLY] * 1000)
            self.data.set('prod_w_rel', (self.data.get('prod_w') - self.PROD_WATT_MIN) / (
                    self.PROD_WATT_MAX - self.PROD_WATT_MIN))

        if self.p1.ELECTRICITY_1_WITHDRAWAL_CUMULATIVE in p1_data and self.p1.ELECTRICITY_2_WITHDRAWAL_CUMULATIVE in p1_data:
            self.data.set('cons_cnt',
                          p1_data[self.p1.ELECTRICITY_1_WITHDRAWAL_CUMULATIVE] + p1_data[
                              self.p1.ELECTRICITY_2_WITHDRAWAL_CUMULATIVE])

        if self.p1.ELECTRICITY_1_SUPPLY_CUMULATIVE in p1_data and self.p1.ELECTRICITY_2_SUPPLY_CUMULATIVE in p1_data:
            self.data.set('prod_cnt', p1_data[self.p1.ELECTRICITY_1_SUPPLY_CUMULATIVE] + p1_data[
                self.p1.ELECTRICITY_2_SUPPLY_CUMULATIVE])

        if self.p1.GAS_CUMULATIVE in p1_data:
            self.data.set('gas_cnt', p1_data[self.p1.GAS_CUMULATIVE])

        self.log('P1 parsed data: ' + str(p1_data))

    def write_data(self):
        self.log('Writing data')
        self.writer.write(self.data.get('cons_cnt'), self.data.get('prod_cnt'),
                          self.data.get('gas_cnt'))

    # Update displays
    def tick(self):
        if self.data.get('cons_w') > 0:
            self.rgb.rgb(self.data.get('cons_w_rel') * 255,
                         255 - (self.data.get('cons_w_rel') * 255), 0)
            self.matrix.update_graph(self.data.get('cons_w_rel'))
        else:
            self.rgb.rgb(0, self.data.get('prod_w_rel') * 255,
                         255 - (self.data.get('prod_w_rel') * 255))
            self.matrix.update_graph(self.data.get('prod_w_rel'))

    def display(self):
        if self.is_awake():
            self.matrix.graph()
            self.oled.top_text(self.MODES[self.mode], False)

            if self.mode == self.MODE_ELECTRICITY:
                if self.time == self.TIME_NOW:
                    self.oled.main_text(
                        str(self.data.get('cons_w') - self.data.get('prod_w')) + " W", False)
                    self.oled.sub_text(self.TIMES[self.time], False)
                else:
                    self.oled.main_text(
                        str(self.data.get('cons_avg_' + self.TIMES[self.time])) + " kWh", False)
                    self.oled.sub_text('last ' + self.TIMES[self.time], False)

            elif self.mode == self.MODE_GAS:
                if self.time == self.TIME_NOW:
                    self.oled.main_text('n/a', False)
                    self.oled.sub_text(self.TIMES[self.time], False)
                else:
                    self.oled.main_text(
                        str(self.data.get('gas_avg_' + self.TIMES[self.time])) + " m3", False)
                    self.oled.sub_text('last ' + self.TIMES[self.time], False)

            self.oled.build_text()


# Create controller
main = Controller()

main.bootstrap()

# Start loop
while True:
    tick_counter = tick_counter + 1
    if tick_counter > TICK_RESTART_AFTER:
        rebooter.restart()

    time.sleep(TICK_SECONDS)
