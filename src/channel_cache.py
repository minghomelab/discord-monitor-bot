"""
channel_cache.py
Handles resolving and caching YouTube channel IDs.
"""

import json
import os
import requests
import logging
from dotenv import load_dotenv
from threading import Lock

# Load .env variables
load_dotenv()

API_KEY = os.getenv("YOUTUBE_API_KEY")

# Base directory (project root)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE_FILE = os.path.join(BASE_DIR, "data/channel_cache.json")

HEADERS = {"User-Agent": "Mozilla/5.0"}

# Thread-safe lock (future-proofing for async/multi-monitor)
_cache_lock = Lock()

# Logger
logger = logging.getLogger("discord_monitor.channel_cache")


def load_cache():
    """Load cached channel IDs safely."""
    if not os.path.exists(CACHE_FILE):
        return {}

    try:
        with open(CACHE_FILE, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        logger.warning("channel_cache.json is corrupted. Resetting cache.")
        return {}


def save_cache(cache):
    """Save channel ID cache safely with atomic write."""
    os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)

    temp_file = CACHE_FILE + ".tmp"
    with open(temp_file, "w") as f:
        json.dump(cache, f, indent=4)

    # Atomic replace (prevents corruption)
    os.replace(temp_file, CACHE_FILE)


def resolve_channel_id(url):
    """
    Resolve channel ID using YouTube API once, then cache it forever.
    Supports @handle URLs and direct channel IDs.
    """

    with _cache_lock:
        cache = load_cache()

        # Return cached value instantly
        if url in cache:
            logger.debug(f"Using cached channel ID for {url}")
            return cache[url]

        # If user pasted a channel ID directly
        if "/channel/" in url:
            channel_id = url.split("/channel/")[-1]
            cache[url] = channel_id
            save_cache(cache)
            logger.info(f"Cached direct channel ID for {url}")
            return channel_id

        # Extract handle safely
        if "@" in url:
            handle = url.split("@")[-1]
        else:
            logger.error(f"Invalid YouTube URL: {url}")
            return None

        if not API_KEY:
            logger.error("YOUTUBE_API_KEY missing in .env")
            return None

        logger.info(f"Resolving channel ID via API for handle: {handle}")

        # 1️⃣ Try handle lookup
        api_url = (
            f"https://www.googleapis.com/youtube/v3/channels"
            f"?part=id&forHandle={handle}&key={API_KEY}"
        )

        try:
            response = requests.get(api_url, headers=HEADERS, timeout=10).json()
        except Exception as e:
            logger.exception(f"YouTube API request failed: {e}")
            return None

        channel_id = None

        if response.get("items"):
            channel_id = response["items"][0]["id"]

        # 2️⃣ Fallback search if handle fails
        if not channel_id:
            logger.warning(f"Handle lookup failed, searching channel name: {handle}")

            search_url = (
                f"https://www.googleapis.com/youtube/v3/search"
                f"?part=snippet&type=channel&q={handle}&maxResults=1&key={API_KEY}"
            )

            try:
                search = requests.get(search_url, headers=HEADERS, timeout=10).json()
            except Exception as e:
                logger.exception(f"YouTube search failed: {e}")
                return None

            if search.get("items"):
                channel_id = search["items"][0]["snippet"]["channelId"]

        # If still failed
        if not channel_id:
            logger.error(f"Could not resolve channel ID for {url}")
            return None

        # Cache result
        cache[url] = channel_id
        save_cache(cache)

        logger.info(f"Cached YouTube handle {handle} → {channel_id}")
        return channel_id
