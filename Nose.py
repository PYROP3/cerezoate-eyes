import os
import sys
import time
import logging
import threading
from gpiozero import DigitalInputDevice, DigitalOutputDevice

logging.basicConfig(level=logging.DEBUG)

BUTTON_DEBOUNCE = 0.01
BUTTON_LONG_HOLD = 10
BUTTON_SHORT_HOLD = 1

class Nose:
    def __init__(self, oled, pin = 24, fans_pin = 23, pull_up = True, active_state = True):
        self.oled = oled
        self.button = DigitalInputDevice(pin, pull_up=pull_up)
        self.fans = DigitalOutputDevice(fans_pin, active_high=True, initial_value=False)
        self.ad_mode = self.state()
        self.oled.on_state_update('ad', self.ad_mode)
        logging.info(f'Nose startup AD mode={self.ad_mode}')

        self._last_state = self.state()
        self._last_state_change = time.monotonic()

        self.kill_switch = False

        self.on_click = None
        self.on_hold = None
        self.on_long_hold = None

        self.fans_on = False
        self.fans.value = True

        self.eyes = None

    def set_eyes(self, eyes):
        self.eyes = eyes

    def state(self):
        state = self.button.value == 1
        # logging.debug(f'State={state}')
        return state

    def _on_click(self):
        logging.info('Click')
        if self.on_click is not None:
            self.on_click()

    def _on_hold(self):
        logging.info('Hold')
        self.fans_on = not self.fans_on
        self.fans.value = not self.fans_on

        self.oled.on_state_update('fan', self.fans_on)

    def _on_long_hold(self):
        logging.info('Long hold')

        self.oled.display_raw('Goodbye Dot~! <3')

        if self.eyes is not None:
            self.eyes.stop_display()

        time.sleep(0.5)

        self.stop_polling()

        os._exit(0)

    def handle(self, edge, duration):
        if edge:
            # Button was just pressed, ignore
            return

        if duration < BUTTON_DEBOUNCE:
            # Noise, ignore
            return

        logging.debug(f'handling falling edge, {duration=}')

        if duration < BUTTON_SHORT_HOLD:
            return self._on_click()

        if duration < BUTTON_LONG_HOLD:
            return self._on_hold()

        return self._on_long_hold()

    def poll(self):
        new_state = self.state()
        if new_state != self._last_state:
            now = time.monotonic()
            self.handle(new_state, now - self._last_state_change)
            self._last_state = new_state
            self._last_state_change = now

    def polling_thread(self):
        while not self.kill_switch:
            self.poll()

    def start_polling(self):
        self.thread = threading.Thread(target=self.polling_thread)
        self.thread.start()

    def stop_polling(self):
        self.kill_switch = True
        try:
            self.thread.join()
        except:
            pass

if __name__ == '__main__':
    nose = Nose()

    nose.start_polling()

    try:
        while True:
            pass
    except:
        logging.info('quit')
        nose.stop_polling()
