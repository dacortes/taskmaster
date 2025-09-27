import select
import sys

from Logger import LOGGER as logger
from TaskMaster import TaskMaster as TM


class InteractiveTerminal:
    def __init__(self, config=None):
        if config is None:
            raise ValueError("Configuration must be provided")
        self.config = config
        self.tm = TM(self.config)
        self.running = True
        self.commands = {
            "status": self._cmd_status,
            "start": self._cmd_start,
            "stop": self._cmd_stop,
            "restart": self._cmd_restart,
            "reload": self._cmd_reload,
            "quit": self._cmd_quit,
            "exit": self._cmd_quit,
            "help": self._cmd_help,
        }
        self.commands_help = {
            "status": "status <program_name> [process_id]\n    Show the status of a specific program (optionally for a given process ID).",
            "start": "start <program_name>\n    Start a specific program.",
            "stop": "stop <program_name> [index]\n    Stop a specific program (optionally one process by index).",
            "restart": "restart [program_name]\n    Restart a specific program, or all programs if none is specified.",
            "reload": "reload\n    Reload the configuration file.",
            "quit/exit": "quit | exit\n    Exit the terminal interface.",
            "help": "help\n    Show this help message.",
        }

        self.cmd = None
        self.input = None
        self.cmd_options = []
        logger.info("Interactive terminal initialized.")

    def run(self):
        self.commands["help"]()
        first_prompt = True

        while self.running:
            try:
                self.input = self._timed_input(timeout=1, show_prompt=first_prompt)
                first_prompt = False
                if self.input is not None:
                    # Got an input line, need to print prompt next time
                    first_prompt = True
                    self._parse_input()
                    self._dispatch()

            except (KeyboardInterrupt, EOFError):
                self._cmd_quit()
            except Exception as e:
                logger.error(e, exc_info=True)

    def _timed_input(self, timeout=1, show_prompt=False):
        """Return input if available within `timeout` seconds, else None."""
        if show_prompt:
            print("> ", end="", flush=True)
        if select.select([sys.stdin], [], [], timeout)[0]:
            return sys.stdin.readline().strip()
        return None

    def _dispatch(self):
        if self.cmd is None:
            return
        try:
            if self.cmd in self.commands:
                self.commands[self.cmd]()
            else:
                print(f"Unknown command: {self.cmd}")
        except Exception as e:
            logger.error(e, exc_info=True)

    def _parse_input(self):
        parts = self.input.split()
        if parts:
            self.cmd = parts[0]
            self.cmd_options = parts[1:]
        else:
            self.cmd = None
            self.cmd_options = []

    def _cmd_help(self):
        if self.cmd is None or self.cmd_options == []:
            print("Available commands: " + ", ".join(self.commands.keys()))
        elif self.cmd_options[0] in self.commands_help:
            print(f"{self.cmd_options[0]}: {self.commands_help[self.cmd_options[0]]}")
        else:
            print(f"No help available for '{self.cmd_options[0]}'")

    def _cmd_status(self):
        process_name = self.cmd_options[0] if self.cmd_options else None
        self.tm.getStatus(process_name)

    def _cmd_start(self):
        process_name = self.cmd_options[0] if self.cmd_options else None
        self.tm.startProcess(process_name)

    def _cmd_stop(self):
        process_name = self.cmd_options[0] if self.cmd_options else None
        index = int(self.cmd_options[1]) if len(self.cmd_options) > 1 else None
        self.tm.stopProcess(process_name, index)

    def _cmd_restart(self):
        process_name = self.cmd_options[0] if self.cmd_options else None
        self.tm.restartProcess(process_name, cmd_terminal=True)

    def _cmd_reload(self):
        self.tm.reloadConfig()

    def _cmd_quit(self):
        print("[Quit] Exiting program.")
        self.running = False
        self.tm.__del__()
