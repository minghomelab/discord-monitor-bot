"""
main.py

Main scheduler for the Discord Monitor Bot.
This file ONLY controls timing and calls monitor modules.
"""

import time
import os
from dotenv import load_dotenv

# Import monitoring modules
from monitor_youtube import check_youtube

# Load environment variables
load_dotenv()

# Check interval in seconds (default 5 minutes)
CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", 300))


def main():
    """
    Main infinite scheduler loop.
    Calls each monitoring module on a timer.
    """

    print("======================================")
    print(" Discord Monitor Bot V0.2 (Modular) ")
    print("======================================")
    print(f"Check interval: {CHECK_INTERVAL} seconds\n")

    while True:
        start_time = time.strftime("%Y-%m-%d %H:%M:%S")
        print(f"\n===== Cycle started at {start_time} =====")

        # Run YouTube monitor
        check_youtube()

        # Future modules:
        # check_reddit()
        # check_websites()

        print(f"\nSleeping for {CHECK_INTERVAL} seconds...\n")
        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    main()
