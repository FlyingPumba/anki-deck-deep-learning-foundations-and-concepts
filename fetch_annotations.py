#!/usr/bin/env python3
"""
Fetch annotations from a book in local Zotero SQLite database.

The Zotero local HTTP API doesn't expose annotations, so we read directly
from the SQLite database.

Usage:
    uv run python fetch_annotations.py

Outputs annotations to content/annotations.json
"""

import json
import sqlite3
from pathlib import Path

ZOTERO_DB = Path.home() / "Zotero" / "zotero.sqlite"
BOOK_KEY = "6LKJEGD4"  # Deep Learning: Foundations and Concepts
OUTPUT_FILE = Path(__file__).parent / "content" / "annotations.json"

# Annotation type mapping (from Zotero source)
ANNOTATION_TYPES = {
    1: "highlight",
    2: "note",
    3: "image",
    4: "ink",
    5: "underline",
    6: "text",
}


def get_book_info(conn, book_key: str) -> dict | None:
    """Get book metadata by item key."""
    cursor = conn.execute(
        """
        SELECT i.itemID, idv.value as title
        FROM items i
        JOIN itemData id ON i.itemID = id.itemID
        JOIN itemDataValues idv ON id.valueID = idv.valueID
        JOIN fields f ON id.fieldID = f.fieldID
        WHERE i.key = ? AND f.fieldName = 'title'
        """,
        (book_key,),
    )
    row = cursor.fetchone()
    if not row:
        return None
    return {"itemID": row[0], "title": row[1]}


def get_annotations(conn, book_key: str) -> list[dict]:
    """Get all annotations for a book's PDF attachment."""
    cursor = conn.execute(
        """
        SELECT
            ia.text,
            ia.comment,
            ia.pageLabel,
            ia.color,
            ia.sortIndex,
            ia.type
        FROM itemAnnotations ia
        JOIN items i ON ia.parentItemID = i.itemID
        JOIN itemAttachments att ON i.itemID = att.itemID
        WHERE att.parentItemID = (
            SELECT itemID FROM items WHERE key = ?
        )
        ORDER BY ia.sortIndex
        """,
        (book_key,),
    )

    annotations = []
    for row in cursor:
        annotations.append({
            "text": row[0],
            "comment": row[1],
            "pageLabel": row[2],
            "color": row[3],
            "sortIndex": row[4],
            "type": ANNOTATION_TYPES.get(row[5], "unknown"),
        })

    return annotations


def main():
    if not ZOTERO_DB.exists():
        print(f"Zotero database not found: {ZOTERO_DB}")
        return

    # Connect in read-only mode
    conn = sqlite3.connect(f"file:{ZOTERO_DB}?mode=ro", uri=True)

    try:
        book = get_book_info(conn, BOOK_KEY)
        if not book:
            print(f"Book not found with key: {BOOK_KEY}")
            return

        print(f"Found: {book['title']}")

        annotations = get_annotations(conn, BOOK_KEY)
        print(f"Found {len(annotations)} annotations")

        # Write output
        output = {
            "book": {
                "title": book["title"],
                "key": BOOK_KEY,
            },
            "annotations": annotations,
        }

        OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(output, f, indent=2, ensure_ascii=False)

        print(f"Wrote annotations to: {OUTPUT_FILE}")

    finally:
        conn.close()


if __name__ == "__main__":
    main()
