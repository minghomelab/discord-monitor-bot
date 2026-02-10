"""
discord.py
Handles sending messages to Discord using webhooks.
"""

import requests


def send_discord_notification(title, channel_name, video_id, webhook_url):
    """
    Send a Discord embed notification to a specific webhook.
    """

    if not webhook_url:
        print("[ERROR] Webhook URL not provided")
        return

    video_url = f"https://youtu.be/{video_id}"
    thumbnail_url = f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg"

    payload = {
        "embeds": [
            {
                "title": title,
                "url": video_url,
                "description": f"📺 New video from **{channel_name}**",
                "color": 16711680,
                "image": {"url": thumbnail_url}
            }
        ]
    }

    try:
        response = requests.post(webhook_url, json=payload, timeout=10)

        if response.status_code == 204:
            print("[Discord] Sent notification")
        elif response.status_code == 429:
            print("[Discord] Rate limited! Slow down.")
        else:
            print(f"[Discord] Error {response.status_code}: {response.text}")

    except Exception as e:
        print(f"[Discord] Request failed: {e}")
