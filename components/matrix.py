import max7219.led as led

class Matrix:

    graph_data = []

    def __init__(self):
        self.device = led.matrix()
        self.reset_graph()

    def clear(self):
        self.device.clear()

    def brightness(self, intensity):
        self.device.brightness(intensity)

    def character(self, character):
        self.device.letter(0, ord(str(character)))

    def message(self, message):
        self.device.show_message(message)

    def height(self, height):
        height = min(int(height / 0.125), 8)

        for x in range(0, 8):
            for y in range(0, 8):
                self.device.pixel(x, y, 0, False)

        for x in range(0, 8):
            for y in range(7, (7 - height), -1):
                self.device.pixel(x, y, 1, False)

        self.device.flush()

    def reset_graph(self):
        self.graph_data = [0,0,0,0,0,0,0,0]

    def update_graph(self, height):
        height = min(int(height / 0.125), 8)

        self.graph_data.pop(0)
        self.graph_data.append(height)

    def graph(self):
        for x in range(0, 8):
            for y in range(0, 8):
                self.device.pixel(x, y, 0, False)

        for x in range(0, 8):
            for y in range(7, (7 - self.graph_data[x]), -1):
                self.device.pixel(x, y, 1, False)

        self.device.flush()