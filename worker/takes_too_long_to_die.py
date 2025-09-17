import os
import signal
import time

running = True


def handle_sigterm(signum, frame):
    global running
    print(
        f"[PID={os.getpid()}] Received SIGTERM, but I'm going to take a long time to exit..."
    )
    time.sleep(100)


if __name__ == "__main__":
    signal.signal(signal.SIGTERM, handle_sigterm)

    while True:
        time.sleep(1)
