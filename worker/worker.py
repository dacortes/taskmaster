import os
import random
import signal
import sys
import time

running = True


def handle_sigterm(signum, frame):
    global running
    print(f"[PID={os.getpid()}] Received SIGTERM, shutting down gracefully...")
    running = False


if __name__ == "__main__":
    signal.signal(signal.SIGTERM, handle_sigterm)

    print(f"Worker starting with PID={os.getpid()}")
    print(f"Environment: {os.environ.get('APP_ENV')} / {os.environ.get('DB_HOST')}")

    runtime = random.randint(5, 15)
    i = 0
    while running and i < runtime:
        print(f"[PID={os.getpid()}] Running... {i+1}/{runtime}")
        time.sleep(1)
        i += 1

    # If stopped gracefully, exit code 0
    if not running:
        print(f"[PID={os.getpid()}] Stopped by SIGTERM")
        sys.exit(0)

    # Otherwise, simulate exit code (to test restart policies)
    exit_code = random.choice([0, 1, 2])
    print(f"[PID={os.getpid()}] Exiting with code {exit_code}")
    sys.exit(exit_code)
