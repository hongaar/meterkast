from pprint import pprint
import time
from components import continuousP1

print "Hold on..."
time.sleep(.5)
print "Ready"


def show(data):
    pprint(data)


_p1 = continuousP1.P1()

_p1.event_setup(show)
_p1.event_start()

print "Done"
