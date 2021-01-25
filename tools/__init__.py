__all__ = ['util', 'encryption', 'techtrans', 'lyric', 'web']

import sys
import logging

args = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARRING": logging.WARNING,
    "ERROR": logging.ERROR
}

default_log_level = True
# CHECK
for arg in args:

    _log = sys.argv.count(arg)
    if _log != 0:
        log_level = args.get(sys.argv[sys.argv.index(arg)])
        default_log_level = False
        logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
        logging.getLogger("init").info("log level info.")
        break

if default_log_level:
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    logging.getLogger("init").info("default log level info.")