import logging

from Eyes import Eyes
from Nose import Nose

logging.basicConfig()

nose = Nose()
eyes = Eyes(nose)

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
