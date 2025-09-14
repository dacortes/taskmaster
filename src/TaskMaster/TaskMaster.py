import signal
import threading
import time

import yaml

from Constants import LIST_NO_RESTART, LIST_RESTART
from Logger import LOGGER as logger
from Program import Program
from Program.BaseUtils import BaseUtils
from Program.ProgramConfig import ProgramConfig

# import sys


class TaskMaster(BaseUtils):
    def __init__(self, config: dict):
        # Registrar el handler
        signal.signal(signal.SIGHUP, self.handle_sighup)
        self.config = config
        self.new_config = None
        self.programs = {}
        self.file_path = self.config["file_path"]

        programs_config = self.config.get("programs", {})
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
                logger.error(
                    f"Error initializing program {v['name']}: {e}",
                    exc_info=True,
                )
        self._num_proc = len(self.programs)
        # self.monitorProcesses()

    def _get_config(self) -> dict:
        logger.debug(f"Reloading YAML file: {self.file_path}")

        with open(self.file_path, "r") as f:
            return yaml.safe_load(f)

    def configCmp(self):
        old_programs = self.config["programs"]
        new_programs = self.new_config.get("programs", None)

        if new_programs is None:
            logger.warning("new programs is None")
            return
        for program, config in new_programs.items():
            restart = False
            if "name" not in config:
                config["name"] = program
            if program not in old_programs:
                self.programs[config["name"]] = Program(config)
                self.startProcess(program)
                continue
            else:
                for cmd in LIST_RESTART:
                    if cmd not in old_programs[program] and cmd not in config:
                        continue
                    if cmd in old_programs[program] and cmd in config:
                        if old_programs[program][cmd] != config[cmd]:
                            restart = True
                            break
                    elif (
                        cmd in config
                        and cmd not in old_programs[program]
                        or cmd in old_programs[program]
                        and cmd not in config
                    ):
                        restart = True
                if restart:
                    self.programs[config["name"]] = Program(config)
                    self.startProcess(program)
                else:
                    new_dict = old_programs[program]
                    no_restart_list = []
                    for cmd in LIST_NO_RESTART:
                        old_cmd = old_programs[program].get(cmd, None)
                        new_cmd = config.get(cmd, None)
                        if old_cmd != new_cmd:
                            no_restart_list.append(cmd)
                            new_dict.update({cmd: new_cmd})
                    if not no_restart_list:
                        continue
                    update = ProgramConfig(new_dict)
                    self.programs[program].updateProcess(update, no_restart_list)

    def monitorProcesses(self):
        def monitor():
            while True:
                try:
                    for program in self.programs.values():
                        program.restartProcess()
                except Exception as e:
                    logger.error(e, exc_info=True)
                time.sleep(1)

        thread = threading.Thread(target=monitor, daemon=True)
        thread.start()

    def getStatus(self, program_name: str = None, process_id: int = None):
        if program_name is None:
            logger.info("Getting status for all programs")
            for name, program in self.programs.items():
                program.getStatus(process_id)
        else:
            if program_name not in self.programs:
                raise ValueError(f"The process {program_name} does not exist")
            logger.info(f"Getting status for program '{program_name}'")
            self.programs[program_name].getStatus(process_id)

    def handle_sighup(self, signum, frame):
        logger.info("signal: SIGHUP, reload config file...")
        self.new_config = self._get_config()
        self.configCmp()
        for program in self.programs.values():
            if program["start_at_launch"]:
                program.rebootProcess()

    def startProcess(self, process_name: str):
        if process_name not in self.programs:
            raise ValueError(self.ERROR + " The process name does not exist")
        try:
            self.programs[process_name].startProcess()
        except Exception as e:
            logger.error(f"{e}")

    def stopProcess(self, process_name: str, index: int = None):
        if process_name not in self.programs:
            raise ValueError(f"The process {process_name} does not exist")
        logger.info(f"Stopping process '{process_name}'")
        self.programs[process_name].stopProcess(index)

    def restartProcess(self, process_name: str = None):
        if process_name and process_name not in self.programs:
            raise ValueError(f"The process {process_name} does not exist")
        logger.info(f"Restarting process '{process_name}'")
        self.programs[process_name].restartProcess()

    def reloadConfig(self):
        logger.info("Reloading configuration (stub).")
        pass

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
