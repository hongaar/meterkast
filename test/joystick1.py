import sys
sys.path.insert(0, '..')

import time

from components import joystick

_joystick = joystick.Joystick()

i = 0

while True:

    status = _joystick.status()

    print status

    time.sleep(.0001)
