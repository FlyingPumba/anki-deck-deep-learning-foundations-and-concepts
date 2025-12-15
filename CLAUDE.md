# Project Instructions

## Package Management
- Use `uv` for Python dependency management (not pip)
- Run scripts with `uv run python <script>`

## Card Content Formatting

### Style
- Lead with **intuition** using everyday analogies (coin flips, dice, paint mixing, hills, shadows, etc.)
- Include concrete **examples** where helpful
- Preserve key **formulas** for reference, but don't make them the focus
- Add practical notes like **Why useful** or **Trade-offs** where relevant
- Avoid dry, formula-first definitions - make concepts memorable and relatable

### LaTeX
- Use LaTeX for all mathematical equations
- Inline math: `\( ... \)`
- Matrices: `\begin{bmatrix} ... \end{bmatrix}`
- Vectors: `\vec{v}`, `\hat{i}`
- Greek letters: `\lambda`, `\theta`, etc.

### Text Formatting
- Use HTML tags for formatting (not Markdown)
- Bold: `<b>text</b>` (not `**text**`)
- Italics: `<i>text</i>` (not `*text*`)
- Line breaks: `<br>` (not `\n`)
- Unordered lists: `<ul><li>item</li></ul>`
- Ordered lists: `<ol><li>item</li></ol>`

### Example
```json
{
  "back": "The determinant tells you:<br><ul><li>How much areas/volumes scale</li><li>Whether orientation flips (negative)</li></ul>Formula: \\( \\det(A) = ad - bc \\)"
}
```

## File Structure

### Lesson Files
- One JSON file per lesson: `content/lesson_XX.json`
- Title format: `"Lesson XX: {title}"` (for proper Anki sorting)

### Card UIDs
- Format: `XX-YYY` where XX is lesson number, YYY is card number
- Example: `01-001`, `14-005`

### Tags
- Always include chapter tag: `chXX`
- Add 1-2 topic tags: `neural-networks`, `backpropagation`, `cnn`, etc.

### Images
- Store images in `content/images/`
- Naming convention: `{full_card_uid}_{sequence}.{ext}`
  - Example: `deep-learning-foundations-and-concepts-12-071_01.png`
  - Multiple images for same card: `..._01.png`, `..._02.png`, etc.
- Supported formats: png, jpg, jpeg, gif, webp, svg
- Reference in card JSON using HTML img tags:
  ```json
  {
    "back": "See diagram:<br><img src=\"deep-learning-foundations-and-concepts-12-071_01.png\">"
  }
  ```
- Images are automatically:
  - Uploaded to Anki when syncing
  - Deleted from Anki when the corresponding card is removed or when the image file is deleted from `content/images/`

## Content Source
- Based on "Deep Learning: Foundations and Concepts" by Christopher Bishop and Hugh Bishop
- Book text available in `book.txt`
- Annotations fetched from Zotero are in `content/annotations.json` (gitignored)

## Workflow for Creating Lessons

### Prerequisites
- Fetch annotations: `uv run python fetch_annotations.py` (requires Zotero running)
- Annotations are stored in `content/annotations.json`

### Creating a New Lesson
1. Check which chapters have annotations in `content/annotations.json`
2. **Skip chapters with no annotations**
3. For each chapter with annotations:
   - Read the chapter content from `book.txt`
   - Read the annotations for that chapter's page range
   - Create cards based on both book content and annotations
   - Write to `content/lesson_XX.json`
4. Sync to Anki: `uv run python sync_anki.py`

### Working Iteratively
- Create one lesson at a time
- Get user approval before proceeding to the next chapter
- Cards should cover key concepts from both the book and user's annotations
