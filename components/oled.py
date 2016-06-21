import Adafruit_SSD1306

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont


class OLED:

    # Raspberry Pi pin configuration:
    RST = 24

    # Note the following are only used with SPI:
    DC = 23
    SPI_PORT = 0
    SPI_DEVICE = 0

    text_top = ''
    text_main = ''
    text_sub = ''

    def __init__(self):

        # 128x64 display with hardware I2C:
        self.disp = Adafruit_SSD1306.SSD1306_128_64(rst=self.RST)

        # Initialize library.
        self.disp.begin()

    def simple_text(self, text):
        # Create blank image for drawing.
        # Make sure to create image with mode '1' for 1-bit color.
        w = self.disp.width
        h = self.disp.height
        image = Image.new('1', (w, h))

        # Get drawing object to draw on image.
        draw = ImageDraw.Draw(image)

        # Draw a black filled box to clear the image.
        draw.rectangle((0, 0, w, h), outline=0, fill=0)

        # Load default font.
        #font = ImageFont.load_default()

        # Alternatively load a TTF font.  Make sure the .ttf font file is in the same directory as the python script!
        # Some other nice fonts to try: http://www.dafont.com/bitmap.php
        font = ImageFont.truetype('/home/pi/code/components/VCR_OSD_MONO_1.001.ttf', 21)

        # Text dimensions
        tw, th = draw.textsize(text, font=font)

        # Write text.
        draw.text(((w-tw) / 2, (h-th) / 2), text, font=font, fill=255)

        # Display image.
        self.disp.image(image)
        self.disp.display()

    def top_text(self, text):
        self.text_top = text
        self.build_text()

    def main_text(self, text):
        self.text_main = text
        self.build_text()

    def sub_text(self, text):
        self.text_sub = text
        self.build_text()

    def full_text(self, top_text, main_text, sub_text):
        self.text_top = top_text
        self.text_main = main_text
        self.text_sub = sub_text
        self.build_text()

    def build_text(self):
        # Create blank image for drawing.
        # Make sure to create image with mode '1' for 1-bit color.
        w = self.disp.width
        h = self.disp.height
        padding = 2
        small_font = 12
        big_font = 21
        image = Image.new('1', (w, h))

        # Get drawing object to draw on image.
        draw = ImageDraw.Draw(image)

        # Draw a black filled box to clear the image.
        draw.rectangle((0, 0, w, h), outline=0, fill=0)

        # Load default font for top / sub texts
        font = ImageFont.load_default()

        # Top text
        tw, th = draw.textsize(self.text_top, font=font)
        draw.text(((w - tw) / 2, padding), self.text_top, font=font, fill=255)

        # Sub text
        tw, th = draw.textsize(self.text_sub, font=font)
        draw.text(((w - tw) / 2, h - small_font - padding), self.text_sub, font=font, fill=255)

        # Main text
        font = ImageFont.truetype('/home/pi/code/components/VCR_OSD_MONO_1.001.ttf', big_font)
        tw, th = draw.textsize(self.text_main, font=font)
        draw.text(((w - tw) / 2, (h - th) / 2), self.text_main, font=font, fill=255)

        # Display image.
        self.disp.image(image)
        self.disp.display()

    def clear(self):
        self.disp.clear()
        self.disp.display()