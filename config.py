# Copyright Severin Josef Burg 2023
# Any unauthorised usage forbidden

import logging


def set_up_logging():
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s | %(name)s | %(levelname)s | %(message)s',
        filename='logging.log'
    )
    formatter = logging.Formatter(fmt='%(asctime)s | %(levelname)s | %(module)s | %(message)s')

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)

    logger = logging.getLogger('Main_Logger')
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)

    return logger
