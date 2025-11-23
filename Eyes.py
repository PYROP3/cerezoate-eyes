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

# Raspberry Pi pin configuration:
logging.basicConfig(level=logging.DEBUG)

class Eyes:
    def __init__(self, nose):
        self.images = []
        self.idx = 0
        self.nose = nose
        self.nose.on_click = self.next_eyes
        self.kill_switch = False
        self.init_disp()
        self.load_images()

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

    def _frame_to_np(self, image: Image.Image) -> list:
        if image.size != (240, 240):
            image = image.resize((240, 240), resample=Image.Resampling.BICUBIC)
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

    def _preprocess_file(self, file):
        if file[-3:] not in ('gif', 'png'):
            return None, None
        image = Image.open(file)
        frame_data = []
        duration = 0.
        n_frames = image.n_frames
        for index in range(1, n_frames):
            image.seek(index)
            frame_duration = image.info['duration']
            # if frame_duration == 0:
            frame_data.append((self._frame_to_np(image.rotate(180)), frame_duration / 1000.))
            # logging.debug('[load] frame %d -> %d', index, len(frame_data[-1][0]))
            duration += frame_duration
        logging.debug('[load] %s: %d frames; %.2fs', file, len(frame_data), duration / 1000.)
        return frame_data

    def _load_folder(self, folder):
        for eye in os.listdir(f'eyes/{folder}'):
            logging.debug(f'Checking {folder}/{eye}')
            files = os.listdir(f'eyes/{folder}/{eye}')
            if len(files) == 1: # The same for both eyes
                frame_data = self._preprocess_file(f'eyes/{folder}/{eye}/{files[0]}')
                if frame_data is None:
                    continue
                self.images.append((frame_data, frame_data))
                continue

            frame_data_l = None
            frame_data_r = None

            for file in files:
                frame_data = self._preprocess_file(f'eyes/{folder}/{eye}/{file}')
                if 'left' in file:
                    frame_data_l = frame_data
                else:
                    frame_data_r = frame_data

            self.images.append((frame_data_l, frame_data_r))

    def load_images(self):
        if self.nose.ad_mode:
            self.display_dbg('Loading...\nAD ON >:3')
        else:
            self.display_dbg('Loading...')

        self._load_folder('normal')

        if self.nose.ad_mode:
            self._load_folder('AD')

        self.display_dbg(f'Loading...\nLoaded {len(self.images)}')

    def cleanup(self):
        try:
            self.display_dbg('Exit...')
        except:
            pass
        self.disp.module_exit()

    def next_eyes(self):
        self.idx += 1
        self.idx %= len(self.images)

    def display_loop(self, left):

        def get_next_frame(img, current_frame, frame_debt):
            while frame_debt > 0:
                _, duration = img[current_frame]
                frame_debt -= duration

                current_frame += 1
                current_frame %= len(img)
                # self.log.debug('Skipping frame...')
            return current_frame, frame_debt

        last_idx = self.idx
        frame = 0
        frame_debt = 0
        img_l, img_r = self.images[self.idx]
        img = img_l if left else img_r

        while not self.kill_switch:
            if last_idx != self.idx:
                img_l, img_r = self.images[self.idx]
                img = img_l if left else img_r
                frame = 0
                last_idx = self.idx

            start_time = time.time()

            frame, frame_debt = get_next_frame(img, frame, frame_debt)
            duration = img[frame][1]

            # logging.debug(f'Passing {len(img_l[gif_idx_l])} blocks')
            self.disp.ShowImageRaw(img[frame][0], left)

            frame += 1
            frame %= len(img)

            now = time.time()
            frame_delay = duration + start_time - now
            if frame_delay > 0:
                time.sleep(frame_delay)
            else:
                logging.warning('Too long displaying frame: %.2f vs %.2f', now - start_time, duration)
                frame_debt += frame_delay

    def display_thread(self):
        self.thread_l = threading.Thread(target=self.display_loop, args=(True,))
        self.thread_r = threading.Thread(target=self.display_loop, args=(False,))
        self.thread_l.start()
        self.thread_r.start()

    def stop_display(self):
        self.kill_switch = True
        self.thread_l.join()
        self.thread_r.join()
        
        self.cleanup()

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
