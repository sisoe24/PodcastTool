"""Logging module for podcasttools."""
import os
import sys
import logging
import pathlib

# from startup import LOG_PATH

LOGGER = logging.getLogger('podcasttool')

LOGGER.setLevel(logging.DEBUG)

LOG_PATH = pathlib.Path(os.path.dirname(__file__))
LOG_PATH = os.path.join(LOG_PATH.parent, 'log')
os.makedirs(LOG_PATH, exist_ok=True)

CRITICAL_LOG = logging.FileHandler(os.path.join(LOG_PATH, 'errors.log'), 'a+')
CRITICAL_LOG.setLevel(logging.ERROR)
CH_FORMATTER = logging.Formatter(
    '%(asctime)s [%(levelname)s] - %(module)s: %(lineno)d: %(funcName)s() - %(message)s',
    '%Y-%m-%d %H:%M:%S')
CRITICAL_LOG.setFormatter(CH_FORMATTER)
LOGGER.addHandler(CRITICAL_LOG)

DEBUG_LOW = logging.FileHandler(os.path.join(LOG_PATH, 'debug.log'), 'a+')
DEBUG_LOW.setLevel(logging.DEBUG)
FORMATTER = logging.Formatter(
    '%(asctime)s - %(filename)-20s %(funcName)-25s %(levelname)-10s %(message)s',
    '%Y-%m-%d %H:%M')
DEBUG_LOW.setFormatter(FORMATTER)
LOGGER.addHandler(DEBUG_LOW)

CONSOLE_LOG = logging.StreamHandler(stream=sys.stdout)
CONSOLE_LOG.setLevel(logging.INFO)
CONSOLE = logging.Formatter('[%(levelname)s line: %(lineno)d] - %(message)s')
CONSOLE_LOG.setFormatter(CONSOLE)
LOGGER.addHandler(CONSOLE_LOG)
