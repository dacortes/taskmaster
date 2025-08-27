from pathlib import Path


class ProgramConfig(dict):
    def __init__(self, program_config: dict):
        super().__init__()
        self.program_config = program_config
        self._load_config()

    def _load_config(self):
        """
        Load and validate program configuration from a YAML file.

        This method reads the YAML file specified by `self.config_path` and sets
        all the configuration attributes of the ProgramConfig instance, applying
        defaults where values are missing. It also validates required fields and
        checks for incompatible options.

        Attributes set by this method:
            command (str): The command to launch the program (required).
            processes (int): Number of processes to start and keep running (default: 1).
            start_at_launch (bool): Whether to start this program at launch
                                    (default: False).
            restart_policy (str): Restart policy: 'always', 'never', or 'on_failure'
                                    (default: 'on_failure').
            expected_exit_codes (List[int]): List of exit codes considered successful
                                    (default: [0]).
            success_timeout (int): Seconds the program must run to be considered
                                    successfully started (default: 5).
            max_restarts (int): Maximum number of restart attempts before aborting (default: 3).
            stop_signal (str): Signal to use for graceful shutdown (default: 'SIGTERM').
            stop_timeout (int): Seconds to wait after graceful stop before killing the program (default: 10).
            stdout (Optional[str]): File path to redirect standard output (default: None).
            stderr (Optional[str]): File path to redirect standard error (default: None).
            discard_output (bool): Whether to discard stdout/stderr instead of redirecting (default: False).
            env (Dict[str, str]): Environment variables to set before launching the program (default: {}).
            working_dir (str): Working directory to set before launching the program (default: current working directory).
            umask (str): Umask to set before launching the program (default: '022').

        Raises:
            FileNotFoundError: If the YAML configuration file does not exist.
            ValueError: If the required 'command' field is missing or if
                        discard_output is True while stdout or stderr are set.
        """
        # Command and process settings
        self["name"] = self.program_config.get("name", None)
        if not self["name"]:
            raise ValueError("Missing required config key: name")
        self["command"] = self.program_config.get(
            "command", self.program_config.get("cmd", None)
        )
        if not self["command"]:
            raise ValueError("Missing required config key: command")
        self["processes"] = int(self.program_config.get("processes", 1))
        self["start_at_launch"] = bool(
            self.program_config.get("start_at_launch", False)
        )
        self["restart_policy"] = self.program_config.get("restart_policy", "on_failure")
        self["expected_exit_codes"] = [
            int(code) for code in self.program_config.get("expected_exit_codes", [0])
        ]
        self["success_timeout"] = int(
            self.program_config.get("success_timeout", 5)
        )  # seconds
        self["max_restarts"] = int(self.program_config.get("max_restarts", 3))

        # Stopping behavior
        self["stop_signal"] = self.program_config.get("stop_signal", "SIGTERM")
        self["stop_timeout"] = int(self.program_config.get("stop_timeout", 10))

        # Logging
        self["stdout"] = self.program_config.get("stdout", None)
        self["stderr"] = self.program_config.get("stderr", None)
        self["discard_output"] = bool(self.program_config.get("discard_output", False))
        if self["discard_output"] and (self["stdout"] or self["stderr"]):
            raise ValueError("Cannot discard output if stdout or stderr are set")

        # Environment & execution context
        self["env"] = {
            str(k): str(v) for k, v in self.program_config.get("env", {}).items()
        }
        self["working_dir"] = self.program_config.get("working_dir", str(Path.cwd()))
        self["umask"] = self.program_config.get("umask", "022")

    def __repr__(self):
        attrs = "\n  ".join(f"{k}={v!r}" for k, v in vars(self).items())
        return f"<ProgramConfig:\n  {attrs}\n>"


if __name__ == "__main__":
    config_data = {
        "name": "myprogram",
        "command": "/usr/bin/myprogram",
        "processes": 2,
        "start_at_launch": True,
        "restart_policy": "always",
        "expected_exit_codes": [0, 1],
    }

    # Load the config
    cfg = ProgramConfig(config_data)
    print(cfg)
