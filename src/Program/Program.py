from Logger import LOGGER as logger
from Program.ProgramConfig.ProgramConfig import ProgramConfig
from Program.ProgramProcess.ProgramProcess import ProgramProcess


class Program:
    def __init__(self, dict: dict = None):
        logger.debug(f"Initializing Program with config: {dict}")
        self._program_config = ProgramConfig(dict)
        self._process = ProgramProcess(self._program_config)
        self.startProcess()

    def startProcess(self):
        self._process.startProcess()

    def stopProcess(self):
        try:
            self._process.stopProcess(index=0)
        except Exception:
            None

    def Restart(self):
        try:
            self._process.Restart()
        except Exception:
            None

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
