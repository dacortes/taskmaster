from Logger import LOGGER as logger
from Program.ProgramConfig.ProgramConfig import ProgramConfig
from Program.ProgramProcess.ProgramProcess import ProgramProcess


class Program:
    def __init__(self, dict: dict = None):
        logger.debug(f"Initializing Program with config: {dict}")
        self._program_config = ProgramConfig(dict)
        self._process = ProgramProcess(self._program_config)
        logger.debug(f"Program '{self._program_config.name}' initialized.")

    def getStatus(self, process_id: int = None):
        self._process.getStatus(process_id)

    def updateProcess(self, ProgramConfig, cmdList):
        self._process.updateProcess(ProgramConfig, cmdList)

    def startProcess(self):
        self._process.startProcess()

    def stopProcess(self, index=None):
        self._process.stopProcess(index)

    def restartProcess(self):
        self._process.restartProcess()

    def check_startup_timeouts(self):
        self._process.check_startup_timeouts()

    def rebootProcess(self):
        self._process.rebootProcess()

    def get(self, key, default=None):
        return self._process.get(key, default)

    def update(self, other_dict):
        self._process.update(other_dict)

    def __getitem__(self, key):
        return self._process[key]

    def __setitem__(self, key, value):
        self._process[key] = value

    def __delitem__(self, key):
        del self._process[key]

    def __iter__(self):
        return iter(self._process)

    def __len__(self):
        return len(self._process)

    def __contains__(self, key):
        return key in self._process

    def __repr__(self):
        return f"Program(config={self._program_config})"  # TODO ADD SELF.PROCESS PRINT HERE
