import logging, os
from datetime import datetime
from zoneinfo import ZoneInfo

from proj_config import config

TZ = os.getenv("TZ", "America/Puerto_Rico")

class TimezoneFormatter(logging.Formatter):
    def formatTime(self, record, datefmt=None):
        time = datetime.fromtimestamp(record.created, tz=ZoneInfo(TZ))
        return time.strftime(datefmt)

def setup_logger(logger):
    logger.setLevel(config.logging_level)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(config.logging_level)

    formatter = TimezoneFormatter(fmt='%(asctime)s | %(name)s | %(levelname)s | %(message)s', datefmt="%H:%M:%S.%f %Z")
    console_handler.setFormatter(formatter)

    logger.addHandler(console_handler)

def get_logger(name=None):
    logger = logging.getLogger(name)
    setup_logger(logger)
    return logger
