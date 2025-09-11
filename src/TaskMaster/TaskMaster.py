import threading
import time

from Logger import LOGGER as logger
from Program import Program
from Program.BaseUtils import BaseUtils


class TaskMaster(BaseUtils):
    def __init__(self, config: dict):
        self.config = config
        self.programs = {}

        programs_config = config.get("programs", {})
        if not programs_config:
            raise ValueError("No programs defined in configuration")

        for k, v in programs_config.items():
            # Since we don't include name in the configs,
            # we assign name using the key in the list of dicts
            if "name" not in v:
                v["name"] = k
            try:
                self.programs[v["name"]] = Program(v)
            except Exception as e:
                logger.error(f"Error initializing program {v['name']}: {e}")
        self._num_proc = len(self.programs)
        self.monitorProcesses()

    def monitorProcesses(self):
        def monitor():
            while True:
                for program in self.programs.values():
                    program.Restart()
                time.sleep(1)

        thread = threading.Thread(target=monitor, daemon=True)
        thread.start()

    def startProcess(self, process_name: str):
        if process_name not in self.programs:
            logger.error(f"Process {process_name} does not exist")
            raise ValueError(self.ERROR + " The process name does not exist")
        self.programs[process_name].startProcess()

    def stopProcess(self, process_name: str):
        if process_name not in self.programs:
            logger.error(f"Process {process_name} does not exist")
            raise ValueError(self.ERROR + " The process name does not exist")
        self.programs[process_name].stopProcess()

    def __repr__(self):
        return (
            f"TaskMaster(config={self.config}, programs={[p for p in self.programs]})"
        )


if __name__ == '__main__':
    config = {
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
        }
    }

    tm = TaskMaster(config)
    print(tm)
