# Taskmaster

## Overview

Taskmaster is a Python-based process supervisor designed to start, monitor, and manage configured programs in the foreground. It implements a control shell and can reload configuration without stopping unchanged supervised processes. The project follows classic supervisor-style behavior and supports process restart policies, logging, output redirection, environment control, and graceful shutdown.

## Core Features

- Starts programs as child processes and keeps them alive according to configuration.
- Monitors process health and restart policies continuously.
- Reloads configuration on demand via the shell or `SIGHUP` without stopping unchanged processes.
- Provides an interactive control shell with commands for `status`, `start`, `stop`, `restart`, `reload`, and `quit`.
- Logs events to file, console/syslog, and optional remote syslog.
- Supports output redirection, environment variables, working directory, and umask settings.

## Project Structure

- `src/main.py` — application entry point and configuration loader.
- `src/TaskMaster/TaskMaster.py` — main supervisor core handling process groups, configuration reloads, and signal handling.
- `src/Terminal/terminal.py` — interactive terminal interface for runtime control.
- `src/Program/Program.py` — wrapper that connects program configuration and process management.
- `src/Program/ProgramConfig/ProgramConfig.py` — parses and validates YAML program configuration.
- `src/Program/ProgramProcess/ProgramProcess.py` — creates and controls subprocesses, restart behavior, shutdown, and status reporting.
- `src/Logger/Logger.py` — custom logger that writes to file, syslog, and optionally remote syslog.
- `src/Constants/constants.py` — runtime constants, configuration path, and restart logic lists.
- `configs/` — example YAML configuration files.
- `tests/` — basic test coverage for configuration loading and program initialization.

## Configuration

Taskmaster loads a YAML configuration file at startup. The configuration defines one or more supervised programs under the top-level `programs` key.

Example:

```yaml
programs:
  webapp:
    command: "/usr/bin/python3 /opt/webapp/app.py"
    processes: 2
    start_at_launch: true
    restart_policy: "on_failure"
    expected_exit_codes: [0]
    success_timeout: 5
    max_restarts: 3
    stop_signal: "SIGTERM"
    stop_timeout: 10
    stdout: "./webapp.out"
    stderr: "./webapp.err"
    env:
      APP_ENV: "production"
      DB_HOST: "localhost"
    working_dir: "/opt/webapp"
    umask: 027
```

### Supported configuration fields

- `command` (required): command line used to launch the program.
- `processes`: number of child processes to start and keep running.
- `start_at_launch`: whether the program should start automatically.
- `restart_policy`: `always`, `never`, or `on_failure`.
- `expected_exit_codes`: exit codes treated as expected and not considered failures.
- `success_timeout`: seconds a process must remain alive to be considered successfully started.
- `max_restarts`: maximum restart attempts before giving up.
- `stop_signal`: signal name used for graceful shutdown.
- `stop_timeout`: seconds to wait after graceful stop before forcing kill.
- `stdout`: file path to redirect standard output.
- `stderr`: file path to redirect standard error.
- `discard_output`: disable capturing stdout/stderr entirely.
- `env`: environment variables for the supervised process.
- `working_dir`: working directory for the process.
- `umask`: file creation mask applied before launching the process.

## Supported Commands

Taskmaster exposes a simple shell with these commands:

- `status [program_name] [process_id]` — show status for all programs or a specific program/process.
- `start <program_name>` — start a configured program.
- `stop <program_name> [index]` — stop a program or a specific process instance.
- `restart [program_name]` — restart a program or all programs.
- `reload` — reload the YAML configuration file and apply changes.
- `quit` / `exit` — stop Taskmaster and exit cleanly.

## Signal Handling

- `SIGHUP` reloads the configuration file without stopping unchanged programs.
- `SIGINT` exits Taskmaster gracefully.

## Logging

Taskmaster logs significant events such as process start, stop, restart, configuration reload, and failures.

Logging destinations include:

- local log file under `logs/app.log`
- local syslog when available
- optional remote syslog via UDP (configured in `src/Constants/constants.py`)

## Run Instructions

Install dependencies from `requirements.txt`:

```bash
pip install -r requirements.txt
```

Run Taskmaster with a YAML configuration file:

```bash
python src/main.py -c configs/all_config.yaml
```

If the config file name is relative, Taskmaster resolves it relative to the `configs/` directory by default.

## Example Workflow

1. Start Taskmaster in the foreground.
2. Use `status` to inspect supervised programs.
3. Use `stop`, `start`, or `restart` to manage individual programs.
4. Use `reload` or send `SIGHUP` to apply configuration changes.
5. Use `quit` or `exit` to shut down cleanly.

## Testing

Run the available tests with pytest:

```bash
pytest
```

## Project Notes

This implementation matches the required Taskmaster behavior:

- it manages child processes and monitors their lifecycle accurately,
- it uses YAML configuration loading compatible with the allowed parser library,
- it supports reloadable configuration without restarting unchanged programs,
- it provides a foreground control shell and logging system,
- it implements restart policies, expected exit codes, startup success timeouts, graceful stop signals, stop timeouts, output redirection, environment variables, working directory, and umask.

The code is designed to be extensible for additional bonus features such as remote logging or a daemon/control client separation.

