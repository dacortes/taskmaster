import copy
import os
import signal
import subprocess
import time

from Logger import LOGGER as logger
from Program.BaseUtils import BaseUtils
from Program.ProgramConfig import ProgramConfig


class ProgramProcess(BaseUtils, dict):
    @staticmethod
    def nothing(obj):
        pass

    @staticmethod
    def processUpdate(obj):
        if obj.old_num_proc > obj._num_proc:
            for index in range(obj._num_proc, obj.old_num_proc):
                index += 1
                logger.info(
                    f"About to destroy process {index} of program {obj['name']} "
                )
                obj.stopProcess(index)
        elif obj.old_num_proc < obj._num_proc:
            for index in range(obj.old_num_proc, obj._num_proc):
                index += 1
                obj._processes[index] = obj._initProcess(
                    name_proc=obj["name"], index=index
                )

    @staticmethod
    def startUpdate(obj):
        if obj._old_start_at_launch != obj["start_at_launch"]:
            if obj["start_at_launch"]:
                if obj._processes:
                    obj.rebootProcess()
                else:
                    obj.startProcess()
            else:
                obj.stopProcess(flag=True)

    attr_map = {
        "processes": ("_num_proc", processUpdate),
        "start_at_launch": ("_start_at_launch", startUpdate),
        "restart_policy": ("_restart_policy", nothing),
        "expected_exit_codes": ("_expected_exit_codes", nothing),
        "success_timeout": ("_success_timeout", nothing),
        "max_restarts": ("_max_restarts", nothing),
        "stop_signal": ("_stop_signal", nothing),
        "stop_timeout": ("_stop_timeout", nothing),
    }
    """
    ProgramProcess is a class for managing and controlling multiple subprocesses with advanced configuration options.
    Inherits from:
        BaseUtils, dict
    Args:
        pc (dict): Dictionary containing process configuration parameters.
    Raises:
        ValueError: If the input configuration dictionary is None or if process initialization/stopping fails.
    Attributes:
        _num_proc (int): Number of processes to manage.
        _processes (dict): Dictionary holding information about each managed process.
        _command (list): Command to execute for the subprocess.
        _working_directory (str): Working directory for the subprocess.
        _use_shell (bool): Whether to use shell for subprocess execution.
        _max_restarts (int): Maximum number of allowed restarts for a process.
        _success_timeout (float): Timeout to consider a process as successfully started.
        _restart_policy (str): Policy for restarting processes ("always", "unexpected", "never").
        _start_at_launch (bool): Whether to start processes automatically at launch.
        _expected_exit_codes (list): List of exit codes considered as expected.
        _env (dict): Environment variables for the subprocess.
        _preexec_fn (callable): Function to execute in the child process before running the command.
        _stop_timeout (float): Timeout for stopping a process.
        _stop_signal (signal): Signal used to stop a process.
    Methods:
        printContent(data): Prints the content of the process configuration.
        addDataProcess(data): Adds process configuration data to the instance.
        _initRedirectionFile(num_proc, name_file, index): Initializes file redirection for process output.
        _initProcess(name_proc, index): Initializes a single subprocess and stores its metadata.
        _createProcess(): Creates and starts all configured subprocesses.
        _getStopSignal(): Retrieves the signal to use for stopping processes.
        _stopSingleProcess(process): Stops a single subprocess, force kills if timeout is exceeded.
        _stopAllProcess(): Stops all managed subprocesses.
        _getProcess(index=None, pid=None): Retrieves process information by index or PID.
        _restartProcessIfNeeded(index): Restarts a process if needed based on the restart policy.
        startProcess(): Starts processes based on the configuration.
        stopProcess(index=None, pid=None): Stops a specific process or all processes based on configuration.
    """

    def __init__(self, pc: dict):
        if pc is None:
            raise ValueError(self.ERROR + " Null parameter in constructor")
        self.addDataProcess(pc)
        self._num_proc = self.get("processes")
        self._processes = {}
        self._log_restart_fails = True

    def __del__(self):
        self.stopProcess()

    def printContent(self, data):
        for key, value in data:
            logger.debug(
                self.BLUE + self.LIGTH + str(key) + self.END + ": " + str(value)
            )

    def addDataProcess(self, data: ProgramConfig):
        for proc, cont in data.items():
            self[proc] = copy.deepcopy(cont)

    def updateProcess(self, data_update: ProgramConfig, no_restart_list: list):
        self.old_num_proc = self._num_proc
        self._old_start_at_launch = self["start_at_launch"]
        for idx in range(0, len(no_restart_list)):
            logger.debug(f"update no restart list -- {no_restart_list[idx]}")
            parameter = no_restart_list[idx]
            self[parameter] = data_update[parameter]
            if parameter in self.attr_map:
                private_attr_name, _ = self.attr_map[parameter]
                setattr(self, private_attr_name, data_update[parameter])

        for idx in range(0, len(no_restart_list)):
            logger.debug(f"call function update -- {no_restart_list[idx]}")
            parameter = no_restart_list[idx]
            self[parameter] = data_update[parameter]
            if parameter in self.attr_map:
                _, update_func = self.attr_map[parameter]
                update_func(self)
        logger.info(f"Process '{self['name']}' configuration updated.")

    @staticmethod
    def _initRedirectionFile(num_proc, name_file, index):
        file_output = name_file
        if num_proc > 1:
            base, ext = os.path.splitext(file_output)
            file_output = f"{base}{index}{ext}"
        file_output = open(os.path.expanduser(file_output), "a")
        return file_output

    def _initProcess(self, name_proc, index) -> dict:
        curr_name = f"{name_proc}" + (f"{index}" if self._num_proc > 1 else "")
        new_process = {}
        stdout = subprocess.PIPE
        stderr = subprocess.PIPE
        if self.get("discard_output", False):
            stdout = subprocess.DEVNULL
            stderr = subprocess.DEVNULL
        else:
            if self.get("stdout", ""):
                stdout = self._initRedirectionFile(
                    self._num_proc, self["stdout"], index
                )
            if self.get("stderr", ""):
                stderr = self._initRedirectionFile(
                    self._num_proc, self["stderr"], index
                )
        try:
            process = subprocess.Popen(
                self._command,
                cwd=self._working_directory,
                env=self._env,
                stdout=stdout,
                stderr=stderr,
                shell=self._use_shell,
                preexec_fn=self._preexec_fn,
            )
            new_process["_popen"] = process
            new_process['_pid'] = process.pid
            new_process["_status"] = "starting"
            new_process["_start_time"] = time.time()
            new_process["_restarts"] = 0
            logger.debug(
                f"{self.GREEN}{self.LIGTH}Process{self.END} '{curr_name}' initialized (PID: {process.pid})"
            )
        except Exception as err:
            raise ValueError(f"In process initialization {curr_name}: {err}")
        return new_process

    def _createProcess(self):
        self._command = self.get("command", "").split()
        self._working_directory = self.get("working_dir", None)
        self._use_shell = self.get("shell", False)

        self._max_restarts = self.get("max_restarts")
        self._success_timeout = self.get("success_timeout")
        self._restart_policy = self.get("restart_policy")
        self._start_at_launch = self.get("start_at_launch")
        self._expected_exit_codes = self.get("expected_exit_codes")

        if self._working_directory:
            self._working_directory = os.path.expanduser(self._working_directory)
        else:
            self._working_directory = None

        self._env = os.environ.copy()
        if "env" in self:
            self._env.update(self["env"])

        self._preexec_fn = None
        if "umask" in self:
            umask_val = self["umask"]
            self._preexec_fn = lambda: os.umask(umask_val)
        for new in range(1, self._num_proc + 1):
            self._processes[new] = self._initProcess(name_proc=self["name"], index=new)

    def _getStopSignal(self):
        signal_name = self.get("stop_signal")
        return getattr(signal, signal_name, signal.SIGTERM)

    def _stopSingleProcess(self, process):
        os.kill(process.pid, self._stop_signal)
        try:
            process.wait(timeout=self._stop_timeout)
        except subprocess.TimeoutExpired:
            os.kill(process.pid, signal.SIGKILL)
            process.wait()
            logger.warning(
                f"{self.YELLOW}Process '{process.pid}' force killed with SIGKILL after timeout{self.END}"
            )
        logger.info(f"Process '{process.pid}' stopped.")

    def _stopAllProcess(self):
        print(f"buenas loco jajjajajajjajajaja {self}")
        for new in range(1, self._num_proc + 1):
            if (new) in self._processes and self._processes[new][
                "_status"
            ] == "running":
                process = self._processes[new]["_popen"]
                try:
                    self._stopSingleProcess(process)
                    self._processes[new]["_status"] = "stopped"
                    self._processes[new]["_exit_code"] = process.returncode
                    self._processes[new]["stop_time"] = time.time()
                    self._processes[new]["_stop_signal_used"] = self._stop_timeout
                    logger.debug(
                        f"{self.YELLOW} Process {self.END} program index:{new} -- pid:{self._processes[new]['_pid']} {self.RED}{self.LIGTH}stopped{self.END}"
                    )
                except Exception as err:
                    raise ValueError(
                        f"{self.ERROR} stopping process: {self._processes[new]['_pid']}: {err}"
                    )

    def _getProcess(self, index=None, pid=None):
        proc = self._processes.get(index, None)
        if proc is None:
            proc = self._processes.get(pid, None)
        return proc

    def _restartProcessIfNeeded(self, index):
        if not self._processes or self["start_at_launch"] == False:
            return
        proc_info = self._processes[index]
        exit_code = proc_info["_popen"].poll()
        if exit_code is None:
            return
        restart_needed = False

        if self._restart_policy == "always":
            restart_needed = True
        elif (
            self._restart_policy == "unexpected"
            or self._restart_policy == "on_failure"
            and exit_code not in self._expected_exit_codes
        ):
            restart_needed = True
        elif self._restart_policy == "never":
            restart_needed = False
        if restart_needed:
            restarts = proc_info.get("_restarts", 0)
            if restarts < self._max_restarts:
                logger.info(
                    f"{self.YELLOW}Restarting process index {index}...{self.END}"
                )
                self._processes[index] = self._initProcess(
                    name_proc=self["name"], index=index
                )
                self._processes[index]["_restarts"] = restarts + 1
            else:
                if self._log_restart_fails:
                    self._log_restart_fails = False
                    proc_info["_exit_code"] = exit_code
                    logger.info(
                        f"{self.RED}Max restarts reached for process index {index}{self.END}"
                    )
        else:
            proc_info["_status"] = "closed"
            proc_info["_exit_code"] = exit_code
            # logger.info(
            #     f"Process index {index} exited normally with code {exit_code}"
            # )

    def restartProcess(self):
        for index in range(1, self._num_proc + 1):
            self._restartProcessIfNeeded(index)

    def rebootProcess(self):
        for index in range(1, self._num_proc + 1):
            proc = self._processes.get(index, None)
            if proc is None:
                continue
            if proc["_status"] != "running" and proc["_status"] != "starting":
                new = self._initProcess(name_proc=self["name"], index=index)
                self._processes.update({index: new})

    def getStatus(self, process_id=None):
        if not self._processes:
            return
        for index in range(1, self._num_proc + 1):
            proc = self._processes[index]
            if process_id is None or proc['_pid'] == process_id:
                status = proc["_status"]
                pid = proc['_pid']
                start_time = time.strftime(
                    "%Y-%m-%d %H:%M:%S", time.localtime(proc["_start_time"])
                )
                exit_code = proc.get("_exit_code", "N/A")
                restarts = proc.get("_restarts", 0)
                print(
                    f"Program:{self['name']} Process index: {index}, PID: {pid}, Status: {status}, Start Time: {start_time}, Exit Code: {exit_code}, Restarts: {restarts}"
                )

    def startProcess(self):
        start_at_launch = self.get("start_at_launch")
        if start_at_launch:
            self._createProcess()
        else:
            logger.info(
                f"{self.YELLOW}Skipping auto-start for process: {self['name']}{self.END}"
            )

    def stopProcess(self, index=None, pid=None, flag=None):
        self._stop_timeout = self.get("stop_timeout")
        self._stop_signal = self._getStopSignal()

        if index is not None or pid is not None:
            stop = self._getProcess(index, pid)
            if stop is None:
                return
            if stop["_status"] != "running":
                return
            logger.debug(stop)
            try:
                process = stop["_popen"]
                self._stopSingleProcess(process)
                stop["_status"] = "stopped"
                stop["_exit_code"] = process.returncode
                stop["stop_time"] = time.time()
                stop["_stop_signal_used"] = self._stop_timeout
            except Exception as err:
                raise ValueError(
                    f"{self.ERROR} stopping process: {stop['_pid']}: {err}"
                )

        elif self["start_at_launch"]:
            self._stopAllProcess()
        elif flag is not None:
            self._stopAllProcess()

    def check_startup_timeouts(self):
        current_time = time.time()
        for index in range(1, self._num_proc + 1):
            proc_info = self._processes.get(index)
            if not proc_info:
                continue

            if proc_info["_status"] == "starting":
                proc = proc_info["_popen"]

                if proc.poll() is not None:
                    proc_info["_status"] = "exited"
                    proc_info["_successful"] = False
                    logger.warning(
                        f"{self.RED}Program '{self['name']}', Process index {index} exited "
                        f"before reaching success_timeout ({self._success_timeout}s).{self.END}"
                    )
                    continue

                elapsed_time = current_time - proc_info["_start_time"]
                if elapsed_time >= self._success_timeout:
                    proc_info["_status"] = "running"
                    proc_info["_successful"] = True
                    logger.info(
                        f"{self.GREEN}Program '{self['name']}', Process index {index} "
                        f"has successfully started after {self._success_timeout}s.{self.END}"
                    )
