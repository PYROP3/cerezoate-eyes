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

class Button:
    def __init__(self, pin, on_click=None, on_hold=None, on_long_hold=None, pull_up = True):
        self.button = DigitalInputDevice(pin, pull_up=pull_up)

        self._last_state = self.state()
        self._last_state_change = time.monotonic()

        self.kill_switch = False

        self.on_click = on_click or self._dummy
        self.on_hold = on_hold or self._dummy
        self.on_long_hold = on_long_hold or self._dummy

        self.thread = threading.Thread(target=self._poll)
        self.thread.start()

    def _dummy(self):
        logging.debug('Dummy action')
        pass

    def state(self) -> bool:
        state = self.button.value == 1
        # logging.debug(f'State={state}')
        return state

    def _on_click(self):
        logging.info('Click')
        self.on_click()

    def _on_hold(self):
        logging.info('Hold')
        self.on_hold()

    def _on_long_hold(self):
        logging.info('Long hold')
        self.on_long_hold()

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

    def _poll(self):
        while not self.kill_switch:
            new_state = self.state()
            if new_state != self._last_state:
                now = time.monotonic()
                self.handle(new_state, now - self._last_state_change)
                self._last_state = new_state
                self._last_state_change = now

    def kill(self):
        self.kill_switch = True
        try:
            self.thread.join()
        except:
            pass

if __name__ == '__main__':
    button = Button(24)

    try:
        while True:
            pass
    except:
        logging.info('quit')
        button.kill()
