"""
main.py

Main scheduler for the Discord Monitor Bot.
This file ONLY controls timing and calls monitor modules.
Supports multiple monitoring modules in a clean, scalable way.
"""

import time
import os
from dotenv import load_dotenv
from db import init_db
init_db()


# ================= IMPORT MONITOR MODULES =================
# Each module must implement a `check_*()` function
from monitor_youtube import check_youtube
# from monitor_reddit import check_reddit
# from monitor_websites import check_websites

# ================= LOAD ENV VARIABLES =================
load_dotenv()

# Check interval in seconds (default 5 minutes)
CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", 300))

# List of active monitor modules
MONITOR_MODULES = [
    check_youtube,
    # check_reddit,
    # check_websites
]


def run_cycle():
    """
    Run a single monitoring cycle.
    Calls each module in MONITOR_MODULES sequentially.
    """
    start_time = time.strftime("%Y-%m-%d %H:%M:%S")
    print(f"\n===== Cycle started at {start_time} =====")

    for module_func in MONITOR_MODULES:
        try:
            # Call the module's check function
            module_func()
        except Exception as e:
            # Ensure one module crashing does not stop the others
            print(f"[ERROR] Module {module_func.__name__} failed: {e}")

    print(f"\n===== Cycle finished at {time.strftime('%Y-%m-%d %H:%M:%S')} =====")


def main():
    """
    Main infinite scheduler loop.
    Calls each monitoring module on a timer.
    """
    print("======================================")
    print(" Discord Monitor Bot V0.3 (Modular) ")
    print("======================================")
    print(f"Check interval: {CHECK_INTERVAL} seconds\n")

    while True:
        run_cycle()
        print(f"\nSleeping for {CHECK_INTERVAL} seconds...\n")
        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    main()
