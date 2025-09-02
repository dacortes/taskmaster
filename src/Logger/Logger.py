import logging
import os
import sys

# Add root to the paths so it can access the Constants module even if run from a different directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from Constants import APP_NAME, LOG_DIR, LOG_FILE, LOG_LEVEL

from .CleanFormater import CleanFormatter

os.makedirs(LOG_DIR, exist_ok=True)


class Logger:
    _loggers = {}

    @staticmethod
    def get_logger(name):
        if name in Logger._loggers:
            return Logger._loggers[name]
        logger = logging.getLogger(name)
        logger.setLevel(LOG_LEVEL)
        logger.propagate = False

        if not logger.handlers:
            stream_handler = logging.StreamHandler(sys.stdout)
            stream_handler.setLevel(LOG_LEVEL)

            file_handler = logging.FileHandler(os.path.join(LOG_DIR, LOG_FILE))
            file_handler.setLevel(LOG_LEVEL)

            formatter = logging.Formatter(
                "[%(asctime)s] [%(filename)s:%(funcName)s:%(lineno)d] %(levelname)s - %(message)s"
            )

            # I don't need ASCII code when writing to a file
            clean_formatter = CleanFormatter(
                "[%(asctime)s] [%(filename)s:%(funcName)s:%(lineno)d] %(levelname)s - %(message)s"
            )
            stream_handler.setFormatter(formatter)
            file_handler.setFormatter(clean_formatter)

            logger.addHandler(stream_handler)
            logger.addHandler(file_handler)

        Logger._loggers[name] = logger
        return logger


LOGGER = Logger.get_logger(APP_NAME)


if __name__ == "__main__":
    logger = Logger.get_logger(__name__)
    logger.info("Logger initialized")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
