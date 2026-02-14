"""
discord.py
Handles sending messages to Discord using webhooks.
"""

import requests
import logging
from datetime import datetime

logger = logging.getLogger("discord_monitor.discord")


def send_discord_notification(title, channel_name, video_id, webhook_url, thumbnail_url=None):
    """
    Send a Discord embed notification to a specific webhook.
    Reusable for YouTube, Reddit, Websites, etc.
    """

    if not webhook_url:
        logger.error("Webhook URL not provided")
        return

    video_url = f"https://youtu.be/{video_id}"

    # Fallback thumbnail if missing
    if not thumbnail_url:
        thumbnail_url = f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg"

    embed = {
        "title": title,
        "url": video_url,
        "description": f"📺 New video from **{channel_name}**",
        "color": 0xFF0000,
        "timestamp": datetime.utcnow().isoformat(),
        "image": {"url": thumbnail_url},
        "footer": {"text": "Discord Monitor Bot"}
    }

    payload = {"embeds": [embed]}

    try:
        response = requests.post(webhook_url, json=payload, timeout=10)

        if response.status_code == 204:
            logger.info(f"Discord notification sent for {channel_name}")
        elif response.status_code == 429:
            logger.warning("Discord rate limited (429). Consider increasing interval.")
        else:
            logger.error(f"Discord error {response.status_code}: {response.text}")

    except Exception as e:
        logger.exception(f"Discord webhook request failed: {e}")
