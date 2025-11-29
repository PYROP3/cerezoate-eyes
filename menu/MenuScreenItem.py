
from PIL import Image

class BaseMenuItem:
    def __init__(self, screen):
        self.screen = screen

    def render(self, draw, position: tuple[int, int], highlighted: bool):
        pass

class TextMenuItem(BaseMenuItem):
    def __init__(self, text, screen):
        super().__init__(screen)
        self.text = text

    def render(self, draw, position: tuple[int, int], highlighted: bool):
        draw.rectangle(draw.textbbox(position, self.text), outline='white' if highlighted else 'black', fill='black')
        draw.text(position, self.text, fill='white')

class IconMenuItem(BaseMenuItem):
    def __init__(self, value: str, icon: Image, screen, position=None, width=60, height=60):
        super().__init__(screen)
        self.icon = icon
        self.value = value
        self.width = width
        self.height = height
        self.position = position

    def render(self, draw, position: tuple[int, int], highlighted: bool):
        position = self.position or position
        draw.rectangle((position[0], position[1], position[0] + self.width + 4, position[1] + self.height + 4), outline='white' if highlighted else 'black', fill='black')
        draw.bitmap((position[0], position[1]), self.icon)

class IconMenuItemSlot(BaseMenuItem):
    def __init__(self, icons: dict[str, IconMenuItem], screen, position=None, width=24, height=24):
        super().__init__(screen)
        self.icons = icons
        self.width = width
        self.height = height
        self.position = position

        self._unknown_icon = IconMenuItem('unknown', Image.open('resources/core/oled/ic_unknown_24x24.bmp').convert(), self.screen)

    def render(self, draw, position: tuple[int, int], highlighted: bool):
        position = self.position or position
        draw.rectangle((position[0], position[1], position[0] + self.width + 4, position[1] + self.height + 4), outline='white' if highlighted else 'black', fill='black')
        draw.bitmap((position[0] + 2, position[1] + 2), self.icons.get(self._get_icon_key(), self._unknown_icon).icon)

    def _get_icon_key(self):
        return None

class FanMenuItem(IconMenuItemSlot):
    def __init__(self, icon_on: Image, icon_off: Image, screen, position=None):
        super().__init__({'FanOn': IconMenuItem('FanOn', icon_on, screen), 'FanOff': IconMenuItem('FanOff', icon_off, screen)}, screen, position=position)

    def _get_icon_key(self):
        return 'FanOn' if self.screen.brain.get_fan_state() else 'FanOff'

class EyesMenuItem(IconMenuItemSlot):
    def _get_icon_key(self):
        return self.screen.brain.get_current_eye_key()
