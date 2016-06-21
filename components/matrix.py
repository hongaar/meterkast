import max7219.led as led

class Matrix:

    def __init__(self, data):
        self.data = data
        self.device = led.matrix()

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
        self.data.set_list('graph', [0,0,0,0,0,0,0,0])

    def update_graph(self, height):
        height = min(int(height / 0.125), 8)

        graph_data = self.data.get_list('graph')
        graph_data = [int(i) for i in graph_data]

        graph_data.pop(0)
        graph_data.append(height)

        self.data.set_list('graph', graph_data)

    def graph(self):
        graph_data = self.data.get_list('graph')
        graph_data = [int(i) for i in graph_data]

        for x in range(0, 8):
            for y in range(0, 8):
                self.device.pixel(x, y, 0, False)

        for x in range(0, 8):
            for y in range(7, (7 - graph_data[x]), -1):
                self.device.pixel(x, y, 1, False)

        self.device.flush()