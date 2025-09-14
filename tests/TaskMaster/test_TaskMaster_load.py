import pytest

from TaskMaster import TaskMaster


def make_config():
    return {
        "file_path": "/tmp/test_config.yaml",
        "programs": {
            "nginx": {
                "cmd": "/usr/local/bin/nginx -c /etc/nginx/test.conf",
                "numprocs": 1,
                "umask": 0o22,
                "workingdir": "/tmp",
                "autostart": True,
                "autorestart": "unexpected",
                "exitcodes": [0, 2],
                "startretries": 3,
                "starttime": 5,
                "stopsignal": "TERM",
                "stoptime": 10,
                "stdout": "/tmp/nginx.stdout",
                "stderr": "/tmp/nginx.stderr",
                "env": {
                    "STARTED_BY": "taskmaster",
                    "ANSWER": 42,
                },
            },
            "vogsphere": {
                "cmd": "/usr/local/bin/vogsphere-worker --no-prefork",
                "numprocs": 8,
                "umask": 0o77,
                "workingdir": "/tmp",
                "autostart": True,
                "autorestart": "unexpected",
                "exitcodes": 0,
                "startretries": 3,
                "starttime": 5,
                "stopsignal": "USR1",
                "stoptime": 10,
                "stdout": "/tmp/vgsworker.stdout",
                "stderr": "/tmp/vgsworker.stderr",
            },
        },
    }


def test_init_assigns_program_names():
    config = make_config()
    tm = TaskMaster(config)
    names = [p for p in tm.programs]
    assert names == ["nginx", "vogsphere"]


def test_raises_if_no_programs():
    with pytest.raises(ValueError):
        TaskMaster({"file_path": "/tmp/test_config.yaml", "programs": {}})

    with pytest.raises(ValueError):
        TaskMaster({"file_path": "/tmp/test_config.yaml", "programs": {}})
