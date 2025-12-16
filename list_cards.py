#!/usr/bin/env python3
"""
List all lessons and their cards.

Usage:
    python list_cards.py
"""

import json
import re
from pathlib import Path


def main():
    script_dir = Path(__file__).parent
    content_dir = script_dir / "content"

    # Load config for uid_prefix
    config_path = content_dir / "config.json"
    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)
    uid_prefix = config["uid_prefix"]

    # Find and sort lesson files
    lesson_files = sorted(content_dir.glob("lesson_*.json"))

    for lesson_path in lesson_files:
        with open(lesson_path, "r", encoding="utf-8") as f:
            lesson_data = json.load(f)

        lesson_title = lesson_data.get("title", lesson_path.stem)
        print(f"# {lesson_title}")

        for card in lesson_data.get("cards", []):
            uid = card.get("uid", "")
            front = card.get("front", "")

            # Extract short id (just the card number part, e.g., "071" from "...-12-071")
            match = re.search(r"-(\d+)$", uid)
            short_id = match.group(1) if match else uid

            # Truncate front if too long
            front_display = front[:80] + "..." if len(front) > 80 else front

            print(f"- {short_id}: {front_display}")

        print()


if __name__ == "__main__":
    main()
