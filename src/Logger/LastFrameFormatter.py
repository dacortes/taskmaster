import logging
import traceback


class LastFrameFormatter(logging.Formatter):
    def format(self, record):
        # If an exception is being logged, replace with last traceback frame info
        if record.exc_info:
            tb = record.exc_info[2]
            last_frame = traceback.extract_tb(tb)[-1]
            record.filename = last_frame.filename.split("/")[-1]
            record.funcName = last_frame.name
            record.lineno = last_frame.lineno
            # Clear exc_info to prevent default traceback printing
            record.exc_info = None
        return super().format(record)
