import logging
import sys


def get_named_logger(name, debug=False):
    """
    Create a logger, if no handlers already exist attach to stdout
    :param name: desired name of logger as string
    :param debug: log DEBUG events if True
    :return: Logger instance
    """
    logger = logging.getLogger(name)
    if debug:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)
    if not len(logger.handlers):
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter('[ %(asctime)s ] [%(name)s] [%(levelname)s] %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger
