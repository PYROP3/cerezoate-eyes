# MicroPython SSD1306 OLED driver, I2C and SPI interfaces created by Adafruit

# pylint: disable=import-error
from luma.core.interface.serial import i2c
from luma.oled.device import ssd1306
from luma.core.render import canvas
from PIL import Image
# pylint: enable=import-error

import logging


class OLED:
    def __init__(self, oled_width=128, oled_height=64, oled_address=0x3c):
        self.oled = ssd1306(i2c(port=1, address=oled_address), width=oled_width, height=oled_height, rotate=0)
        self.oled.contrast(1)

        self.info = {
            'ad': False,
            'fan': False,
            'loading': True,
            'loaded': 0,
            'eye': 0,
        }

        logging.info('Init done')

    def _text(self, draw, text, x: int=None, y: int=None):
        text_size = draw.textsize(text)
        x = x or 10 # self.oled.width - text_size[0]
        y = y or (self.oled.height - text_size[1]) // 2
        draw.text((x, y), text, fill='white')

    def on_state_update(self, key, value):
        self.info[key] = value
        self.refresh_display()

    def refresh_display(self):
        with canvas(self.oled, dither=True) as draw:
            draw.rectangle(self.oled.bounding_box, outline='white', fill='black')
            self._text(draw, 'Cerezoate v1.0 <3', x=10, y=10)
            if self.info['ad']:
                self._text(draw, 'AD mode ON >;3', x=10, y=20)
            self._text(draw, 'Fans: ' + ('ON ^3^' if self.info['fan'] else 'off x3x'), x=10, y=30)
            self._text(draw, f'Eyes: {self.info["eye"]}/{self.info["loaded"]}' + (' (loading)' if self.info['loading'] else ''), x=10, y=40)

    def display_raw(self, text):
        logging.info(f'display_raw: {text}')

        with canvas(self.oled, dither=True) as draw:
            draw.rectangle(self.oled.bounding_box, outline='white', fill='black')
            self._text(draw, text)
            # text_size = draw.textsize(text)
            # draw.text((self.oled.width - text_size[0], (self.oled.height - text_size[1]) // 2), text, fill='white')

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    print('sanity')

    oled = OLED()
    oled.display_raw('Welcome, Dot~ <3')

    import time
    time.sleep(5)
