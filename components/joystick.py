#!/usr/bin/env python

import time
import RPi.GPIO as GPIO
from multiprocessing import Process


class Joystick:
    CHANNEL_X = 1
    CHANNEL_Y = 0  # + button channel

    AVG = 256 * 2
    MIN = 256
    MAX = 256 * 3
    THRESHOLD_BUTTON = 256 * 4

    THRESHOLD = 150

    IDLE = 0
    LEFT = 1
    RIGHT = 2
    TOP = 3
    BOTTOM = 4
    CLICK = 5

    # change these as desired - they're the pins connected from the
    # SPI port on the ADC to the Cobbler
    SPICLK = 18
    SPIMISO = 23
    SPIMOSI = 24
    SPICS = 25

    callback = None
    timer = None

    def __init__(self):
        GPIO.setmode(GPIO.BCM)

        # set up the SPI interface pins
        GPIO.setup(self.SPIMOSI, GPIO.OUT)
        GPIO.setup(self.SPIMISO, GPIO.IN)
        GPIO.setup(self.SPICLK, GPIO.OUT)
        GPIO.setup(self.SPICS, GPIO.OUT)

    def readadc(self, adcnum):
        clockpin = self.SPICLK
        mosipin = self.SPIMOSI
        misopin = self.SPIMISO
        cspin = self.SPICS

        # read SPI data from MCP3008 chip, 8 possible adc's (0 thru 7)
        if (adcnum > 7) or (adcnum < 0):
            return -1
        GPIO.output(cspin, True)

        GPIO.output(clockpin, False)  # start clock low
        GPIO.output(cspin, False)  # bring CS low

        commandout = adcnum
        commandout |= 0x18  # start bit + single-ended bit
        commandout <<= 3  # we only need to send 5 bits here
        for i in range(5):
            if commandout & 0x80:
                GPIO.output(mosipin, True)
            else:
                GPIO.output(mosipin, False)
            commandout <<= 1
            GPIO.output(clockpin, True)
            GPIO.output(clockpin, False)

        adcout = 0
        # read in one empty bit, one null bit and 10 ADC bits
        for i in range(12):
            GPIO.output(clockpin, True)
            GPIO.output(clockpin, False)
            adcout <<= 1
            if GPIO.input(misopin):
                adcout |= 0x1

        GPIO.output(cspin, True)

        adcout >>= 1  # first bit is 'null' so drop it
        return adcout

    def status(self):
        x = self.readadc(self.CHANNEL_X)
        y = click = self.readadc(self.CHANNEL_Y)

        if click > (self.THRESHOLD_BUTTON - self.THRESHOLD):
            return self.CLICK

        if x < (self.MIN + self.THRESHOLD):
            return self.LEFT

        if x > (self.MAX - self.THRESHOLD):
            return self.RIGHT

        if y < (self.MIN + self.THRESHOLD):
            return self.TOP

        if y > (self.MAX - self.THRESHOLD):
            return self.BOTTOM

        return self.IDLE

    def event_setup(self, callback):
        self.callback = callback

    def event_start(self):
        self.timer = Process(target=self.event_loop)
        self.timer.start()

    def event_stop(self):
        if self.timer is not None and self.timer.is_alive():
            try:
                self.timer.terminate()
            except AttributeError:
                print("[JOYSTICK] Could not terminate timer")

    def event_loop(self):
        wait_for_idle = False
        while True:
            command = self.status()

            if command != self.IDLE and wait_for_idle == False:
                self.event_callback(command)
                wait_for_idle = True
            elif command == self.IDLE:
                wait_for_idle = False

            time.sleep(1.0 / 30)

    def event_callback(self, command):
        self.callback(command)
