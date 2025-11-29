import os
import numpy as np
from PIL import Image

import logging
import time

class EyesData:
    def __init__(self, name: str, icon: Image, eye_l: np.array, eye_r: np.array):
        self.name = name
        self.icon = icon
        self.eye_l = eye_l
        self.eye_r = eye_r

class ImagesLoader:
    def __init__(self):
        pass

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
            # frame_data.append((self._frame_to_np(image.rotate(180)), frame_duration / 1000.))
            frame_data.append((image.resize((240, 240), resample=Image.Resampling.BICUBIC).rotate(180), frame_duration / 1000.))
            # logging.debug('[load] frame %d -> %d', index, len(frame_data[-1][0]))
            duration += frame_duration
        logging.debug('[load] %s: %d frames; %.2fs', file, len(frame_data), duration / 1000.)
        return frame_data

    def _load_folder(self, folder) -> dict[str, EyesData]:
        result = {}
        for eye in sorted(os.listdir(f'resources/eyes/{folder}')):
            logging.debug(f'Checking {folder}/{eye}')
            files = os.listdir(f'resources/eyes/{folder}/{eye}')

            icon = None
            frame_data_l = None
            frame_data_r = None

            for file in files:
                filename = file.split('.')[0].lower()
                if filename == 'icon':
                    icon = Image.open(f'resources/eyes/{folder}/{eye}/{file}').convert()
                    continue

                if filename in ['both', 'left', 'right']:
                    # frame_data = self._preprocess_file(f'resources/eyes/{folder}/{eye}/{file}')
                    # frame_data = Image.open(f'resources/eyes/{folder}/{eye}/{file}')
                    # if frame_data is None:
                    #     continue
                    if filename in ['both', 'left']:
                        frame_data_l = f'resources/eyes/{folder}/{eye}/{file}'
                    if filename in ['both', 'right']:
                        frame_data_r = f'resources/eyes/{folder}/{eye}/{file}'

            result[eye] = EyesData(eye, icon, frame_data_l, frame_data_r)
        return result

    def load_images(self, ad_mode: bool) -> dict[str, EyesData]:
        result = self._load_folder('normal')

        if ad_mode:
            ad_result = self._load_folder('AD')
            for key, eye in ad_result.items():
                result[f'{key} [AD]'] = eye

        return result

class Profiler:
    def __init__(self):
        self.last_time = time.time()

    def trig(self, key: str):
        now = time.time()
        diff = now - self.last_time
        logging.debug(f'[PROFILER] {key} - {diff}')
        self.last_time = now