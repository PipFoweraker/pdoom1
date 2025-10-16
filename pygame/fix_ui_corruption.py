#!/usr/bin/env python3
"""Fix widespread string corruption in ui.py"""

import re

def fix_ui_file():
    with open('ui.py', 'r', encoding='utf-8') as f:
        content = f.read()

    # Fix line 391: Pip Foweraker's with unescaped quote
    content = content.replace(
        "attribution_font.render('Pip Foweraker's',",
        'attribution_font.render("Pip Foweraker\'s",'
    )

    with open('ui.py', 'w', encoding='utf-8') as f:
        f.write(content)

    print("Fixed ui.py")

if __name__ == '__main__':
    fix_ui_file()
