import logging
import os
import socket
import sys
from logging.handlers import SysLogHandler

from Constants import APP_NAME, LOG_DIR, LOG_FILE, LOG_LEVEL, REMOTE_SYSLOG

from .CleanFormater import CleanFormatter
from .LastFrameFormatter import LastFrameFormatter

# 🔹 Ensure log directory exists
os.makedirs(LOG_DIR, exist_ok=True)

log_string = "[%(asctime)-19s] [%(filename)-20s %(funcName)-20s %(lineno)-4d] %(levelname)-7s - %(message)s"
datefmt = "%Y-%m-%d %H:%M:%S"


class Logger:
    """
    Custom logger that writes logs to:
      - Console (stdout)
      - File in LOG_DIR
      - Local Syslog (if available)
      - Remote Syslog server (if configured)
    """

    _loggers = {}

    @staticmethod
    def get_logger(name, remote_syslog_server: tuple = None):
        """
        Returns a logger instance. If it does not exist, it creates one.

        :param remote_syslog_server: optional tuple (host, port) to send logs to a remote syslog/UDP server
        """
        if name in Logger._loggers:
            return Logger._loggers[name]

        # Create logger instance
        logger = logging.getLogger(name)
        logger.setLevel(LOG_LEVEL)
        logger.propagate = False  # Prevent messages from propagating to root logger

        # Only add handlers once per logger
        if not logger.handlers:
            # Console Handler
            stream_handler = logging.StreamHandler(sys.stdout)
            stream_handler.setLevel(LOG_LEVEL)

            # File Handler
            file_handler = logging.FileHandler(os.path.join(LOG_DIR, LOG_FILE))
            file_handler.setLevel(LOG_LEVEL)

            formatter = LastFrameFormatter(log_string, datefmt=datefmt)

            # I don't need ASCII code when writing to a file
            clean_formatter = CleanFormatter(log_string, datefmt=datefmt)
            stream_handler.setFormatter(formatter)
            file_handler.setFormatter(clean_formatter)

            # Local Syslog Handler
            syslog_handler = None
            try:
                # Try UNIX socket (typical Linux /dev/log)
                if os.path.exists("/dev/log"):
                    syslog_handler = SysLogHandler(address="/dev/log")
                else:
                    # Fallback: UDP to localhost:514 or 5514 if no /dev/log
                    syslog_handler = SysLogHandler(
                        address=("localhost", 514), socktype=socket.SOCK_DGRAM
                    )
            except (FileNotFoundError, PermissionError, OSError):
                syslog_handler = None  # Skip if syslog unavailable

            if syslog_handler:
                syslog_handler.setLevel(LOG_LEVEL)
                syslog_formatter = CleanFormatter(log_string, datefmt=datefmt)
                syslog_handler.setFormatter(syslog_formatter)
                logger.addHandler(syslog_handler)

            # Remote Syslog Server Handler (optional)
            if remote_syslog_server:
                try:
                    remote_handler = SysLogHandler(
                        address=remote_syslog_server, socktype=socket.SOCK_DGRAM
                    )
                    remote_handler.setLevel(LOG_LEVEL)
                    remote_formatter = CleanFormatter(log_string, datefmt=datefmt)
                    remote_handler.setFormatter(remote_formatter)
                    logger.addHandler(remote_handler)
                except Exception as e:
                    print(
                        f"Could not connect to the remote syslog server {remote_syslog_server}: {e}"
                    )

            # Add Console and File Handlers (always last)
            logger.addHandler(stream_handler)
            logger.addHandler(file_handler)

        Logger._loggers[name] = logger
        return logger


# 🔹 Global logger instance (local syslog + console + file)
# LOGGER = Logger.get_logger(APP_NAME)
LOGGER = Logger.get_logger(APP_NAME, remote_syslog_server=REMOTE_SYSLOG)

# 🔹 Simple test
if __name__ == "__main__":
    local_logger = Logger.get_logger("local_logger")
    local_logger.info("This goes to console, file and local syslog")

    # Remote logger (also sends logs to the remote syslog server)
    remote_logger = Logger.get_logger(
        "remote_logger",
        remote_syslog_server=("127.0.0.1", 5514),  # Change to your remote server
    )
    remote_logger.info("This goes to console, file, local syslog and remote syslog")
    remote_logger.warning("This also reaches the remote syslog server")
    remote_logger.error("Error also sent to the remote syslog server")
    # logger.info("Logger initialized")
    # logger.warning("This is a warning message")
    # logger.error("This is an error message")
