"""
monitor_youtube.py

Handles YouTube monitoring logic.
Called by main.py on a schedule.
"""

import os
from db import get_channels, get_last_seen, update_last_seen
from youtube import get_latest_video
from discord import send_discord_notification
from channel_cache import resolve_channel_id


def check_youtube():
    from dotenv import load_dotenv
    load_dotenv(override=True)
    """Check all configured YouTube channels for new uploads."""

    print("\n[YouTube] Starting YouTube check cycle...")

    # Load channels from SQLite
    channels = get_channels()
    if not channels:
        print("[YouTube] No channels configured.")
        return

    # Load last seen cache once
    last_seen_data = get_last_seen()
    youtube_last_seen = last_seen_data.get("youtube", {})

    # Loop channels
    for channel in channels:
        name = channel["name"]
        url = channel["url"]
        webhook_env = channel["webhook_env"]

        print(f"\n[YouTube] Checking: {name}")

        # Load webhook
        webhook_url = os.getenv(webhook_env)
        if not webhook_url:
            print(f"[ERROR] Missing webhook ENV: {webhook_env}")
            continue

        try:
            # Resolve channel ID (cached)
            channel_id = resolve_channel_id(url)
            if not channel_id:
                print(f"[YouTube] Could not resolve channel ID for {name}")
                continue

            # Fetch latest video
            video_id, title = get_latest_video(channel_id)
            if not video_id:
                print(f"[YouTube] No video found for {name}")
                continue

            # Compare with last seen
            previous_video = youtube_last_seen.get(url)

            if previous_video == video_id:
                print("[YouTube] No new video.")
                continue

            # NEW VIDEO
            print(f"🔥 NEW VIDEO: {title}")

            send_discord_notification(title, name, video_id, webhook_url)

            update_last_seen(url, video_id, platform="youtube")

        except Exception as e:
            print(f"[YouTube ERROR] {name}: {e}")

    print("\n[YouTube] YouTube check cycle finished.")
