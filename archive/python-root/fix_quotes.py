import re
from pathlib import Path

def fix_file(filepath):
    text = filepath.read_text(encoding='utf-8')
    # Fix smart quotes
    text = text.replace('\u2018', "'").replace('\u2019', "'")
    text = text.replace('\u201c', '"').replace('\u201d', '"')
    filepath.write_text(text, encoding='utf-8')
    print(f"Fixed: {filepath}")

for f in Path('pygame').rglob('*.py'):
    fix_file(f)
print("\nDone!")
