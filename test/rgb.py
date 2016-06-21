import sys
sys.path.insert(0, '..')

import time

from components import rgb

_rgb = rgb.RGB()

i = 0

while True:

    print "set rgb value: " + str(i)
    _rgb.rgb(i, i, i)
    _rgb.brightness(255)

    i += 1

    time.sleep(.05)
