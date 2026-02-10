"""
youtube.py
Fetch latest video using YouTube RSS (no API quota).
"""

import requests
import re

HEADERS = {"User-Agent": "Mozilla/5.0"}


def get_latest_video(channel_id):
    """
    Fetch latest video ID + title from YouTube RSS feed.
    Returns (video_id, title) or (None, None)
    """

    rss_url = f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"

    try:
        response = requests.get(rss_url, headers=HEADERS, timeout=10)
        response.raise_for_status()
    except Exception as e:
        print(f"[YouTube] RSS error: {e}")
        return None, None

    # Extract first <entry> block (latest video)
    entry = re.search(r"<entry>(.*?)</entry>", response.text, re.DOTALL)
    if not entry:
        return None, None

    entry_text = entry.group(1)

    # Extract video ID and title
    video_id_match = re.search(r"<yt:videoId>(.*?)</yt:videoId>", entry_text)
    title_match = re.search(r"<title>([^<]+)</title>", entry_text)

    if not video_id_match or not title_match:
        return None, None

    video_id = video_id_match.group(1)
    title = title_match.group(1)

    return video_id, title
