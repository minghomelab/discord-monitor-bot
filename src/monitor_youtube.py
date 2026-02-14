"""
monitor_youtube.py

Handles YouTube monitoring logic.
Called by main.py on a schedule.
"""

import os
import logging
from dotenv import load_dotenv

from db import get_channels, get_last_seen, update_last_seen, get_last_seen_for_channel
from youtube import get_latest_video
from channel_cache import resolve_channel_id
from discord import send_discord_notification

# Logger (will be configured globally later)
logger = logging.getLogger("discord_monitor.youtube")


def check_youtube():
    """Check all configured YouTube channels for new uploads."""
    load_dotenv(override=True)

    logger.info("Starting YouTube check cycle")

    # Load channels from SQLite
    channels = get_channels()
    if not channels:
        logger.info("No YouTube channels configured")
        return

    # Load last seen cache once
    last_seen_data = get_last_seen()
    youtube_last_seen = last_seen_data.get("youtube", {})

    # Loop channels
    for channel in channels:
        name = channel["name"]
        url = channel["url"]
        webhook_env = channel["webhook_env"]

        logger.info(f"Checking YouTube channel: {name}")

        # Load webhook
        webhook_url = os.getenv(webhook_env)
        if not webhook_url:
            logger.error(f"Missing webhook ENV: {webhook_env}")
            continue

        try:
            # Resolve channel ID (cached)
            channel_id = resolve_channel_id(url)
            if not channel_id:
                logger.warning(f"Could not resolve channel ID for {name}")
                continue

            # Fetch latest video
            video_id, title, thumbnail = get_latest_video(channel_id)
            if not video_id:
                logger.warning(f"No video found for {name}")
                continue

            # Get last seen video
            previous_video = youtube_last_seen.get(url)
            is_first_run = previous_video is None

            # First-run bootstrap (NO DISCORD NOTIFICATION)
            if is_first_run:
                logger.info(f"First run detected for {name}. Caching latest video only.")
                update_last_seen(url, video_id, platform="youtube")
                continue

            # No new video
            if previous_video == video_id:
                logger.debug(f"No new video for {name}")
                continue

            # NEW VIDEO DETECTED
            logger.info(f"NEW VIDEO detected for {name}: {title}")

            send_discord_notification(
                title=title,
                channel_name=name,
                video_id=video_id,
                webhook_url=webhook_url,
                thumbnail=thumbnail
            )

            # Update last seen
            update_last_seen(url, video_id, platform="youtube")

        except Exception as e:
            logger.exception(f"YouTube error for {name}: {e}")

    logger.info("YouTube check cycle finished")
