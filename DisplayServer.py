#!/usr/bin/python
# -*- coding: UTF-8 -*-
#import chardet
import os
import sys
import time
import logging
import spidev as SPI
sys.path.append(".")
from lib import LCD_1inch28_dual
from PIL import Image,ImageDraw,ImageFont

import threading

# Raspberry Pi pin configuration:
RST = 27
DC = 25
BL = 18
bus = 0
device = 0

logging.basicConfig(level=logging.DEBUG)

def _preprocess_file(file):
    if file[-3:] not in ('gif', 'png'):
        return None, None
    image = Image.open(file)
    frame_data = []
    duration = 0.
    n_frames = image.n_frames
    for index in range(1, n_frames):
        image.seek(index)
        frame_duration = image.info['duration']
        frame_data.append((image.resize((240, 240), resample=Image.Resampling.BICUBIC).rotate(180), frame_duration / 1000.))
        duration += frame_duration
    logging.debug('[load] %s: %d frames; %.2fs', file, len(frame_data), duration / 1000.)
    return frame_data

def _get_next_frame(img, current_frame, frame_debt):
    while frame_debt > 0:
        # duration = img.info['duration']
        _, duration = img[current_frame]
        frame_debt -= duration

        current_frame += 1
        current_frame %= len(img)
        # current_frame %= img.n_frames
        # self.log.debug('Skipping frame...')
    return current_frame, frame_debt

def loop_sync(disp, file_l, file_r):
    logging.info("loop_sync")
    frame = 0
    frame_debt = 0
    warned = False

    while True:
        # p.trig('loop start')
        start_time = time.time()

        frame, frame_debt = _get_next_frame(file_l, frame, frame_debt)
        duration = file_l[frame][1]
        
        disp.ShowImage(file_l[frame][0], True)
        disp.ShowImage(file_r[frame][0], False)
        # p.trig('display done')
        # self.disp.ShowImage(img.resize((240,240), resample=Image.Resampling.BICUBIC), left)

        frame += 1
        frame %= len(file_l)

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

def _loop_async(disp, file, left, kill_switch):
    frame = 0
    frame_debt = 0
    warned = False

    while not kill_switch.is_set():
        start_time = time.time()

        frame, frame_debt = _get_next_frame(file, frame, frame_debt)
        duration = file[frame % len(file)][1]

        disp.ShowImage(file[frame % len(file)][0], left)

        frame += 1
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

def loop_async(disp, file_l, file_r):
    logging.info("loop_async")

    kill_switch = threading.Event()
    thread_l = threading.Thread(target=_loop_async, args=(disp, file_l, True, kill_switch))
    thread_r = threading.Thread(target=_loop_async, args=(disp, file_r, False, kill_switch))

    thread_l.start()
    thread_r.start()

    try:
        while True:
            pass
    except KeyboardInterrupt:
        kill_switch.set()
        thread_l.join()
        thread_r.join()
        raise

try:
    # display with hardware SPI:
    disp = LCD_1inch28_dual.LCD_1inch28_Dual()

    # Initialize library.
    disp.Init(True)
    disp.Init(False)

    # Clear display.
    # disp.clear(True)
    # disp.clear(False)

    #Set the backlight to 100
    disp.bl_DutyCycle(50)

    file_l = _preprocess_file(sys.argv[1])
    file_r = _preprocess_file(sys.argv[2])

    threads = []

    if len(file_l) == len(file_r):
        loop_sync(disp, file_l, file_r)
    else:
        loop_async(disp, file_l, file_r)

except IOError as e:
    logging.info(e)

except KeyboardInterrupt:
    disp.module_exit()
    logging.info("quit:")
    exit()
