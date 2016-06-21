import RPi.GPIO as GPIO
from lib import max7219 as led
import time

PIR_PIN = 21

GPIO.setmode(GPIO.BCM)
GPIO.setup(PIR_PIN, GPIO.IN)

device = led.matrix()
device.clear()

print "Hold on..."
time.sleep(.5)
print "Ready"

i = 0

while True:
    #i = i + 1
    device.letter(0, ord(str(GPIO.input(PIR_PIN))))
    #device.letter(0, i)

    time.sleep(.1)
