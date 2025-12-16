#!/usr/bin/env python3
"""
Move a card from one lesson to another.

This script:
1. Moves the card from its current lesson JSON to the destination lesson JSON
2. Updates the card UID to follow the convention (new lesson number)
3. Updates Anki: changes the uid tag and moves to the new subdeck

Usage:
    python move_card.py <card_uid> <dest_lesson_number>
    python move_card.py deep-learning-foundations-and-concepts-12-071 08

The card's learning progress in Anki is preserved.
"""

import argparse
import json
import re
import sys
from pathlib import Path

import requests

ANKI_URL = "http://127.0.0.1:8765"
API_VERSION = 6


def invoke(action: str, params: dict | None = None) -> any:
    """Call AnkiConnect API."""
    payload = {"action": action, "version": API_VERSION}
    if params is not None:
        payload["params"] = params

    try:
        r = requests.post(ANKI_URL, json=payload, timeout=30)
        r.raise_for_status()
    except requests.exceptions.ConnectionError:
        raise RuntimeError(
            "Cannot connect to Anki. Make sure Anki is running "
            "and AnkiConnect add-on is installed (code: 2055492159)"
        )

    data = r.json()
    if data.get("error"):
        raise RuntimeError(f"AnkiConnect error: {data['error']}")
    return data.get("result")


def load_config(content_dir: Path) -> dict:
    """Load config.json."""
    config_path = content_dir / "config.json"
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_lesson(content_dir: Path, lesson_num: int) -> tuple[dict, Path]:
    """Load a lesson JSON file. Returns (data, path)."""
    lesson_path = content_dir / f"lesson_{lesson_num:02d}.json"
    if not lesson_path.exists():
        raise FileNotFoundError(f"Lesson file not found: {lesson_path}")
    with open(lesson_path, "r", encoding="utf-8") as f:
        return json.load(f), lesson_path


def save_lesson(path: Path, data: dict) -> None:
    """Save a lesson JSON file."""
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")


def parse_uid(uid: str, uid_prefix: str) -> tuple[int, int]:
    """Parse a UID into (lesson_number, card_number)."""
    pattern = rf"^{re.escape(uid_prefix)}-(\d+)-(\d+)$"
    match = re.match(pattern, uid)
    if not match:
        raise ValueError(f"Invalid UID format: {uid}. Expected: {uid_prefix}-XX-YYY")
    return int(match.group(1)), int(match.group(2))


def make_uid(uid_prefix: str, lesson_num: int, card_num: int) -> str:
    """Create a UID from components."""
    return f"{uid_prefix}-{lesson_num:02d}-{card_num:03d}"


def find_card_in_lessons(content_dir: Path, uid: str) -> tuple[dict, dict, Path, int]:
    """
    Find a card by UID across all lesson files.
    Returns (card, lesson_data, lesson_path, card_index).
    """
    lesson_files = sorted(content_dir.glob("lesson_*.json"))
    for lesson_path in lesson_files:
        with open(lesson_path, "r", encoding="utf-8") as f:
            lesson_data = json.load(f)
        for i, card in enumerate(lesson_data.get("cards", [])):
            if card.get("uid") == uid:
                return card, lesson_data, lesson_path, i
    raise ValueError(f"Card not found: {uid}")


def get_next_card_number(lesson_data: dict, uid_prefix: str, lesson_num: int) -> int:
    """Get the next available card number for a lesson."""
    max_card_num = 0
    pattern = rf"^{re.escape(uid_prefix)}-{lesson_num:02d}-(\d+)$"
    for card in lesson_data.get("cards", []):
        match = re.match(pattern, card.get("uid", ""))
        if match:
            card_num = int(match.group(1))
            max_card_num = max(max_card_num, card_num)
    return max_card_num + 1


def find_note_by_uid(uid_tag: str, parent_deck: str) -> int | None:
    """Find a note by its UID tag."""
    query = f'deck:"{parent_deck}*" tag:"{uid_tag}"'
    note_ids = invoke("findNotes", {"query": query})
    return note_ids[0] if note_ids else None


