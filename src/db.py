"""
db.py

Handles SQLite database for Discord Monitor Bot.
"""

import sqlite3
import os

# Base directory of project
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "data/discord_monitor.db")


def init_db():
    """Create database and tables if they do not exist."""
    os.makedirs(os.path.join(BASE_DIR, "data"), exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Channels table
    c.execute("""
        CREATE TABLE IF NOT EXISTS channels (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE,
            url TEXT UNIQUE,
            webhook_env TEXT
        )
    """)

    # Last seen table
    c.execute("""
        CREATE TABLE IF NOT EXISTS last_seen (
            platform TEXT,
            channel_url TEXT,
            video_id TEXT,
            PRIMARY KEY (platform, channel_url)
        )
    """)

    conn.commit()
    conn.close()


# ================= CHANNELS =================

def add_channel(name, url, webhook_env):
    """Add a new channel to the database."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    try:
        c.execute(
            "INSERT INTO channels (name, url, webhook_env) VALUES (?, ?, ?)",
            (name, url, webhook_env)
        )
    except sqlite3.IntegrityError:
        print(f"[INFO] Channel '{name}' already exists in the database, skipping.")
    conn.commit()
    conn.close()


def get_channels():
    """Return all channels as a list of dicts."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT name, url, webhook_env FROM channels")
    rows = c.fetchall()
    conn.close()
    return [{"name": r[0], "url": r[1], "webhook_env": r[2]} for r in rows]


def remove_channel(name):
    """Remove a channel by name."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM channels WHERE name = ?", (name,))
    conn.commit()
    conn.close()


def update_channel(name, new_name, new_url, new_webhook):
    """Update a channel's name, URL, or webhook."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    if new_name:
        c.execute("UPDATE channels SET name=? WHERE name=?", (new_name, name))
        name = new_name

    if new_url:
        c.execute("UPDATE channels SET url=? WHERE name=?", (new_url, name))

    if new_webhook:
        c.execute("UPDATE channels SET webhook_env=? WHERE name=?", (new_webhook, name))

    conn.commit()
    conn.close()


# ================= LAST SEEN =================

def get_last_seen(platform=None):
    """
    Return dictionary of last seen video IDs.
    If platform is provided, return only that platform's data.
    Otherwise, return all platforms.
    """
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT platform, channel_url, video_id FROM last_seen")
    rows = c.fetchall()
    conn.close()

    data = {}
    for plat, url, vid in rows:
        data.setdefault(plat, {})[url] = vid

    if platform:
        return data.get(platform, {})  # Return only the requested platform
    return data  # Return all platforms


def update_last_seen(channel_url, video_id, platform="youtube"):
    """Update the last seen video ID for a channel."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("""
        INSERT OR REPLACE INTO last_seen (platform, channel_url, video_id)
        VALUES (?, ?, ?)
    """, (platform, channel_url, video_id))

    conn.commit()
    conn.close()

def get_last_seen_for_channel(channel_url, platform="youtube"):
    """
    Return the last seen video ID for a single channel.
    Returns None if no record exists.
    """

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute(
        "SELECT video_id FROM last_seen WHERE platform=? AND channel_url=?",
        (platform, channel_url)
    )

    row = c.fetchone()
    conn.close()

    return row[0] if row else None

def channel_exists(url):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT 1 FROM channels WHERE url=?", (url,))
    exists = c.fetchone() is not None
    conn.close()
    return exists
