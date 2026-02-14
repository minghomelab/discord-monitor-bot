"""
youtube.py
Fetch latest video using YouTube RSS (no API quota).
"""

import requests
import re
import logging

HEADERS = {"User-Agent": "Mozilla/5.0"}

logger = logging.getLogger("discord_monitor.youtube")


def get_latest_video(channel_id):
    """
    Fetch latest video ID, title, and thumbnail from YouTube RSS feed.
    Returns (video_id, title, thumbnail_url) or (None, None, None)
    """

    rss_url = f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"

    try:
        response = requests.get(rss_url, headers=HEADERS, timeout=10)
        response.raise_for_status()
    except Exception as e:
        logger.exception(f"RSS request failed: {e}")
        return None, None, None

    # Extract first <entry> block (latest video)
    entry = re.search(r"<entry>(.*?)</entry>", response.text, re.DOTALL)
    if not entry:
        logger.warning("No <entry> found in RSS feed")
        return None, None, None

    entry_text = entry.group(1)

    # Extract video ID and title
    video_id_match = re.search(r"<yt:videoId>(.*?)</yt:videoId>", entry_text)
    title_match = re.search(r"<title>([^<]+)</title>", entry_text)

    if not video_id_match or not title_match:
        logger.warning("Could not parse video ID or title from RSS")
        return None, None, None

    video_id = video_id_match.group(1)
    title = title_match.group(1)

    # YouTube thumbnail (maxres may fail → Discord will fallback automatically)
    thumbnail_url = f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg"

    logger.debug(f"Latest video fetched: {video_id} | {title}")

    return video_id, title, thumbnail_url
