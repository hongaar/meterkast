#!/usr/bin/python

import datetime
import signal
import sys
import time

import RPi.GPIO as GPIO

from components import rgb, pir, matrix, oled, p1, joystick, timedReader, writer, data

# Setup classes
########################################################################################################################

debug = False

_data = data.Data()

_matrix = matrix.Matrix()
_pir = pir.PIR()
_rgb = rgb.RGB()
_oled = oled.OLED()
_joystick = joystick.Joystick()

_p1 = p1.P1(debug)
_reader = timedReader.TimedReader(_p1, debug)
_writer = writer.Writer()

# SIGINT handler
########################################################################################################################

def signal_handler(signal, frame):
    global main

    main.shutdown()

    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

# The controller
########################################################################################################################

class Controller:

    # Constants
    STATE_AWAKE = 1
    STATE_HIBERNATION = 0

    MODE_ELECTRICITY = 0
    MODE_GAS = 1

    MODES = {
        MODE_ELECTRICITY: 'Electriciteit',
        MODE_GAS: 'Gas'
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

    def __init__(self):
        self.p1 = _p1
        self.joystick = _joystick
        self.rgb = _rgb
        self.matrix = _matrix
        self.pir = _pir
        self.oled = _oled
        self.reader = _reader
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

        self.reader.event_probing_setup(self.p1_probing)
        self.reader.event_probed_setup(self.p1_probed)
        self.reader.event_start()

        self.log('Bootstrap success')

    def shutdown(self):
        self.joystick.event_stop()
        self.pir.event_stop()

        time.sleep(.1)

        self.reader.event_stop()

        self.rgb.off()
        self.rgb.cleanup()
        self.matrix.clear()
        self.oled.clear()

        time.sleep(.1)

        GPIO.cleanup()

        self.log('Bye')

    @staticmethod
    def log(message):
        print (datetime.datetime.utcnow().isoformat() + ": " + str(message))

    # Hibernation

    def hibernate(self):
        self.log('Hibernating')

        self.state = self.STATE_HIBERNATION

        self.rgb.brightness(self.RGB_BRIGHTNESS_HIBERNATION)
        self.rgb.render()

        self.oled.clear()

        self.matrix.clear()

        self.reader.hibernate()

    def wakeup(self):
        self.log('Waking up')

        self.state = self.STATE_AWAKE

        self.rgb.brightness(self.RGB_BRIGHTNESS_AWAKE)
        self.rgb.render()

        self.matrix.brightness(self.MATRIX_BRIGHTNESS)

        self.reader.wakeup()

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

        if command == _joystick.CLICK:
            self.log('Got CLICK input')
            self.p1_manual()
            return

        if command == self.joystick.LEFT:
            self.log('Got LEFT input')
            self.matrix.reset_graph()
            self.mode -= 1
            if self.mode < 0: self.mode = 1

        if command == self.joystick.RIGHT:
            self.log('Got RIGHT input')
            self.matrix.reset_graph()
            self.mode += 1
            if self.mode > 1: self.mode = 0

        self.display()

    # Electricity usage

    def p1_manual(self):
        self.log('P1 manual probe triggered')

        self.p1_probing()
        self.p1_probed(self.p1.probe())

    def p1_probing(self):
        self.log('P1 probing started')

        if self.is_awake():
            self.oled.sub_text("Meten is weten")

        self.rgb.color('pink')

    def p1_probed(self, p1_data):
        self.log('P1 probing success')

        self.parse_data(p1_data)
        self.write_data()
        self.tick()
        self.display()

    def parse_data(self, p1_data):
        if self.p1.ELECTRICITY_CURRENT_WITHDRAWAL in p1_data:
            self.data.set('cons_w', p1_data[self.p1.ELECTRICITY_CURRENT_WITHDRAWAL] * 1000)
            self.data.set('cons_w_rel', (self.data.get('cons_w') - self.CONS_WATT_MIN) / (self.CONS_WATT_MAX - self.CONS_WATT_MIN))

        if self.p1.ELECTRICITY_CURRENT_SUPPLY in p1_data:
            self.data.set('prod_w', p1_data[self.p1.ELECTRICITY_CURRENT_SUPPLY] * 1000)
            self.data.set('prod_w_rel', (self.data.get('prod_w') - self.PROD_WATT_MIN) / (self.PROD_WATT_MAX - self.PROD_WATT_MIN))

        if self.p1.ELECTRICITY_1_WITHDRAWAL_CUMULATIVE in p1_data and self.p1.ELECTRICITY_2_WITHDRAWAL_CUMULATIVE in p1_data:
            self.data.set('cons_cnt', p1_data[self.p1.ELECTRICITY_1_WITHDRAWAL_CUMULATIVE] + p1_data[self.p1.ELECTRICITY_2_WITHDRAWAL_CUMULATIVE])

        if self.p1.ELECTRICITY_1_SUPPLY_CUMULATIVE in p1_data and self.p1.ELECTRICITY_2_SUPPLY_CUMULATIVE in p1_data:
            self.data.set('prod_cnt', p1_data[self.p1.ELECTRICITY_1_SUPPLY_CUMULATIVE] + p1_data[self.p1.ELECTRICITY_2_SUPPLY_CUMULATIVE])

        if self.p1.GAS_CUMULATIVE in p1_data:
            self.data.set('gas_cnt', p1_data[self.p1.GAS_CUMULATIVE])

        self.log('P1 parsed data: ' + str(self.data.all()))

    def write_data(self):
        if self.data.get('cons_cnt') > 0:
            self.log('Writing data')
            self.writer.write(self.data.get('cons_cnt'), self.data.get('prod_cnt'), self.data.get('gas_cnt'))

    # Update displays

    def tick(self):
        if self.mode == self.MODE_ELECTRICITY:
            if self.data.get('cons_w') > 0:
                self.rgb.rgb(self.data.get('cons_w_rel') * 255, 255 - (self.data.get('cons_w_rel') * 255), 0)
                self.matrix.update_graph(self.data.get('cons_w_rel'))
            else:
                self.rgb.rgb(0, self.data.get('prod_w_rel') * 255, 255 - (self.data.get('prod_w_rel') * 255))
                self.matrix.update_graph(self.data.get('prod_w_rel'))

        elif self.mode == self.MODE_GAS:
            self.rgb.color('yellow')

    def display(self):
        if self.is_awake():
            self.matrix.graph()
            self.oled.top_text(self.MODES[self.mode])
            self.oled.sub_text("")

            if self.mode == self.MODE_ELECTRICITY:
                self.oled.main_text(str(self.data.get('cons_w') - self.data.get('prod_w')) + " W")

            elif self.mode == self.MODE_GAS:
                self.oled.main_text(str(self.data.get('gas_cnt')) + " m3")


# Create controller
main = Controller()

main.bootstrap()

# Start loop
while True:
    time.sleep(1)