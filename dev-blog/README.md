# P(Doom) Development Blog

This directory contains development blog entries that are automatically processed by the website.

## Structure

- `entries/` - Individual blog entries (YYYY-MM-DD-title.md format)
- `templates/` - Markdown templates for different entry types
- `config.json` - Blog configuration and metadata
- `index.json` - Auto-generated index of all entries

## Entry Format

Each entry should follow this naming convention:
```
YYYY-MM-DD-brief-title-slug.md
```

Example: `2025-09-10-type-annotations-milestone.md`

## Automatic Processing

The website build process will:
1. Scan all .md files in entries/
2. Parse frontmatter metadata
3. Generate index.json with entry listings
4. Include entries in website dev blog section

## ASCII-Only Policy

All content must use ASCII characters only (no Unicode, emojis, or special characters).
This ensures maximum compatibility across all systems and AI models.
