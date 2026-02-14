"""
main.py

Main scheduler for the Discord Monitor Bot.
This file ONLY controls timing and calls monitor modules.
"""

import time
import os
import signal
import sys
from dotenv import load_dotenv

from db import init_db
from logging_config import setup_logging

# ================= INIT DATABASE =================
init_db()

# ================= LOGGING =================
logger = setup_logging()

# ================= IMPORT MONITOR MODULES =================
from monitor_youtube import check_youtube
# from monitor_reddit import check_reddit
# from monitor_websites import check_websites

# ================= LOAD ENV VARIABLES =================
load_dotenv()

# Check interval in seconds (default 5 minutes)
CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", 300))

# Active monitor modules
MONITOR_MODULES = [
    check_youtube,
    # check_reddit,
    # check_websites
]

# Shutdown flag
shutdown_requested = False


def signal_handler(sig, frame):
    global shutdown_requested
    logger.info("Shutdown signal received. Exiting gracefully...")
    shutdown_requested = True


# Register signal handlers (Docker + Ctrl+C)
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)


def run_cycle():
    """Run a single monitoring cycle."""
    logger.info("===== Monitoring cycle started =====")

    for module_func in MONITOR_MODULES:
        try:
            logger.info(f"Running module: {module_func.__name__}")
            module_func()
        except Exception as e:
            logger.exception(f"Module {module_func.__name__} failed: {e}")

    logger.info("===== Monitoring cycle finished =====")


def main():
    """Main infinite scheduler loop."""
    logger.info("======================================")
    logger.info(" Discord Monitor Bot V0.4 (Modular) ")
    logger.info("======================================")
    logger.info(f"Check interval: {CHECK_INTERVAL} seconds")

    while not shutdown_requested:
        run_cycle()

        logger.info(f"Sleeping for {CHECK_INTERVAL} seconds...")

        # Sleep in small chunks to allow graceful shutdown
        for _ in range(CHECK_INTERVAL):
            if shutdown_requested:
                break
            time.sleep(1)

    logger.info("Bot stopped cleanly.")
    sys.exit(0)


if __name__ == "__main__":
    main()
