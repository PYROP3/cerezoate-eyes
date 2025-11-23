import logging

from Eyes import Eyes
from Nose import Nose
from Oled import OLED

logging.basicConfig()

oled = OLED()
nose = Nose(oled)
eyes = Eyes(nose, oled)
nose.set_eyes(eyes)

if __name__ == '__main__':
    eyes.display_thread()
    nose.start_polling()

    try:
        while True:
            pass
    except:
        logging.info('quit')
        nose.stop_polling()
        eyes.stop_display()
