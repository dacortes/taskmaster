import logging
import re
import traceback

ANSI_ESCAPE = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')


class CleanFormatter(logging.Formatter):
    def format(self, record):
        # If logging with an exception, overwrite record with last traceback frame
        if record.exc_info:
            tb = record.exc_info[2]
            last_frame = traceback.extract_tb(tb)[-1]
            record.filename = last_frame.filename.split("/")[-1]
            record.funcName = last_frame.name
            record.lineno = last_frame.lineno
            # Clear exc_info to prevent default traceback printing
            record.exc_info = None
        msg = super().format(record)
        # Strip ANSI codes
        return ANSI_ESCAPE.sub('', msg)
