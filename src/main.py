from Program.ProgramConfig.ProgramConfig import ProgramConfig
from Program.Program import Program

# from Program.ProgramProcess import ProgramProcess

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
    tmp.update({config_data1.get("name"):config_data1})
    tmp.update({config_data2.get("name"):config_data2})
    try:
        pro = Program(tmp)
        print(pro)
    except Exception as err:
        print(err)


if __name__ == "__main__":
    test()