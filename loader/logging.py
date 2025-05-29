import logging
import sys

async def logger():
    logging.basicConfig(format='[%(levelname) %(asctime)s] %(name)s: %(message)s', level=logging.WARNING)
