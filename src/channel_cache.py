"""
channel_cache.py
Handles resolving and caching YouTube channel IDs.
"""

import json
import os
import requests
from dotenv import load_dotenv

# Load .env variables
load_dotenv()

API_KEY = os.getenv("YOUTUBE_API_KEY")

# Base directory (project root)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE_FILE = os.path.join(BASE_DIR, "data/cache_channel_ids.json")

HEADERS = {"User-Agent": "Mozilla/5.0"}


def load_cache():
    """Load cached channel IDs from file safely."""
    if not os.path.exists(CACHE_FILE):
        return {}

    try:
        with open(CACHE_FILE, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        print("[WARNING] channel_cache.json is corrupted. Resetting cache.")
        return {}


def save_cache(cache):
    """Save channel ID cache safely."""
    os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)
    with open(CACHE_FILE, "w") as f:
        json.dump(cache, f, indent=4)


def resolve_channel_id(url):
    """
    Resolve channel ID using YouTube API once, then cache it forever.
    Supports @handle URLs and direct channel IDs.
    """

    cache = load_cache()

    # Return cached value instantly
    if url in cache:
        print(f"[Cache] Using cached channel ID for {url}")
        return cache[url]

    # If user pasted a channel ID directly
    if "/channel/" in url:
        channel_id = url.split("/channel/")[-1]
        cache[url] = channel_id
        save_cache(cache)
        print(f"[Cache] Saved direct channel ID {channel_id}")
        return channel_id

    # Extract handle safely
    if "@" in url:
        handle = url.split("@")[-1]
    else:
        print(f"[ERROR] Invalid YouTube URL: {url}")
        return None

    if not API_KEY:
        print("[ERROR] YOUTUBE_API_KEY missing in .env")
        return None

    print(f"[API] Resolving channel ID for {handle}")

    # 1️⃣ Try handle lookup
    api_url = (
        f"https://www.googleapis.com/youtube/v3/channels"
        f"?part=id&forHandle={handle}&key={API_KEY}"
    )

    try:
        response = requests.get(api_url, headers=HEADERS, timeout=10).json()
    except Exception as e:
        print(f"[API] Request failed: {e}")
        return None

    channel_id = None

    if "items" in response and response["items"]:
        channel_id = response["items"][0]["id"]

    # 2️⃣ Fallback search if handle fails
    if not channel_id:
        print(f"[API] Handle failed, searching channel name: {handle}")

        search_url = (
            f"https://www.googleapis.com/youtube/v3/search"
            f"?part=snippet&type=channel&q={handle}&maxResults=1&key={API_KEY}"
        )

        try:
            search = requests.get(search_url, headers=HEADERS, timeout=10).json()
        except Exception as e:
            print(f"[API] Search failed: {e}")
            return None

        if "items" in search and search["items"]:
            channel_id = search["items"][0]["snippet"]["channelId"]

    # If still failed
    if not channel_id:
        print(f"[ERROR] Could not resolve channel ID for {url}")
        return None

    # Cache result
    cache[url] = channel_id
    save_cache(cache)

    print(f"[API] Cached {handle} → {channel_id}")
    return channel_id
