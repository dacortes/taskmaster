import logging
import os
import sys
import socket
from logging.handlers import SysLogHandler  # 🔹 Syslog handler

# Add root to the paths so it can access the Constants module even if run from a different directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from Constants import APP_NAME, LOG_DIR, LOG_FILE, LOG_LEVEL
from .CleanFormater import CleanFormatter

# 🔹 Ensure log directory exists
os.makedirs(LOG_DIR, exist_ok=True)


class Logger:
    """
    Custom logger that writes logs to:
      - Console (stdout)
      - File in LOG_DIR
      - Syslog (if available)
    """
    _loggers = {}

    @staticmethod
    def get_logger(name):
        """
        Returns a logger instance. If it does not exist, it creates one.
        """
        if name in Logger._loggers:
            return Logger._loggers[name]

        logger = logging.getLogger(name)
        logger.setLevel(LOG_LEVEL)
        logger.propagate = False  # Prevent messages from propagating to root logger

        if not logger.handlers:
            # --------------------------
            # Console Handler
            # --------------------------
            stream_handler = logging.StreamHandler(sys.stdout)
            stream_handler.setLevel(LOG_LEVEL)

            # --------------------------
            # File Handler
            # --------------------------
            file_handler = logging.FileHandler(os.path.join(LOG_DIR, LOG_FILE))
            file_handler.setLevel(LOG_LEVEL)

            # --------------------------
            # Formatters
            # --------------------------
            formatter = logging.Formatter(
                "[%(asctime)s] [%(filename)s:%(funcName)s:%(lineno)d] %(levelname)s - %(message)s"
            )
            clean_formatter = CleanFormatter(
                "[%(asctime)s] [%(filename)s:%(funcName)s:%(lineno)d] %(levelname)s - %(message)s"
            )

            stream_handler.setFormatter(formatter)
            file_handler.setFormatter(clean_formatter)

            # --------------------------
            # Syslog Handler (with fallback)
            # --------------------------
            syslog_handler = None
            try:
                # Try UNIX socket (typical Linux /dev/log)
                if os.path.exists("/dev/log"):
                    syslog_handler = SysLogHandler(address="/dev/log")
                else:
                    # Fallback: UDP to localhost:514 or localhost:5514
                    syslog_handler = SysLogHandler(address=("localhost", 5514),  socktype=socket.SOCK_DGRAM)
            except (FileNotFoundError, PermissionError, OSError):
                syslog_handler = None  # If syslog unavailable, skip

            if syslog_handler:
                print(f"====================================>{("localhost", 5514)}")
                syslog_handler.setLevel(LOG_LEVEL)
                syslog_formatter = logging.Formatter(
                    f"{APP_NAME} [%(filename)s:%(lineno)d] %(levelname)s - %(message)s"
                )
                syslog_handler.setFormatter(syslog_formatter)
                logger.addHandler(syslog_handler)

            # --------------------------
            # Add Console and File Handlers
            # --------------------------
            logger.addHandler(stream_handler)
            logger.addHandler(file_handler)

        Logger._loggers[name] = logger
        return logger


# 🔹 Global logger instance
LOGGER = Logger.get_logger(APP_NAME)


# 🔹 Simple test
if __name__ == "__main__":
    logger = Logger.get_logger(__name__)
    logger.info("Logger initialized")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
