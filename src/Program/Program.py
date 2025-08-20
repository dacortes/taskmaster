from ProgramConfig import ProgramConfig
from ProgramProcess import ProgramProcess

class Program:
    def __init__(self, dict: dict):
        self.program_config = ProgramConfig(dict)
        self.process = ProgramProcess(self.program_config)
        None