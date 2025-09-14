import argparse
import os
import sys

import yaml

from Constants import CONFIG_PATH
from Logger import LOGGER as logger
from Terminal import Terminal


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


def get_config(file: str) -> dict:
    """
    Load a YAML file and return its contents as a dictionary.

    :param file: File name or absolute path. If relative, uses CONFIG_PATH.
    :return: Contents of the YAML file as a dictionary.
    """
    logger.debug(f"Loading YAML file: {file}")

    if not os.path.isabs(file):
        if not (file.endswith(".yaml") or file.endswith(".yml")):
            if os.path.exists(os.path.join(CONFIG_PATH, file + ".yaml")):
                file += ".yaml"
            elif os.path.exists(os.path.join(CONFIG_PATH, file + ".yml")):
                file += ".yml"
        file = os.path.join(CONFIG_PATH, file)

    with open(file, "r") as f:
        return yaml.safe_load(f), file


def main():
    res = 0
    logger.info("Starting TaskMaster...")
    try:
        args = get_args()
        config = get_config(args.config_file)
        terminal = Terminal(config)
        terminal.run()
    except BaseException as e:
        logger.error(e, exc_info=True)
        res = 1
    return res


if __name__ == "__main__":
    sys.exit(main())
