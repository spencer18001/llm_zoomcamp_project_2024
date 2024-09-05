import logging, time, socket, os
from datetime import datetime
from zoneinfo import ZoneInfo

from proj_config import config

TZ = os.getenv("TZ", "America/Puerto_Rico")

_logger = logging.getLogger(__name__)
_logger.setLevel(config.logging_level)

def check_service(host, port):
    log_prefix = "check_service"

    attempt = 0
    while attempt < config.chk_serv_retries:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(config.chk_serv_timeout)
            try:
                s.connect((host, port))

                _logger.debug(f"{log_prefix}: success. host={host}, port={port}")
                return True
            except (socket.timeout, ConnectionRefusedError):
                attempt += 1
                time.sleep(config.chk_serv_delay)

    _logger.error(f"{log_prefix}: failed! host={host}, port={port}")
    return False

class TimezoneFormatter(logging.Formatter):
    def formatTime(self, record, datefmt=None):
        time = datetime.fromtimestamp(record.created, tz=ZoneInfo(TZ))
        return time.strftime(datefmt)

def setup_logger(logger):
    logger.setLevel(config.logging_level)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(config.logging_level)

    formatter = TimezoneFormatter(fmt='%(asctime)s | %(levelname)s | %(message)s', datefmt="%H:%M:%S %Z")
    console_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
