import logging

from Brain import Brain

logging.basicConfig()

if __name__ == '__main__':
    brain = Brain()
    
    logging.info('Bootstrapping resources')
    brain.bootstrap()

    try:
        while True:
            pass
    except:
        logging.info('quit')
        brain.keep_yourself_safe()
