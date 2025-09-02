import copy
import os
import subprocess
import time

from Logger import LOGGER as logger
from Program.BaseUtils import BaseUtils
from Program.ProgramConfig import ProgramConfig


class ProgramProcess(BaseUtils, dict):
    def printContent(self, data):
        for key, value in data:
            logger.debug(
                self.BLUE + self.LIGTH + str(key) + self.END + ": " + str(value)
            )

    def addDataProcess(self, data: ProgramConfig):
        for proc, cont in data.items():
            self[proc] = copy.deepcopy(cont)

    def startProcess(self):
        logger.info(f"Starting process: {self['name']}")
        process_name = self["name"]
        command = self.get("command").split()
        working_directory = self.get("working_dir", None)
        if working_directory:
            working_directory = os.path.expanduser(working_directory)
        else:
            working_directory = None
        logger.debug(working_directory)
        env = os.environ.copy()
        if "env" in self:
            env.update(self["env"])

        stdout = subprocess.PIPE
        stderr = subprocess.PIPE
        if self.get("stdout", ""):
            stdout = open(os.path.expanduser(self["stdout"]), "a")
        if self.get("stderr", ""):
            stderr = open(os.path.expanduser(self["stderr"]), "a")

        try:
            process = subprocess.Popen(
                command,
                cwd=working_directory,
                env=env,
                stdout=stdout,
                stderr=stderr,
                shell=self.get("shell", False),
                preexec_fn=os.setsid if self.get("umask") else None,
            )
            self["_process"] = process
            self["_pid"] = process.pid
            self["_status"] = "running"
            self[
                "_start_time"
            ] = time.time()  # cambiar por el del parametro solo para prueba
            logger.debug(
                f"{self.GREEN}{self.LIGTH}Process{self.END} '{process_name}' initialized (PID: {process.pid})"
            )

        except Exception as err:
            raise ValueError(
                self.ERROR
                + " in process initialization "
                + process_name
                + ":"
                + str(err)
            )

    def stopProcess(self):
        process_name = self["name"]
        if self["_process"] is None:
            raise ValueError(
                self.ERROR + "Process" + process_name + "it is not running"
            )
        process = self["_process"]

        try:
            process.terminate()
            try:
                process.wait(timeout=5)
            except Exception as e:
                process.kill()
                process.wait()
                raise e
            self["_status"] = "stopped"
            self["_stop_time"] = time.time()  # lo mismo que arriba loco
            logger.warning(f"{self.YELLOW} Process {self.END} '{process_name}' stopped")
            return True
        except Exception as err:
            raise ValueError(
                self.ERROR + " stopping process: " + process_name + ":" + err
            )

    def __init__(self, pc: dict):
        logger.info("Initializing ProgramProcess")
        if pc is None:
            logger.error("Null parameter in constructor")
            raise ValueError(self.ERROR + " Null parameter in constructor")
        self["_process"] = None
        self.addDataProcess(pc)
        self.printContent(self.items())
