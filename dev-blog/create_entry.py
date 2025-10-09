# !/usr/bin/env python3
'''
Quick Dev Blog Entry Creator

Creates a new blog entry from template with current date and commit hash.
Usage: python create_entry.py [template_name] [title_slug]
'''

import sys
import subprocess
from datetime import datetime
from pathlib import Path

def get_latest_commit_hash() -> str:
    '''Get the latest git commit hash.'''
    try:
        result = subprocess.run(
            ['git', 'rev-parse', '--short', 'HEAD'],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return 'unknown'

def create_entry(template_name: str, title_slug: str) -> bool:
    '''Create a new blog entry from template.'''
    blog_dir = Path(__file__).parent
    templates_dir = blog_dir / 'templates'
    entries_dir = blog_dir / 'entries'
    
    template_path = templates_dir / f'{template_name}.md'
    if not template_path.exists():
        print(f'ERROR: Template "{template_name}" not found')
        print(f'Available templates:')
        for template in templates_dir.glob('*.md'):
            print(f'  - {template.stem}')
        return False
    
    # Generate filename
    today = datetime.now().strftime('%Y-%m-%d')
    filename = f'{today}-{title_slug}.md'
    output_path = entries_dir / filename
    
    if output_path.exists():
        print(f'ERROR: Entry "{filename}" already exists')
        return False
    
    # Read template
    with open(template_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace placeholders
    commit_hash = get_latest_commit_hash()
    content = content.replace('YYYY-MM-DD', today)
    content = content.replace('git-hash-here', commit_hash)
    
    # Write new entry
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f'SUCCESS: Created "{filename}"')
    print(f'Path: {output_path}')
    print(f'Edit the file to customize title, tags, and content')
    return True

def main():
    '''Main function.'''
    if len(sys.argv) != 3:
        print('Usage: python create_entry.py [template_name] [title_slug]')
        print('')
        print('Examples:')
        print('  python create_entry.py development-session ui-improvements')
        print('  python create_entry.py milestone type-annotations-complete')
        return 1
    
    template_name = sys.argv[1]
    title_slug = sys.argv[2]
    
    success = create_entry(template_name, title_slug)
    return 0 if success else 1

if __name__ == '__main__':
    exit(main())
