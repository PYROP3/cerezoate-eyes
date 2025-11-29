import logging

from PIL import Image

from menu.MenuScreenItem import IconMenuItem, FanMenuItem, EyesMenuItem, TextMenuItem

class BaseMenuScreen:
    def __init__(self, brain, parent=None):
        self.parent = parent
        self.brain = brain
        self.items = []
        self.selected_key = None

        self.children_menus = {}

    def render(self, draw):
        pass

    def on_click_x(self):
        pass

    def on_hold_x(self):
        pass

    def on_long_hold_x(self):
        pass

    def on_click_o(self):
        pass

    def on_hold_o(self):
        pass

    def on_long_hold_o(self):
        pass

class SplashScreen(BaseMenuScreen):
    def __init__(self, brain):
        super().__init__(brain, parent=None)
        self.splash = Image.open("resources/core/oled/splash.bmp").convert()

    def render(self, draw):
        draw.bitmap((0,0), self.splash)

class EyeSelectionScreen(BaseMenuScreen):
    def __init__(self, brain, parent):
        super().__init__(brain, parent)

        self.items = []
        for key in self.brain.eyes_data.keys():
            self.items.append(TextMenuItem(key, self))

        self.selected_idx = 0

    def on_click_x(self):
        self.selected_idx += 1
        self.selected_idx %= len(self.items)

    def on_click_o(self):
        self.brain.set_current_eye_key(self.items[self.selected_idx].text)
        self.brain.exit_menu()

    def render(self, draw):
        self.items[self.selected_idx - 1].render(draw, (10, 10), False)
        self.items[self.selected_idx].render(draw, (10, 25), True)
        self.items[(self.selected_idx + 1) % len(self.items)].render(draw, (10, 40), False)

class PoweroffScreen(BaseMenuScreen):
    def __init__(self, brain, parent):
        super().__init__(brain, parent)

        self.items = []
        self.items.append(TextMenuItem('Cancel', self))
        self.items.append(TextMenuItem('Restart', self))

        self.selected_idx = 0

    def on_click_x(self):
        self.selected_idx += 1
        self.selected_idx %= len(self.items)

    def on_click_o(self):
        if self.items[self.selected_idx].text == 'Restart':
            self.brain.keep_yourself_safe()
        else:
            self.brain.exit_menu()

    def render(self, draw):
        for idx, item in enumerate(self.items):
            item.render(draw, (20, 25+idx*20), self.selected_idx == idx)
        # self.items[0].render(draw, (20, 25), self.selected_idx == 0)
        # self.items[1].render(draw, (20, 50), self.selected_idx == 1)

# +---+---+---+---+
# |       | A | B |
# + icon  +---+---+
# |       | C | D |
# +---+---+---+---+

class MainMenuScreen(BaseMenuScreen):
    def __init__(self, brain):
        super().__init__(brain, parent=None)

        unknown_icon = Image.open('resources/core/oled/ic_unknown_24x24.bmp').convert()

        eye_icons = {}
        for key, eye in brain.eyes_data.items():
            eye_icons[key] = IconMenuItem(key, eye.icon or unknown_icon, self)

        self.items = {
            'icon': IconMenuItem('icon', Image.open('resources/core/oled/icon.bmp'), self, position=(0, 0)),
            'eyes': EyesMenuItem(eye_icons, self, position=(66, 2)),
            'fan': FanMenuItem(Image.open('resources/core/oled/fan_on.bmp'), Image.open('resources/core/oled/fan_off.bmp'), self, position=(66, 34)),
            'power': IconMenuItem('icon', Image.open('resources/core/oled/power.bmp'), self, position=(96, 34)),
        }

        self.next_selection = {
            'eyes': 'fan',
            'fan': 'power',
            'power': 'eyes',
        }

        self.children_menus = {
            'eyes': EyeSelectionScreen(self.brain, self),
            'power': PoweroffScreen(self.brain, self),
        }

        self.selected_key = 'eyes'

    def render(self, draw):
        for key, item in self.items.items():
            logging.debug(f'Rendering {key} in main screen')
            item.render(draw, None, key == self.selected_key)

    def _toggle_fan(self):
        self.brain.toggle_fan()

    # def _enter_eyes_menu(self):
    #     logging.debug(f'Enter eyes menu: {self.selected_key}')
    #     if new_screen := self.children_menus.get(self.selected_key):
    #         self.brain.stack_menu_screen(new_screen)

    def _enter_submenu(self):
        logging.debug(f'Enter sub menu: {self.selected_key}')
        if new_screen := self.children_menus.get(self.selected_key):
            self.brain.stack_menu_screen(new_screen)

    def on_click_o(self):
        match self.selected_key:
            case 'fan':
                self._toggle_fan()
            case 'eyes':
                self._enter_submenu()
            case 'power':
                self._enter_submenu()
            case _:
                logging.warning(f'Unknown key {self.selected_key}')

    def on_click_x(self):
        self.selected_key = self.next_selection[self.selected_key]
