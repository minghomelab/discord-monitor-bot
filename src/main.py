"""
main.py
YouTube Monitor Bot (Docker-ready, Option A caching)
Monitors multiple channels and sends new video notifications to per-channel Discord webhooks.
"""

import os
import time
from dotenv import load_dotenv

from storage import get_youtube_channels, get_last_seen, update_last_seen
from youtube import get_latest_video
from discord import send_discord_notification
from channel_cache import resolve_channel_id

# ---------------------------
# Load environment variables
# ---------------------------
load_dotenv()

# Check interval in seconds (can set via .env, default = 300 seconds)
CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", 300))


def check_channels():
    """
    Check all YouTube channels once for new videos.
    Uses cached channel IDs from channel_cache.json via resolve_channel_id().
    Sends Discord notifications for new videos and updates last_seen.json.
    """
    channels = get_youtube_channels()  # Load user-defined channels from JSON
    last_seen = get_last_seen()        # Load last seen videos from JSON

    for channel in channels:
        name = channel["name"]
        url = channel["url"]
        webhook_env = channel["webhook_env"]

        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        print(f"\n[{timestamp}] Checking: {name}")

        # Fetch webhook URL from environment
        webhook_url = os.getenv(webhook_env)
        if not webhook_url:
            print(f"[ERROR] Missing webhook in .env: {webhook_env}")
            continue

        try:
            # Resolve channel ID (cached if available, API call only if new)
            channel_id = resolve_channel_id(url)
            if not channel_id:
                print(f"[ERROR] Could not resolve channel ID for {url}")
                continue

            # Get latest video via RSS feed
            video_id, title = get_latest_video(channel_id)
            if not video_id:
                print(f"[INFO] Could not fetch latest video for {name}")
                continue

            # Compare with last seen video to detect new uploads
            previous_video = last_seen.get(url)

            if previous_video != video_id:
                # New video detected
                print(f"🔥 NEW VIDEO: {title}")
                send_discord_notification(title, name, video_id, webhook_url)
                update_last_seen(url, video_id)  # Persist last seen video
            else:
                print("No new video.")

        except Exception as e:
            # Prevent a single channel failure from stopping the bot
            print(f"[ERROR] {name} failed: {e}")


def main():
    """
    Main loop: continuously check channels at defined intervals.
    Runs indefinitely in Docker.
    """
    print("=== YouTube Monitor Bot (Continuous Mode) ===")
    print(f"Check interval: {CHECK_INTERVAL} seconds\n")

    while True:
        check_channels()
        print(f"\nSleeping for {CHECK_INTERVAL} seconds...\n")
        time.sleep(CHECK_INTERVAL)  # Wait before next loop


if __name__ == "__main__":
    main()
#this is a test push to github