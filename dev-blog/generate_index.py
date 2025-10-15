# !/usr/bin/env python3
'''
Dev Blog Index Generator

Scans dev-blog/entries/ directory and generates index.json for website integration.
Enforces ASCII-only content policy.
'''

import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

def is_ascii_only(text: str) -> bool:
    '''Check if text contains only ASCII characters.'''
    try:
        text.encode('ascii')
        return True
    except UnicodeEncodeError:
        return False

def extract_frontmatter(content: str) -> tuple[Dict[str, Any], str]:
    '''Extract YAML frontmatter from markdown content.'''
    if not content.startswith('---\n'):
        return {}, content
    
    try:
        end_marker = content.find('\n---\n', 4)
        if end_marker == -1:
            return {}, content
        
        frontmatter_text = content[4:end_marker]
        markdown_content = content[end_marker + 5:]
        
        # Simple YAML parsing for our specific format
        frontmatter = {}
        for line in frontmatter_text.strip().split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip()
                value = value.strip().strip(''\'')
                
                # Handle arrays
                if value.startswith('[') and value.endswith(']'):
                    value = [item.strip().strip(''\'') for item in value[1:-1].split(',')]
                
                frontmatter[key] = value
        
        return frontmatter, markdown_content
    
    except Exception as e:
        print(f'Error parsing frontmatter: {e}')
        return {}, content

def validate_entry(entry_path: Path, content: str) -> List[str]:
    '''Validate a blog entry against content policy.'''
    errors = []
    
    # Check ASCII-only policy
    if not is_ascii_only(content):
        errors.append('Content contains non-ASCII characters')
    
    # Check filename format
    if not re.match(r'^\d{4}-\d{2}-\d{2}-.+\.md$', entry_path.name):
        errors.append('Filename must follow YYYY-MM-DD-title.md format')
    
    # Extract and validate frontmatter
    frontmatter, _ = extract_frontmatter(content)
    
    required_fields = ['title', 'date', 'tags', 'summary']
    for field in required_fields:
        if field not in frontmatter:
            errors.append(f'Missing required frontmatter field: {field}')
    
    # Validate title length
    if 'title' in frontmatter and len(frontmatter['title']) > 60:
        errors.append('Title exceeds 60 character limit')
    
    return errors

def generate_blog_index(blog_dir: Path) -> Dict[str, Any]:
    '''Generate blog index from entries directory.'''
    entries_dir = blog_dir / 'entries'
    config_path = blog_dir / 'config.json'
    
    # Load configuration
    config = {}
    if config_path.exists():
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
    
    entries = []
    errors = []
    
    if not entries_dir.exists():
        return {
            'entries': [],
            'config': config,
            'errors': ['Entries directory does not exist'],
            'generated_at': datetime.now().isoformat()
        }
    
    # Process each markdown file
    for entry_path in entries_dir.glob('*.md'):
        try:
            with open(entry_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Validate entry
            entry_errors = validate_entry(entry_path, content)
            if entry_errors:
                errors.extend([f'{entry_path.name}: {error}' for error in entry_errors])
                continue
            
            # Extract metadata
            frontmatter, markdown_content = extract_frontmatter(content)
            
            # Create entry object
            entry = {
                'filename': entry_path.name,
                'slug': entry_path.stem,
                'path': f'entries/{entry_path.name}',
                'frontmatter': frontmatter,
                'word_count': len(markdown_content.split()),
                'file_size': entry_path.stat().st_size,
                'modified_at': datetime.fromtimestamp(entry_path.stat().st_mtime).isoformat()
            }
            
            entries.append(entry)
            
        except Exception as e:
            errors.append(f'{entry_path.name}: Error processing file - {e}')
    
    # Sort entries by date (newest first)
    entries.sort(key=lambda x: x['frontmatter'].get('date', ''), reverse=True)
    
    return {
        'entries': entries,
        'config': config,
        'errors': errors,
        'stats': {
            'total_entries': len(entries),
            'total_errors': len(errors),
            'latest_entry': entries[0]['frontmatter'].get('date') if entries else None
        },
        'generated_at': datetime.now().isoformat()
    }

def main():
    '''Main function to generate blog index.'''
    project_root = Path(__file__).parent.parent
    blog_dir = project_root / 'dev-blog'
    
    print('Generating dev blog index...')
    
    index_data = generate_blog_index(blog_dir)
    
    # Write index.json
    index_path = blog_dir / 'index.json'
    with open(index_path, 'w', encoding='utf-8') as f:
        json.dump(index_data, f, indent=2, ensure_ascii=True)
    
    print(f'Generated index with {index_data['stats']['total_entries']} entries')
    
    if index_data['errors']:
        print('ERRORS found:')
        for error in index_data['errors']:
            print(f'  - {error}')
        return 1
    
    print('SUCCESS: Blog index generated successfully')
    return 0

if __name__ == '__main__':
    exit(main())