def update_note_in_anki(
    old_uid: str,
    new_uid: str,
    old_lesson_num: int,
    new_lesson_num: int,
    new_deck: str,
    parent_deck: str,
) -> bool:
    """
    Update a note in Anki: change uid tag, chapter tag, and move to new deck.
    Returns True if successful.
    """
    old_uid_tag = f"uid:{old_uid}"
    new_uid_tag = f"uid:{new_uid}"
    old_ch_tag = f"ch{old_lesson_num:02d}"
    new_ch_tag = f"ch{new_lesson_num:02d}"

    # Find the note
    note_id = find_note_by_uid(old_uid_tag, parent_deck)
    if not note_id:
        print(f"  Warning: Note not found in Anki for {old_uid}")
        return False

    # Get card IDs for this note (to move to new deck)
    card_ids = invoke("findCards", {"query": f"nid:{note_id}"})

    # Update uid tag: remove old, add new
    invoke("removeTags", {"notes": [note_id], "tags": old_uid_tag})
    invoke("addTags", {"notes": [note_id], "tags": new_uid_tag})

    # Update chapter tag: remove old, add new
    invoke("removeTags", {"notes": [note_id], "tags": old_ch_tag})
    invoke("addTags", {"notes": [note_id], "tags": new_ch_tag})

    # Move cards to new deck
    if card_ids:
        invoke("changeDeck", {"cards": card_ids, "deck": new_deck})

    return True


def move_card(
    content_dir: Path,
    card_uid: str,
    dest_lesson_num: int,
    dry_run: bool = False,
) -> None:
    """Move a card from its current lesson to a destination lesson."""
    config = load_config(content_dir)
    uid_prefix = config["uid_prefix"]
    parent_deck = config["deck"]

    # Parse and validate the source UID
    src_lesson_num, src_card_num = parse_uid(card_uid, uid_prefix)

    if src_lesson_num == dest_lesson_num:
        print(f"Card is already in lesson {dest_lesson_num}")
        return

    # Find the card
    card, src_lesson_data, src_lesson_path, card_index = find_card_in_lessons(
        content_dir, card_uid
    )

    # Load destination lesson
    dest_lesson_data, dest_lesson_path = load_lesson(content_dir, dest_lesson_num)

    # Determine new card number and UID
    new_card_num = get_next_card_number(dest_lesson_data, uid_prefix, dest_lesson_num)
    new_uid = make_uid(uid_prefix, dest_lesson_num, new_card_num)

    # Determine new deck name
    dest_lesson_title = dest_lesson_data.get("title", f"Lesson {dest_lesson_num:02d}")
    new_deck = f"{parent_deck}::{dest_lesson_title}"

    old_ch_tag = f"ch{src_lesson_num:02d}"
    new_ch_tag = f"ch{dest_lesson_num:02d}"

    print(f"Moving card:")
    print(f"  From: {card_uid}")
    print(f"  To:   {new_uid}")
    print(f"  Deck: {new_deck}")
    print(f"  Tags: {old_ch_tag} → {new_ch_tag}")
    print(f"  Question: {card['front'][:60]}...")

    if dry_run:
        print("\n[DRY RUN] No changes made.")
        return

    # Update the card's UID
    card["uid"] = new_uid

    # Update chapter tag in the card's tags
    tags = card.get("tags", [])
    if old_ch_tag in tags:
        tags.remove(old_ch_tag)
    if new_ch_tag not in tags:
        tags.insert(0, new_ch_tag)  # Add at beginning (chapter tag comes first)
    card["tags"] = tags

    # Remove from source lesson
    src_lesson_data["cards"].pop(card_index)

    # Add to destination lesson
    dest_lesson_data.setdefault("cards", []).append(card)

    # Save both JSON files
    save_lesson(src_lesson_path, src_lesson_data)
    save_lesson(dest_lesson_path, dest_lesson_data)
    print(f"  Updated JSON files")

    # Update Anki
    if update_note_in_anki(card_uid, new_uid, src_lesson_num, dest_lesson_num, new_deck, parent_deck):
        print(f"  Updated Anki (uid tag, chapter tag, and deck)")
    else:
        print(f"  Warning: Could not update Anki. Run sync to fix.")

    print("\nDone! Card moved successfully.")


def main():
    parser = argparse.ArgumentParser(
        description="Move a card from one lesson to another"
    )
    parser.add_argument("card_uid", help="The UID of the card to move")
    parser.add_argument(
        "dest_lesson",
        type=int,
        help="Destination lesson number (e.g., 8 for lesson_08.json)",
    )
    parser.add_argument(
        "-d", "--dry-run",
        action="store_true",
        help="Show what would be done without making changes",
    )
    args = parser.parse_args()

    script_dir = Path(__file__).parent
    content_dir = script_dir / "content"

    try:
        move_card(content_dir, args.card_uid, args.dest_lesson, args.dry_run)
    except (RuntimeError, ValueError, FileNotFoundError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
