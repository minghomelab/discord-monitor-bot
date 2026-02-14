"""
manage.py

CLI tool to manage monitored channels in SQLite + auto .env webhook storage
"""

from db import init_db, add_channel, get_channels, remove_channel, update_channel
import os

# Ensure DB exists
def ensure_db():
    from db import init_db
    init_db()

# Base project directory & .env file path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV_FILE = os.path.join(BASE_DIR, ".env")


# ================= ENV FILE UTILS =================

def save_webhook_to_env(key, url):
    """Safely add or update a webhook key in .env without destroying formatting"""

    os.makedirs(os.path.dirname(ENV_FILE), exist_ok=True)
    lines = []
    found = False

    if os.path.exists(ENV_FILE):
        with open(ENV_FILE, "r") as f:
            lines = f.readlines()

    new_lines = []
    for line in lines:
        if line.strip().startswith(f"{key}="):
            new_lines.append(f"{key}={url}\n")
            found = True
        else:
            new_lines.append(line)

    if not found:
        new_lines.append(f"\n{key}={url}\n")

    with open(ENV_FILE, "w") as f:
        f.writelines(new_lines)

    print(f"✅ Saved {key} to .env")


# ================= CLI COMMANDS =================

def add():
    """Add a new YouTube channel + webhook"""

    print("\n=== Add YouTube Channel ===")
    name = input("Channel Name: ").strip()
    url = input("Channel URL (with @handle): ").strip()
    webhook_env = input("Webhook ENV key (e.g. YOUTUBE_LTT_WEBHOOK): ").strip()
    webhook_url = input("Discord Webhook URL: ").strip()

    # Validate inputs
    if not name or not url or not webhook_env or not webhook_url:
        print("[ERROR] All fields are required.")
        return

    # Save to DB
    add_channel(name, url, webhook_env)

    # Save webhook to .env
    save_webhook_to_env(webhook_env, webhook_url)

    print(f"\n🎉 Channel '{name}' added and webhook saved!")


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

    remove_channel(name)
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

    # Handle .env update
    # 1️⃣ If webhook key changed, use new key + new URL
    # 2️⃣ If only URL changed, update old key
    if new_webhook and new_webhook_url:
        save_webhook_to_env(new_webhook, new_webhook_url)
    elif new_webhook_url and not new_webhook:
        # Update the current webhook key's URL
        # Fetch current channel info
        channels = get_channels()
        for c in channels:
            if c["name"] == (new_name if new_name else name):
                save_webhook_to_env(c["webhook_env"], new_webhook_url)
                break

    print(f"✏ Updated {name}")


def main():
    """CLI entry point"""
    ensure_db()
    print("\nDiscord Monitor Channel Manager")
    print("Commands: add | list | remove | edit")

    cmd = input("> ").strip().lower()

    if cmd == "add":
        add()
    elif cmd == "list":
        list_channels()
    elif cmd == "remove":
        remove()
    elif cmd == "edit":
        edit()
    else:
        print("❌ Unknown command")


if __name__ == "__main__":
    main()
