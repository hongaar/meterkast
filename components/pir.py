import RPi.GPIO as GPIO


class PIR:
    PIR_PIN = 21

    callback = None

    def __init__(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.PIR_PIN, GPIO.IN)

    def probe(self):
        return int(GPIO.input(self.PIR_PIN))

    def event_setup(self, callback):
        self.callback = callback

    def event_start(self):
        GPIO.add_event_detect(self.PIR_PIN, GPIO.BOTH, callback=self.event_callback,
                              bouncetime=200)

    def event_callback(self, channel):
        status = self.probe()
        self.callback(status)

    def event_stop(self):
        GPIO.remove_event_detect(self.PIR_PIN)
