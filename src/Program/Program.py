from Logger import LOGGER as logger
from Program.ProgramConfig.ProgramConfig import ProgramConfig
from Program.ProgramProcess.ProgramProcess import ProgramProcess


class Program:
    def __init__(self, dict: dict = None):
        logger.debug(f"Initializing Program with config: {dict}")
        self.program_config = ProgramConfig(dict)
        self.process = ProgramProcess(self.program_config)
        # self.process = ProgramProcess(dict)

    def startProcess(self):
        self.process.startProcess()

    def stopProcess(self):
        try:
            self.process.stopProcess(index=0)
        except Exception as err:
            None

    def __getitem__(self, key):
        return self.process[key]

    def __setitem__(self, key, value):
        self.process[key] = value

    def __delitem__(self, key):
        del self.process[key]

    def __iter__(self):
        return iter(self.process)

    def __len__(self):
        return len(self.process)

    def __contains__(self, key):
        return key in self.process

    def __repr__(self):
        return (
            f"Program(config={self.program_config})"  # TODO ADD SELF.PROCESS PRINT HERE
        )
