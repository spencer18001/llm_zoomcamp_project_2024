import time, socket

from proj_config import config
from log_util import get_logger

_logger = get_logger(__name__)

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
                _logger.debug(f"{log_prefix}: connection failed! retrying in {config.chk_serv_delay} seconds (attempt {attempt} of {config.chk_serv_retries}). host={host}, port={port}")
                time.sleep(config.chk_serv_delay)

    _logger.error(f"{log_prefix}: failed! host={host}, port={port}")
    return False
