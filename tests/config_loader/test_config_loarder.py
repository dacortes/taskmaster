import os
import sys
import tempfile
import unittest

# Add the 'src' directory to sys.path
sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../src"))
)
from pathlib import Path

import yaml

from ProgramConfig.ProgramConfig import ProgramConfig


class TestProgramConfig(unittest.TestCase):
    def setUp(self):
        # Create a temporary YAML file
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".yaml")
        self.config_data = {
            "command": "/usr/bin/myprogram --config /etc/myprogram/config.yaml",
            "processes": 2,
            "start_at_launch": True,
            "restart_policy": "always",
            "expected_exit_codes": [0, 2],
            "success_timeout": 15,
            "max_restarts": 5,
            "stop_signal": "SIGTERM",
            "stop_timeout": 20,
            "stdout": "/tmp/out.log",
            "stderr": "/tmp/err.log",
            "discard_output": False,
            "env": {"APP_ENV": "production", "DB_PORT": 5432},
            "working_dir": "/opt/myprogram",
            "umask": "027",
        }
        yaml.dump(self.config_data, open(self.temp_file.name, "w"))

    def tearDown(self):
        os.unlink(self.temp_file.name)

    def test_load_config(self):
        cfg = ProgramConfig(self.temp_file.name)

        self.assertEqual(cfg.command, self.config_data["command"])
        self.assertEqual(cfg.processes, self.config_data["processes"])
        self.assertEqual(cfg.start_at_launch, True)
        self.assertEqual(cfg.restart_policy, "always")
        self.assertEqual(cfg.expected_exit_codes, [0, 2])
        self.assertEqual(cfg.success_timeout, 15)
        self.assertEqual(cfg.max_restarts, 5)
        self.assertEqual(cfg.stop_signal, "SIGTERM")
        self.assertEqual(cfg.stop_timeout, 20)
        self.assertEqual(cfg.stdout, "/tmp/out.log")
        self.assertEqual(cfg.stderr, "/tmp/err.log")
        self.assertFalse(cfg.discard_output)
        self.assertEqual(cfg.env, {"APP_ENV": "production", "DB_PORT": "5432"})
        self.assertEqual(cfg.working_dir, "/opt/myprogram")
        self.assertEqual(cfg.umask, "027")

    def test_missing_file(self):
        with self.assertRaises(FileNotFoundError):
            ProgramConfig("/non/existent/path.yaml")

    def test_defaults(self):
        # Empty YAML should load defaults
        empty_file = tempfile.NamedTemporaryFile(delete=False, suffix=".yaml")
        yaml.dump({"command": "/usr/bin/myprogram"}, open(empty_file.name, "w"))
        cfg = ProgramConfig(empty_file.name)
        self.assertEqual(cfg.processes, 1)
        self.assertFalse(cfg.start_at_launch)
        self.assertEqual(cfg.restart_policy, "on_failure")
        self.assertEqual(cfg.expected_exit_codes, [0])
        self.assertEqual(cfg.success_timeout, 5)
        self.assertEqual(cfg.max_restarts, 3)
        self.assertEqual(cfg.stop_signal, "SIGTERM")
        self.assertEqual(cfg.stop_timeout, 10)
        self.assertIsNone(cfg.stdout)
        self.assertIsNone(cfg.stderr)
        self.assertFalse(cfg.discard_output)
        self.assertEqual(cfg.env, {})
        self.assertEqual(cfg.working_dir, str(Path.cwd()))
        self.assertEqual(cfg.umask, "022")
        os.unlink(empty_file.name)

    def test_discard_output_conflict(self):
        conflict_cfg = tempfile.NamedTemporaryFile(delete=False, suffix=".yaml")
        conflict_data = {
            "command": "/usr/bin/myprogram",
            "discard_output": True,
            "stdout": "/tmp/out.log",
        }
        yaml.dump(conflict_data, open(conflict_cfg.name, "w"))
        with self.assertRaises(ValueError) as cm:
            ProgramConfig(conflict_cfg.name)
        self.assertIn(
            "Cannot discard output if stdout or stderr are set",
            str(cm.exception),
        )
        os.unlink(conflict_cfg.name)

    def test_missing_command_raises(self):
        # Empty YAML should raise ValueError for missing 'command'
        empty_file = tempfile.NamedTemporaryFile(delete=False, suffix=".yaml")
        yaml.dump({}, open(empty_file.name, "w"))

        with self.assertRaises(ValueError) as cm:
            ProgramConfig(empty_file.name)
        self.assertIn("Missing required config key", str(cm.exception))

        os.unlink(empty_file.name)


if __name__ == "__main__":
    unittest.main()
