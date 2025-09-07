import argparse
import os

import yaml

from Constants import CONFIG_PATH
from Logger import LOGGER as logger
from TaskMaster import TaskMaster


def get_args():
    parser = argparse.ArgumentParser(
        prog='TaskMaster',
    )
    parser.add_argument(
        "-c",
        "--config-file",
        type=str,
        required=True,
        help="Path to the configuration file",
    )
    return parser.parse_args()


def get_yaml(file: str) -> dict:
    """
    Load a YAML file and return its contents as a dictionary.

    :param file: The file name, uses CONFIG_PATH env to find it.
    :return: The contents of the YAML file as a dictionary.
    """
    logger.debug(f"Loading YAML file: {file}")
    if not (file.endswith(".yaml") or file.endswith(".yml")):
        if os.path.exists(CONFIG_PATH + file + ".yaml"):
            file += ".yaml"
        elif os.path.exists(CONFIG_PATH + file + ".yml"):
            file += ".yml"
    with open(CONFIG_PATH + file, "r") as f:
        return yaml.safe_load(f)


def get_tm(args):
    yaml = get_yaml(args.config_file)
    return TaskMaster(yaml)


if __name__ == "__main__":
    args = get_args()
    tm = get_tm(args)
    tm.startProcess("ls")
    tm.stopProcess("ls")
    # print(tm)
