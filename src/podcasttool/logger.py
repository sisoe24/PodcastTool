"""Logging module for podcasttools."""
import sys
import logging

from . import util

# base logging
LOGGER = logging.getLogger('podcast_tool')

LOGGER.setLevel(logging.DEBUG)

FORMATTER = logging.Formatter(
    '%(filename)-20s %(funcName)-25s %(levelname)-10s %(message)s')
CH_FORMATTER = logging.Formatter(
    '[%(levelname)s] - %(module)s:%(lineno)d:%(funcName)s() - %(message)s')
CONSOLE = logging.Formatter('[%(levelname)s] - %(message)s')

LOG_PATH = util.get_path('log')

CRITICAL_LOG = logging.FileHandler(f'{LOG_PATH}/errors.log', 'w')
CRITICAL_LOG.setLevel(logging.WARNING)
CRITICAL_LOG.setFormatter(CH_FORMATTER)
LOGGER.addHandler(CRITICAL_LOG)

DEBUG_LOW = logging.FileHandler(f'{LOG_PATH}/debug_low.log', 'w')
DEBUG_LOW.setLevel(logging.DEBUG)
DEBUG_LOW.setFormatter(FORMATTER)
LOGGER.addHandler(DEBUG_LOW)

CONSOLE_LOG = logging.StreamHandler(stream=sys.stdout)
CONSOLE_LOG.setLevel(logging.INFO)
CONSOLE_LOG.setFormatter(CONSOLE)
LOGGER.addHandler(CONSOLE_LOG)

# status app logging
# if util.DEV_MODE:
#     LEVEL = logging.DEBUG
# else:
#     LEVEL = logging.INFO

# INFO_LOGGER = logging.getLogger('status_app')
# INFO_LOGGER.setLevel(LEVEL)
# CONSOLE = logging.Formatter('[%(levelname)s] - %(message)s')
