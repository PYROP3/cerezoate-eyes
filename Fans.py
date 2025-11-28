from gpiozero import DigitalOutputDevice

class Fans:
    def __init__(self, pin):
        self.fans = DigitalOutputDevice(pin, active_high=True, initial_value=True)
        self.state = False

    def _write(self, state):
        self.state = state
        self.fans.value = not state

    def toggle(self):
        self._write(not self.state)

    def turn_on(self):
        self._write(True)

    def turn_off(self):
        self._write(False)
