import os
import sys

print(f"[PID={os.getpid()}] This worker will always fail, test for restart policies.")
sys.exit(5)
