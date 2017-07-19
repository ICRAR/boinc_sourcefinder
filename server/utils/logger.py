import logging
import logging.handlers

# Setup a small logging helper that prints to a general logging file for work generation

logging.basicConfig(level=logging.INFO, format='%(asctime)-15s:' + logging.BASIC_FORMAT)


def config_logger(name):
    """
    Get a logger

    :param name:
    :return:
    """
    logger = logging.getLogger(name)

    return logger
