import logging
import re

ANSI_ESCAPE = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')


class CleanFormatter(logging.Formatter):
    def format(self, record):
        msg = super().format(record)
        # Strip ANSI codes
        return ANSI_ESCAPE.sub('', msg)
