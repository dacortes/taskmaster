import sys
import unittest
from contextlib import redirect_stdout
from io import StringIO

from Terminal import Terminal


class TestCommand_dispatch(unittest.TestCase):
    def setUp(self):
        # minimal config to initialize the terminal
        self.config = {
            "file_path": "/tmp/test_config.yaml",
            "programs": {
                "nginx": {
                    "cmd": "/usr/local/bin/nginx -c /etc/nginx/test.conf",
                    "numprocs": 1,
                    "umask": "022",
                    "workingdir": "/tmp",
                    "autostart": True,
                    "autorestart": "unexpected",
                    "exitcodes": [0, 2],
                    "startretries": 3,
                    "starttime": 5,
                    "stopsignal": "TERM",
                    "stoptime": 10,
                    "stdout": "/tmp/nginx.stdout",
                    "stderr": "/tmp/nginx.stderr",
                    "env": {"STARTED_BY": "taskmaster", "ANSWER": "42"},
                }
            },
        }

        self.term = Terminal(self.config)
        self.called = {}

        # Replace handlers with stubs
        for name in self.term.commands.keys():
            self.term.commands[name] = self._make_handler(name)

    def _make_handler(self, name):
        def handler():
            self.called[name] = True

        return handler

    def capture_output(self, func):
        buf = StringIO()
        with redirect_stdout(buf):
            func()
        return buf.getvalue().strip()

    def test_known_command_calls_handler(self):
        self.term.input = "status"
        self.term._parse_input()

        output = self.capture_output(self.term._dispatch)
        self.assertTrue(self.called.get("status"))
        self.assertEqual(output, "")

    def test_unknown_command_prints_message(self):
        self.term.input = "foobar"
        self.term._parse_input()

        output = self.capture_output(self.term._dispatch)
        self.assertIn("Unknown command: foobar", output)

    def test_command_with_arguments(self):
        self.term.input = "start nginx"
        self.term._parse_input()

        self.capture_output(self.term._dispatch)
        self.assertTrue(self.called.get("start"))
        self.assertEqual(self.term.cmd_options, ["nginx"])


if __name__ == "__main__":
    unittest.main()
