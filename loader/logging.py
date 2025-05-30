import logging

def logger():
    logging.basicConfig(format='[%(levelname)s %(asctime)s] %(name)s: %(message)s', level=logging.WARNING)
