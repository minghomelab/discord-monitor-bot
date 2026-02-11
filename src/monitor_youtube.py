"""
monitor_youtube.py

This module handles ALL YouTube monitoring logic.
main.py should NEVER directly talk to YouTube again.
This makes the system modular and scalable.
"""

import time
import os

from storage import get_youtube_channels, get_last_seen, update_last_seen
from youtube import get_latest_video
from discord import send_discord_notification
from channel_cache import resolve_channel_id


def check_youtube():
    """
    Check all configured YouTube channels for new uploads.
    This function is called by main.py on a schedule.
    """

    print("\n[YouTube] Starting YouTube check cycle...")

    # Load channels and last seen cache
    channels = get_youtube_channels()
    last_seen = get_last_seen()["youtube"]

    # Loop through each configured channel
    for channel in channels:
        name = channel["name"]
        url = channel["url"]
        webhook_env = channel["webhook_env"]

        print(f"\n[YouTube] Checking channel: {name}")

        # Get webhook URL from .env
        webhook_url = os.getenv(webhook_env)
        if not webhook_url:
            print(f"[ERROR] Missing webhook in .env: {webhook_env}")
            continue

        try:
            # Resolve channel ID (cached or API)
            channel_id = resolve_channel_id(url)
            if not channel_id:
                print(f"[YouTube] Skipping {name} (no channel ID)")
                continue

            # Get latest video via RSS (no API quota)
            video_id, title = get_latest_video(channel_id)
            if not video_id:
                print(f"[YouTube] Could not fetch latest video for {name}")
                continue

            # Check last seen video ID
            previous_video = last_seen.get(url)

            # If new video detected
            if previous_video != video_id:
                print(f"🔥 NEW VIDEO DETECTED: {title}")

                # Send Discord notification
                send_discord_notification(title, name, video_id, webhook_url)

                # Update last seen cache
                update_last_seen(url, video_id, platform="youtube")
            else:
                print("[YouTube] No new video.")

        except Exception as e:
            # Prevent one channel crash from stopping everything
            print(f"[YouTube ERROR] {name} failed: {e}")

    print("\n[YouTube] YouTube check cycle finished.")
