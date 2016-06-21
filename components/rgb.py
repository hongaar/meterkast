import _rpi_ws281x as ws

class RGB:

    # LED configuration.
    LED_CHANNEL = 1
    LED_COUNT = 4  # How many LEDs to light.
    LED_FREQ_HZ = 800000  # Frequency of the LED signal.  Should be 800khz or 400khz.
    LED_DMA_NUM = 5  # DMA channel to use, can be 0-14.
    LED_GPIO = 13  # GPIO connected to the LED signal line.  Must support PWM!
    LED_BRIGHTNESS = 50  # Set to 0 for darkest and 255 for brightest
    LED_INVERT = 0  # Set to 1 to invert the LED signal, good if using NPN
    # transistor as a 3.3V->5V level converter.  Keep at 0
    # for a normal/non-inverted signal.

    # Define colors which will be used by the example.  Each color is an unsigned
    # 32-bit value where the lower 24 bits define the red, green, blue data (each
    # being 8 bits long).
    DOT_COLORS = {
        'red':      [255, 0, 0],
        'green':    [0, 255, 0],
        'blue':     [0, 0, 255],

        'white':    [255, 255, 255],

        'yellow':   [255, 255, 0],
        'pink':     [255, 0, 255],
        'cyan':     [0, 255, 255]
    }

    def __init__(self):
        # Create a ws2811_t structure from the LED configuration.
        # Note that this structure will be created on the heap so you need to be careful
        # that you delete its memory by calling delete_ws2811_t when it's not needed.
        self.leds = ws.new_ws2811_t()

        # Initialize all channels to off
        for channum in range(2):
            channel = ws.ws2811_channel_get(self.leds, channum)
            ws.ws2811_channel_t_count_set(channel, 0)
            ws.ws2811_channel_t_gpionum_set(channel, 0)
            ws.ws2811_channel_t_invert_set(channel, 0)
            ws.ws2811_channel_t_brightness_set(channel, 0)

        self.channel = ws.ws2811_channel_get(self.leds, self.LED_CHANNEL)

        ws.ws2811_channel_t_count_set(self.channel, self.LED_COUNT)
        ws.ws2811_channel_t_gpionum_set(self.channel, self.LED_GPIO)
        ws.ws2811_channel_t_invert_set(self.channel, self.LED_INVERT)
        self.brightness(self.LED_BRIGHTNESS)

        ws.ws2811_t_freq_set(self.leds, self.LED_FREQ_HZ)
        ws.ws2811_t_dmanum_set(self.leds, self.LED_DMA_NUM)

        # Initialize library with LED configuration.
        resp = ws.ws2811_init(self.leds)

        if resp != 0:
            raise RuntimeError('ws2811_init failed with code {0}'.format(resp))

    def brightness(self, brightness):
        ws.ws2811_channel_t_brightness_set(self.channel, brightness)

    def rgb(self, red, green, blue):
        red = max(0, min(255, red))
        green = max(0, min(255, green))
        blue = max(0, min(255, blue))

        color = (int(red) << 16) | (int(green) << 8) | int(blue)
        self.write(color)

    def color(self, color):
        try:
            color = self.DOT_COLORS[color]
            self.rgb(color[0], color[1], color[2])
        except KeyError:
            print "[RGB] Color " + color + " not found"
            self.cleanup()

    def write(self, color):
        # Wrap following code in a try/finally to ensure cleanup functions are called
        # after library is initialized.

        try:
            # Update each LED color in the buffer.
            for i in range(self.LED_COUNT):

                # Set the LED color buffer value.
                ws.ws2811_led_set(self.channel, i, color)

            self.render()

        except BaseException:
            print "[RGB] Something went wrong"
            self.cleanup()

    def off(self):
        self.rgb(0, 0, 0)

    def render(self):
        try:
            # Send the LED color data to the hardware.
            resp = ws.ws2811_render(self.leds)
            if resp != 0:
                raise RuntimeError('ws2811_render failed with code {0}'.format(resp))

        except BaseException:
            print "[RGB] Something went wrong"
            self.cleanup()

    def cleanup(self):
        # Ensure ws2811_fini is called before the program quits.
        ws.ws2811_fini(self.leds)

        # Example of calling delete function to clean up structure memory.  Isn't
        # strictly necessary at the end of the program execution here, but is good practice.
        ws.delete_ws2811_t(self.leds)