import select
import sys

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
            "status": "Show the status of all managed programs.",
            "start": "Start a specific program or all programs.",
            "stop": "Stop a specific program or all programs.",
            "restart": "Restart a specific program or all programs.",
            "reload": "Reload the configuration file.",
            "quit/exit": "Exit the terminal interface.",
            "help": "Show the help message.",
        }
        self.cmd = None
        self.input = None
        self.cmd_options = []

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
        if self.cmd in self.commands:
            self.commands[self.cmd]()
        else:
            print(f"Unknown command: {self.cmd}")

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
        print("[Status] Program is running (stub).")

    def _cmd_start(self):
        print("[Start] Starting program (stub).")

    def _cmd_stop(self):
        print("[Stop] Stopping program (stub).")

    def _cmd_restart(self):
        print("[Restart] Restarting program (stub).")

    def _cmd_reload(self):
        print("[Reload] Reloading config (stub).")

    def _cmd_quit(self):
        print("[Quit] Exiting program.")
        self.running = False
