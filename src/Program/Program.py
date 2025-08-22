from Program.ProgramConfig.ProgramConfig import ProgramConfig
from Program.ProgramProcess.ProgramProcess import ProgramProcess


class Program:
    def __init__(self, dict: dict = None):
        self.program_config = ProgramConfig(dict)
        self.process = ProgramProcess(self.program_config)
        # self.process = ProgramProcess(dict)

    def __repr__(self):
        return (
            f"Program(config={self.program_config})"  # TODO ADD SELF.PROCESS PRINT HERE
        )
