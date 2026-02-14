"""
manage.py

CLI tool to manage monitored channels in SQLite + auto .env webhook storage
"""

import os
import logging
from db import init_db, add_channel, get_channels, remove_channel, update_channel, update_last_seen
from channel_cache import resolve_channel_id
from youtube import get_latest_video
from logging_config import setup_logging

# ================= INIT =================
init_db()
logger = setup_logging()

# Base project directory & .env file path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV_FILE = os.path.join(BASE_DIR, ".env")


# ================= ENV FILE UTILS =================

def save_webhook_to_env(key, url):
    """Safely add or update a webhook key in .env using atomic write"""

    os.makedirs(os.path.dirname(ENV_FILE), exist_ok=True)

    lines = []
    found = False

    if os.path.exists(ENV_FILE):
        with open(ENV_FILE, "r") as f:
            lines = f.readlines()

    # Prevent duplicate keys
    for line in lines:
        if line.strip().startswith(f"{key}="):
            found = True

    new_lines = []
    for line in lines:
        if line.strip().startswith(f"{key}="):
            new_lines.append(f"{key}={url}\n")
        else:
            new_lines.append(line)

    if not found:
        new_lines.append(f"\n{key}={url}\n")

    temp_file = ENV_FILE + ".tmp"
    with open(temp_file, "w") as f:
        f.writelines(new_lines)

    os.replace(temp_file, ENV_FILE)

    logger.info(f"Saved webhook {key} to .env")
    print(f"✅ Saved {key} to .env")


# ================= CLI COMMANDS =================

def add():
    """Add a new YouTube channel + webhook"""

    print("\n=== Add YouTube Channel ===")
    name = input("Channel Name: ").strip()
    url = input("Channel URL (with @handle): ").strip()
    webhook_env = input("Webhook ENV key (e.g. YOUTUBE_LTT_WEBHOOK): ").strip()
    webhook_url = input("Discord Webhook URL: ").strip()

    if not name or not url or not webhook_env or not webhook_url:
        print("[ERROR] All fields are required.")
        return

    # Prevent duplicate webhook keys
    existing = [c["webhook_env"] for c in get_channels()]
    if webhook_env in existing:
        print(f"[ERROR] Webhook ENV '{webhook_env}' already exists.")
        return

    # Save to DB
    add_channel(name, url, webhook_env)
    save_webhook_to_env(webhook_env, webhook_url)

    print(f"\n🎉 Channel '{name}' added!")


def list_channels():
    """List all configured channels"""
    print("\n=== Configured Channels ===")
    channels = get_channels()

    if not channels:
        print("No channels configured.")
        return

    for c in channels:
        print(f"- {c['name']} | {c['url']} | {c['webhook_env']}")


def remove():
    """Remove a channel"""
    list_channels()
    name = input("\nEnter channel name to remove: ").strip()

    confirm = input(f"⚠ Are you sure you want to delete '{name}'? (yes/no): ").lower()
    if confirm != "yes":
        print("Cancelled.")
        return

    remove_channel(name)
    logger.info(f"Removed channel {name}")
    print(f"🗑 Removed {name}")


def edit():
    """Edit an existing channel"""
    list_channels()
    name = input("\nEnter channel name to edit: ").strip()

    if not name:
        print("[ERROR] Channel name required.")
        return

    new_name = input("New Name (leave blank to keep): ").strip()
    new_url = input("New URL (leave blank to keep): ").strip()
    new_webhook = input("New Webhook ENV key (leave blank to keep): ").strip()
    new_webhook_url = input("New Webhook URL (leave blank to keep): ").strip()

    update_channel(name, new_name, new_url, new_webhook)

    # Update webhook in .env
    channels = get_channels()
    final_name = new_name if new_name else name
    for c in channels:
        if c["name"] == final_name:
            if new_webhook_url:
                save_webhook_to_env(c["webhook_env"], new_webhook_url)
            break

    logger.info(f"Updated channel {name}")
    print(f"✏ Updated {name}")


def bootstrap():
    """
    Pre-cache latest videos for all channels (no Discord spam).
    Run this after adding many channels.
    """
    print("\n=== Bootstrapping Last Seen Cache ===")

    channels = get_channels()
    for c in channels:
        name = c["name"]
        url = c["url"]

        print(f"Bootstrapping {name}...")

        channel_id = resolve_channel_id(url)
        if not channel_id:
            print(f"❌ Failed to resolve {name}")
            continue

        video_id, title, _ = get_latest_video(channel_id)
        if not video_id:
            print(f"❌ No video found for {name}")
            continue

        update_last_seen(url, video_id, platform="youtube")
        print(f"Cached latest video for {name}: {title}")

    print("✅ Bootstrap complete. No notifications were sent.")


# ================= MAIN CLI =================

def main():
    print("\nDiscord Monitor Channel Manager")
    print("Commands: add | list | remove | edit | bootstrap")

    cmd = input("> ").strip().lower()

    if cmd == "add":
        add()
    elif cmd == "list":
        list_channels()
    elif cmd == "remove":
        remove()
    elif cmd == "edit":
        edit()
    elif cmd == "bootstrap":
        bootstrap()
    else:
        print("❌ Unknown command")


if __name__ == "__main__":
    main()
