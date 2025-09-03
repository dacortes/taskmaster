import logging
import os

# Change accordinly
LOG_LEVEL = os.getenv("LOG_LEVEL", logging.DEBUG)

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
LOG_DIR = os.path.join(ROOT_DIR, "logs")
LOG_FILE = os.path.join(LOG_DIR, "app.log")
APP_NAME = "TaskMaster"

# from Program.ProgramProcess import ProgramProcess
CONFIG_PATH = os.getenv(
    "CONFIG_PATH",
    os.path.abspath(os.path.join(os.path.dirname(__file__), "../../configs/")),
)

if not CONFIG_PATH.endswith("/"):
    CONFIG_PATH += "/"
