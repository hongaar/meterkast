import time
from components import data, matrix

print "Hold on..."
time.sleep(.5)
print "Ready"

_data = data.Data()
_matrix = matrix.Matrix(_data)

i = 0

while i < 9:
    i = i + 1
    _matrix.character(i)
    time.sleep(.5)

_matrix.clear()
print "Done"
