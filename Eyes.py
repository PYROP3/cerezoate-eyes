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

from Util import EyesData, Profiler

# Raspberry Pi pin configuration:
logging.basicConfig(level=logging.DEBUG)

def _frame_to_np(image: Image.Image, rotate=0) -> list:
    if image.size != (240, 240):
        image = image.resize((240, 240), resample=Image.Resampling.BICUBIC)
    if rotate != 0:
        image = image.rotate(rotate)
    img = np.asarray(image)
    # logging.debug('img.shape=%s, dtype=%s', img.shape, img.dtype)
    pix = np.zeros((image.size[0],image.size[1],2), dtype = np.uint8)
    pix[...,[0]] = np.add(np.bitwise_and(img[...,[0]],0xF8),np.right_shift(img[...,[1]],5))
    pix[...,[1]] = np.add(np.bitwise_and(np.left_shift(img[...,[1]],3),0xE0),np.right_shift(img[...,[2]],3))
    # logging.debug('Pix.shape=%s', pix.shape)
    data = pix.flatten().tolist()
    result = []
    for i in range(0,len(data),4096):
        result.append(data[i:i+4096])
        # logging.debug('i = %d, len=%d', i, len(data[i:i+4096]))
    # logging.debug('first block: %s', result[0][1019])
    return result

class AsyncInterface:
    def __init__(self, displays, eye_l, eye_r):
        self.eye_l = eye_l
        self.eye_r = eye_r
        self.kill_switch = False
        self.thread_l = None
        self.thread_r = None
        self.disp = displays

    def display_loop(self, left):

        def get_next_frame(img, current_frame, frame_debt):
            while frame_debt > 0:
                # duration = img.info['duration']
                _, duration = img[current_frame]
                frame_debt -= duration

                current_frame += 1
                current_frame %= len(img)
                # current_frame %= img.n_frames
                # self.log.debug('Skipping frame...')
            return current_frame, frame_debt

        p = Profiler()

        frame = 0
        frame_debt = 0
        img = self.eye_l if left else self.eye_r
        warned = False

        while not self.kill_switch:
            start_time = time.time()

            frame, frame_debt = get_next_frame(img, frame, frame_debt)
            duration = img[frame][1]
            # duration = img.info['duration']
            # img.seek(frame)

            # logging.debug(f'Passing {len(img_l[gif_key_l])} blocks')
            # self.disp.ShowImageRaw(img[frame][0], left)
            self.disp.ShowImage(img[frame][0], left)
            # self.disp.ShowImage(img.resize((240,240), resample=Image.Resampling.BICUBIC), left)

            frame += 1
            frame %= len(img)
            # frame %= img.n_frames

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

    def start(self):
        self.thread_l = threading.Thread(target=self.display_loop, args=(True,))
        self.thread_r = threading.Thread(target=self.display_loop, args=(False,))
        self.thread_l.start()
        self.thread_r.start()

    def finish(self):
        self.kill_switch = True
        if self.thread_l is not None:
            self.thread_l.join()
        if self.thread_r is not None:
            self.thread_r.join()

class SyncInterface:
    def __init__(self, displays, eye_l, eye_r):
        self.eye_l = [(_frame_to_np(i[0]), i[1]) for i in eye_l]
        self.eye_r = [(_frame_to_np(i[0], rotate=180), i[1]) for i in eye_r]
        self.kill_switch = False
        self.thread = None
        self.disp = displays

    def get_next_frame(self, img, current_frame, frame_debt):
        while frame_debt > 0:
            # duration = img.info['duration']
            _, duration = img[current_frame]
            frame_debt -= duration

            current_frame += 1
            current_frame %= len(img)
            # current_frame %= img.n_frames
            # self.log.debug('Skipping frame...')
        return current_frame, frame_debt

    def display_loop(self):

        # p = Profiler()

        frame = 0
        frame_debt = 0
        warned = False

        while not self.kill_switch:
            # p.trig('loop start')
            start_time = time.time()

            frame, frame_debt = self.get_next_frame(self.eye_l, frame, frame_debt)
            # duration = self.eye_l[frame][1]
            duration = 1.
            # logging.debug(f'{duration=}')
            # duration = img.info['duration']
            # img.seek(frame)

            # logging.debug(f'Passing {len(img_l[gif_key_l])} blocks')
            # self.disp.ShowImageRaw(img[frame][0], left)
            # p.trig('display L')
            # self.disp.ShowImage(self.eye_l[frame][0], True)
            self.disp.ShowImageRaw(self.eye_l[frame][0], True)
            # p.trig('display R')
            # self.disp.ShowImage(self.eye_r[frame][0], False)
            self.disp.ShowImageRaw(self.eye_r[frame][0], False)
            # p.trig('display done')
            # self.disp.ShowImage(img.resize((240,240), resample=Image.Resampling.BICUBIC), left)

            frame += 1
            frame %= len(self.eye_l)
            # frame %= img.n_frames

            now = time.time()
            frame_delay = duration + start_time - now
            if frame_delay > 0:
                # p.trig(f'sleep {frame_delay}')
                time.sleep(frame_delay)
            else:
                if not warned:
                    logging.warning('Too long displaying frame: %.2f vs %.2f', now - start_time, duration)
                    # TODO add notification to OLED?
                    warned = True
                frame_debt += frame_delay

    def start(self):
        self.thread = threading.Thread(target=self.display_loop)
        self.thread.start()

    def finish(self):
        self.kill_switch = True
        if self.thread is not None:
            self.thread.join()

class Eyes:
    def __init__(self, brain):
        self.brain = brain
        self.key = None
        self.kill_switch = False
        self.init_disp()
        
        self.eyes_data = {}

        self.itf = None

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

    def change_eyes(self, key):
        if eye := self.eyes_data.get(key):
            if self.itf is not None:
                self.itf.finish()

            if len(eye.eye_l) == len(eye.eye_r):
                self.itf = SyncInterface(self.disp, eye.eye_l, eye.eye_r)
            else:
                self.itf = AsyncInterface(self.disp, eye.eye_l, eye.eye_r)

            self.itf.start()

    def _cleanup(self):
        try:
            self.display_dbg('Exit...')
        except:
            pass
        self.disp.module_exit()

    def keep_yourself_safe(self):
        self._cleanup()

if __name__ == '__main__':
    from Util import ImagesLoader
    
    eyes_data = ImagesLoader().load_images(False)

    try:
        eyes = Eyes(None)
        eyes.load_eyes_data(eyes_data)
        eyes.change_eyes('0 - Nyan')

        time.sleep(20)

        eyes.keep_yourself_safe()

    except IOError as e:
        logging.info(e)

    except KeyboardInterrupt:
        eyes.keep_yourself_safe()
        logging.info("quit:")
        exit()
