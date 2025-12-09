# Project Instructions

## Package Management
- Use `uv` for Python dependency management (not pip)
- Run scripts with `uv run python <script>`

## Card Content Formatting

### LaTeX
- Use LaTeX for all mathematical equations
- Inline math: `\( ... \)`
- Matrices: `\begin{bmatrix} ... \end{bmatrix}`
- Vectors: `\vec{v}`, `\hat{i}`
- Greek letters: `\lambda`, `\theta`, etc.

### Lists
- Add an extra newline before lists so they display correctly in Anki
- Use `\n\n-` instead of `\n-` before list items

### Example
```json
{
  "back": "The determinant tells you:\n\n- How much areas/volumes scale\n- Whether orientation flips (negative)\n\nFormula: \\( \\det(A) = ad - bc \\)"
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
