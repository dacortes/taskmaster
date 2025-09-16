import os
import time

if __name__ == "__main__":
    time.sleep(1)  # Simulate some startup delay
    print(f"Hello from demo process (PID={os.getpid()})")

    # Show environment variables passed from the manager
    print("Environment variables:")
    print(f"  APP_ENV = {os.environ.get('APP_ENV')}")
    print(f"  DB_HOST = {os.environ.get('DB_HOST')}")
    print(f"  DB_PORT = {os.environ.get('DB_PORT')}")

    # Show the current working directory
    print("\nWorking directory check:")
    print(f"  Current working dir = {os.getcwd()}")

    try:
        with open("demo_output.txt", "w") as f:
            f.write("This file was created inside the working directory.\n")
        print("  Wrote demo_output.txt successfully.")
    except Exception as e:
        print(f"  Could not write to working directory: {e}")
