from luma.core.interface.serial import i2c
from luma.core.render import canvas
from luma.oled.device import ssd1306

import numpy as np

from Eyes import Eyes
from Button import Button
from Oled import OLED
from Fans import Fans
from Util import ImagesLoader, EyesData
from menu.MenuScreen import *

import logging


# Config
_oled_width=128
_oled_height=64
_oled_address=0x3c

class Brain:
    def __init__(self):
        self.button_x = Button(24, on_click=self._on_click_x, on_hold=self._on_hold_x, on_long_hold=self._on_long_hold_x)
        self.button_o = Button(23, on_click=self._on_click_o, on_hold=self._on_hold_o, on_long_hold=self._on_long_hold_o)

        logging.debug('Init buttons')

        self.ad_mode = self.button_o.state() or self.button_x.state()

        logging.debug(f'AD mode = {self.ad_mode}')

        self.oled = ssd1306(i2c(port=1, address=_oled_address), width=_oled_width, height=_oled_height, rotate=0)
        self.oled.contrast(1)

        logging.debug('Oled init')

        self.eyes = Eyes(self)
        self.eyes_data = {}
        self.current_eye_key = None

        self.fans = Fans(14)

        self.menu_stack = [SplashScreen(self)]
        self.render_to_oled()

    def bootstrap(self):
        self.load_eyes()
        self.eyes.load_eyes_data(self.eyes_data)

        self.menu_stack = [MainMenuScreen(self)]
        self.render_to_oled()

        self.eyes.start_display_threads()

    def load_eyes(self):
        self.eyes_data = ImagesLoader().load_images(self.ad_mode)

    def keep_yourself_safe(self):
        import os
        self.eyes.keep_yourself_safe()
        os._exit(0)

    def eyes_dbg(self, text):
        self.eyes.display_dbg(text)

    def exit_menu(self):
        if len(self.menu_stack) > 1:
            self.menu_stack.pop(-1)
            # TODO async render?
            self.render_to_oled()

    def render_to_oled(self):
        with canvas(self.oled, dither=True) as draw:
            self.menu_stack[-1].render(draw)

    def _on_click_x(self):
        logging.info('Click X')
        self.menu_stack[-1].on_click_x()
        self.render_to_oled()

    def _on_hold_x(self):
        logging.info('Hold X')
        self.exit_menu()
        self.render_to_oled()

    def _on_long_hold_x(self):
        logging.info('Long Hold X')
        self.keep_yourself_safe()

    def _on_click_o(self):
        logging.info('Click O')
        self.menu_stack[-1].on_click_o()
        self.render_to_oled()

    def _on_hold_o(self):
        logging.info('Hold O')
        self.menu_stack[-1].on_hold_o()
        self.render_to_oled()

    def _on_long_hold_o(self):
        logging.info('Long Hold O')
        self.menu_stack[-1].on_long_hold_o()
        self.render_to_oled()

    def get_fan_state(self) -> bool:
        return self.fans.state

    def toggle_fan(self):
        self.fans.toggle()

    def get_current_eye_key(self) -> str:
        return self.current_eye_key

    def stack_menu_screen(self, screen: BaseMenuScreen):
        self.menu_stack.append(screen)
        self.render_to_oled()

    def set_current_eye_key(self, key):
        self.current_eye_key = key
        self.eyes.key = key
