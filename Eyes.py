#!/usr/bin/python
# -*- coding: UTF-8 -*-
#import chardet
import os
import sys
import threading
import time
import logging
import spidev as SPI
import numpy as np
sys.path.append(".")
from lib import LCD_1inch28_dual
from PIL import Image,ImageDraw,ImageFont

from Util import EyesData

# Raspberry Pi pin configuration:
logging.basicConfig(level=logging.DEBUG)

class Eyes:
    def __init__(self, brain):
        self.brain = brain
        self.key = None
        self.kill_switch = False
        self.init_disp()
        
        self.eyes_data = {}

    def load_eyes_data(self, eyes_data: dict[str, EyesData]):
        self.eyes_data = eyes_data
        self.key = sorted(list(eyes_data.keys()))[0]

    def init_disp(self):
        self.disp = LCD_1inch28_dual.LCD_1inch28_Dual()

        # Initialize library.
        self.disp.Init(True)
        self.disp.Init(False)

        # Clear display.
        self.disp.clear(True)
        self.disp.clear(False)

        #Set the backlight to 100
        self.disp.bl_DutyCycle(50)

    def display_dbg(self, text, font='Font02.ttf', size=25):
        # Create blank image for drawing.
        image = Image.new("RGB", (self.disp.width, self.disp.height), (0x89, 0x00, 0x38))
        draw = ImageDraw.Draw(image)
        Font = ImageFont.truetype(f"Font/{font}", size)
        draw.text((40, 50), text, fill = (0x7a, 0xee, 0x40),font=Font)
        self.disp.ShowImageEqual(image.rotate(90))
        # self.disp.ShowImage(image, False)

    def _cleanup(self):
        try:
            self.display_dbg('Exit...')
        except:
            pass
        self.disp.module_exit()

    def display_loop(self, left):

        def get_next_frame(img, current_frame, frame_debt):
            while frame_debt > 0:
                _, duration = img[current_frame]
                frame_debt -= duration

                current_frame += 1
                current_frame %= len(img)
                # self.log.debug('Skipping frame...')
            return current_frame, frame_debt

        last_key = self.key
        frame = 0
        frame_debt = 0
        eye_data = self.eyes_data[self.key]
        img = eye_data.eye_l if left else eye_data.eye_r
        warned = False

        while not self.kill_switch:
            if last_key != self.key:
                eye_data = self.eyes_data[self.key]
                img = eye_data.eye_l if left else eye_data.eye_r
                frame = 0
                last_key = self.key
                warned = False

            start_time = time.time()

            frame, frame_debt = get_next_frame(img, frame, frame_debt)
            duration = img[frame][1]

            # logging.debug(f'Passing {len(img_l[gif_key_l])} blocks')
            self.disp.ShowImageRaw(img[frame][0], left)

            frame += 1
            frame %= len(img)

            now = time.time()
            frame_delay = duration + start_time - now
            if frame_delay > 0:
                time.sleep(frame_delay)
            else:
                if not warned:
                    logging.warning('Too long displaying frame: %.2f vs %.2f', now - start_time, duration)
                    # TODO add notification to OLED?
                    warned = True
                frame_debt += frame_delay

    def start_display_threads(self):
        self.thread_l = threading.Thread(target=self.display_loop, args=(True,))
        self.thread_r = threading.Thread(target=self.display_loop, args=(False,))
        self.thread_l.start()
        self.thread_r.start()

    def keep_yourself_safe(self):
        self.kill_switch = True
        self.thread_l.join()
        self.thread_r.join()
        
        self._cleanup()

if __name__ == '__main__':
    try:
        eyes = Eyes(None)

        time.sleep(5)

        eyes.cleanup()

    except IOError as e:
        logging.info(e)

    except KeyboardInterrupt:
        eyes.cleanup()
        logging.info("quit:")
        exit()
