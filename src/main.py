import argparse
import os

import yaml

from Program.Program import Program
from Program.ProgramConfig.ProgramConfig import ProgramConfig
from TaskMaster import TaskMaster

# from Program.ProgramProcess import ProgramProcess
CONFIG_PATH = os.getenv("CONFIG_PATH", "../configs/")


def test():
    import os
    import tempfile

    import yaml

    config_data1 = {
        "name": "ls",
        "command": "/bin/ls",
        "processes": 1,
        "env": {"PORT": "8080", "foo": "loco"},
        "expected_exit_codes": [0, 1],
    }

    config_data2 = {
        "name": "loco",
        "command": "/bin/ls -la",
        "processes": 1,
        "expected_exit_codes": [0, 1],
    }
    with tempfile.NamedTemporaryFile(
        delete=False, suffix=".yaml", mode="w"
    ) as tmp_file:
        yaml.dump(config_data1, tmp_file)
        tmp_file_path = tmp_file.name
    config = ProgramConfig(tmp_file_path)
    if config:
        print("Ok")
    os.unlink(tmp_file_path)
    tmp = {}
    tmp.update({config_data1.get("name"): config_data1})
    tmp.update({config_data2.get("name"): config_data2})
    try:
        pro = Program(tmp)
        print(pro)
    except Exception as err:
        print(err)


def get_args():
    parser = argparse.ArgumentParser(
        prog='TaskMaster',
    )
    parser.add_argument(
        "-c",
        "--config",
        type=str,
        required=True,
        help="Path to the configuration file",
    )
    return parser.parse_args()


def get_yaml(path: str) -> dict:
    """
    Load a YAML file and return its contents as a dictionary.

    :param path: The path to the YAML file, uses CONFIG_PATH env to find it.
    :return: The contents of the YAML file as a dictionary.
    """
    if not (path.endswith(".yaml") or path.endswith(".yml")):
        if os.path.exists(CONFIG_PATH + path + ".yaml"):
            path += ".yaml"
        elif os.path.exists(CONFIG_PATH + path + ".yml"):
            path += ".yml"
    with open(CONFIG_PATH + path, "r") as f:
        return yaml.safe_load(f)


def get_tm(args):
    yaml = get_yaml(args.config)
    return TaskMaster(yaml)


if __name__ == "__main__":
    # test()
    args = get_args()
    tm = get_tm(args)
    print(tm)
