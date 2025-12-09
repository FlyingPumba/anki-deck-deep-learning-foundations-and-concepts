# Deep Learning Anki Deck

An Anki deck based on "Deep Learning: Foundations and Concepts" by Christopher Bishop and Hugh Bishop.

## Prerequisites

1. [Anki](https://apps.ankiweb.net/) installed
2. [AnkiConnect](https://ankiweb.net/shared/info/2055492159) add-on installed (code: 2055492159)
3. Python 3.13+ with [uv](https://github.com/astral-sh/uv)

## Setup

```bash
# Clone the repository
git clone <repo-url>
cd anki-deck-deep-learning-foundations-and-concepts

# Install dependencies
uv sync
```

## Usage

1. Open Anki (AnkiConnect runs on port 8765)
2. Run the sync script:

```bash
uv run python sync_anki.py
```

The script will:
- Create the "Deep Learning" deck with subdecks for each lesson
- Add new cards
- Update modified cards
- Remove cards that no longer exist in the JSON files

## File Structure

```
anki-deck-deep-learning-foundations-and-concepts/
├── sync_anki.py          # Sync script
├── content/
│   ├── config.json       # Deck configuration
│   ├── lesson_01.json    # Lesson 1 cards
│   ├── lesson_02.json
│   └── ...
├── pyproject.toml
└── README.md
```

## Editing Cards

Each lesson file follows this structure:

```json
{
  "id": "01",
  "title": "Lesson 01: Introduction",
  "lesson_title": "Introduction to Deep Learning",
  "objectives": ["..."],
  "cards": [
    {
      "uid": "01-001",
      "front": "Question text with \\( LaTeX \\)",
      "back": "Answer text",
      "tags": ["ch01", "introduction", "definition"]
    }
  ]
}
```

After editing, run `uv run python sync_anki.py` to update Anki.

## Card Tracking

Cards are tracked by UID tags (e.g., `uid:01-001`). This allows the sync script to:
- Identify existing cards for updates
- Detect orphaned cards for removal
- Preserve your Anki review progress
