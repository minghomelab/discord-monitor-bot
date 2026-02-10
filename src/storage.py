"""
storage.py
Handles reading and writing JSON files.
"""

import json
import os

# Base path of the project (one folder above src)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# File paths
CHANNELS_FILE = os.path.join(BASE_DIR, "data/youtube_channels.json")
LAST_SEEN_FILE = os.path.join(BASE_DIR, "data/last_seen.json")


def load_json(file_path, default_data):
    """Load JSON safely, fallback to default if broken."""
    if not os.path.exists(file_path):
        return default_data

    try:
        with open(file_path, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        print(f"[WARNING] {file_path} is corrupted. Resetting.")
        return default_data
    except Exception as e:
        print(f"[ERROR] Failed to load {file_path}: {e}")
        return default_data


def save_json(file_path, data):
    """Save Python data to JSON safely."""
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    try:
        with open(file_path, "w") as f:
            json.dump(data, f, indent=4, sort_keys=True)
    except Exception as e:
        print(f"[ERROR] Failed to save {file_path}: {e}")


def get_youtube_channels():
    """Return list of YouTube channels."""
    return load_json(CHANNELS_FILE, [])


def get_last_seen():
    """Return dict of last seen videos."""
    return load_json(LAST_SEEN_FILE, {})


def update_last_seen(channel_url, video_id):
    """Update last seen video ID."""
    data = get_last_seen()
    data[channel_url] = video_id
    save_json(LAST_SEEN_FILE, data)
