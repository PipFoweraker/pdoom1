# !/usr/bin/env python3
'''
ASCII Compliance Fixer for P(Doom) Documentation

This tool systematically finds and replaces Unicode characters with ASCII equivalents
across all documentation files to ensure cross-platform compatibility.
'''

import os
import glob
import re
from typing import List, Tuple, Dict

class ASCIIComplianceFixer:
    def __init__(self):
        # Common Unicode to ASCII replacements
        self.replacements = {
            # Em and En dashes
            '\u2013': '-',  # EN DASH
            '\u2014': '--', # EM DASH
            '\u2015': '--', # HORIZONTAL BAR
            
            # Quotation marks
            '\u201c': ''',  # LEFT DOUBLE QUOTATION MARK
            '\u201d': ''',  # RIGHT DOUBLE QUOTATION MARK
            '\u2018': ''',  # LEFT SINGLE QUOTATION MARK  
            '\u2019': ''',  # RIGHT SINGLE QUOTATION MARK
            '\u00ab': ''',  # LEFT-POINTING DOUBLE ANGLE QUOTATION MARK
            '\u00bb': ''',  # RIGHT-POINTING DOUBLE ANGLE QUOTATION MARK
            
            # Bullets and list markers
            '\u2022': '*',  # BULLET
            '\u2023': '*',  # TRIANGULAR BULLET
            '\u2043': '*',  # HYPHEN BULLET
            '\u25cf': '*',  # BLACK CIRCLE
            '\u25cb': 'o',  # WHITE CIRCLE
            '\u25aa': '*',  # BLACK SMALL SQUARE
            '\u25ab': '*',  # WHITE SMALL SQUARE
            
            # Arrows
            '\u2192': '->',  # RIGHTWARDS ARROW
            '\u2190': '<-',  # LEFTWARDS ARROW
            '\u2194': '<->',  # LEFT RIGHT ARROW
            '\u21d2': '=>',  # RIGHTWARDS DOUBLE ARROW
            '\u2934': '->',  # ARROW POINTING RIGHTWARDS THEN CURVING UPWARDS
            '\u2935': '->',  # ARROW POINTING RIGHTWARDS THEN CURVING DOWNWARDS
            '\u2191': '^',   # UPWARDS ARROW (^)
            '\u2193': 'v',   # DOWNWARDS ARROW (v)
            '\u2196': '<-',  # NORTH WEST ARROW
            '\u2197': '->',  # NORTH EAST ARROW
            '\u2198': '->',  # SOUTH EAST ARROW
            '\u2199': '<-',  # SOUTH WEST ARROW
            
            # Mathematical symbols
            '\u2713': 'v',   # CHECK MARK (v)
            '\u2717': 'x',   # BALLOT X
            '\u2718': 'x',   # HEAVY BALLOT X
            '\u2714': 'V',   # HEAVY CHECK MARK
            '\u2715': 'X',   # MULTIPLICATION X
            '\u2716': 'X',   # HEAVY MULTIPLICATION X
            '\u00d7': 'x',   # MULTIPLICATION SIGN
            '\u00f7': '/',   # DIVISION SIGN
            '\u2260': '!=',  # NOT EQUAL TO
            '\u2264': '<=',  # LESS-THAN OR EQUAL TO
            '\u2265': '>=',  # GREATER-THAN OR EQUAL TO
            
            # Common punctuation
            '\u2026': '...',  # HORIZONTAL ELLIPSIS
            '\u00a0': ' ',    # NON-BREAKING SPACE
            '\u2007': ' ',    # FIGURE SPACE
            '\u2008': ' ',    # PUNCTUATION SPACE
            '\u2009': ' ',    # THIN SPACE
            '\u200a': ' ',    # HAIR SPACE
            
            # Special characters
            '\u00a9': '(c)',  # COPYRIGHT SIGN
            '\u00ae': '(R)',  # REGISTERED SIGN
            '\u2122': '(TM)', # TRADE MARK SIGN
            '\u00b0': 'deg',  # DEGREE SIGN
            '\u00b1': '+/-',  # PLUS-MINUS SIGN
            '\u00b5': 'u',    # MICRO SIGN
            '\u2328': '[KEYBOARD]',  # KEYBOARD ([KEYBOARD])
            '\U0001FA91': '[CHAIR]', # CHAIR ([CHAIR])
            
            # Fractions
            '\u00bd': '1/2',  # VULGAR FRACTION ONE HALF
            '\u00bc': '1/4',  # VULGAR FRACTION ONE QUARTER
            '\u00be': '3/4',  # VULGAR FRACTION THREE QUARTERS
        }
        
        # Emoji patterns (remove entirely or replace with text)
        self.emoji_replacements = {
            # Common emojis in documentation
            '\U0001f4a1': '[IDEA]',      # [IDEA] ELECTRIC LIGHT BULB
            '\U0001f4dd': '[NOTE]',      # [NOTE] MEMO
            '\U0001f4cb': '[CHECKLIST]', # [CHECKLIST] CLIPBOARD
            '\U0001f4ca': '[CHART]',     # [CHART] BAR CHART
            '\U0001f4c8': '[GRAPH]',     # [GRAPH] CHART WITH UPWARDS TREND
            '\U0001f4c9': '[GRAPH]',     # [GRAPH] CHART WITH DOWNWARDS TREND
            '\U0001f4c5': '[CALENDAR]',  # [CALENDAR] CALENDAR
            '\U0001f4c6': '[DATE]',      # [DATE] TEAR-OFF CALENDAR
            '\U0001f4e7': '[EMAIL]',     # [EMAIL] E-MAIL SYMBOL
            '\U0001f4e8': '[INBOX]',     # [INBOX] INCOMING ENVELOPE
            '\U0001f4f1': '[PHONE]',     # [PHONE] MOBILE PHONE
            '\U0001f4bb': '[LAPTOP]',    # [LAPTOP] PERSONAL COMPUTER
            '\U0001f4be': '[DISK]',      # [DISK] FLOPPY DISK
            '\U0001f4bf': '[DISC]',      # [DISC] OPTICAL DISC
            '\U0001f4c0': '[DVD]',       # [DVD] DVD
            '\U0001f50d': '[SEARCH]',    # [SEARCH] LEFT-POINTING MAGNIFYING GLASS
            '\U0001f512': '[LOCK]',      # [LOCK] LOCK
            '\U0001f513': '[UNLOCK]',    # [UNLOCK] OPEN LOCK
            '\U0001f514': '[BELL]',      # [BELL] BELL
            '\U0001f515': '[SILENT]',    # [SILENT] BELL WITH CANCELLATION STROKE
            '\U0001f5a5': '[DESKTOP]',   # [DESKTOP][EMOJI] DESKTOP COMPUTER
            '\U0001f5a8': '[PRINTER]',   # [PRINTER][EMOJI] PRINTER
            '\U0001f680': '[ROCKET]',    # [ROCKET] ROCKET
            '\U0001f525': '[FIRE]',      # [FIRE] FIRE
            '\U0001f4af': '[100]',       # [100] HUNDRED POINTS SYMBOL
            '\U0001f389': '[PARTY]',     # [PARTY] PARTY POPPER
            '\U0001f38a': '[CONFETTI]',  # [CONFETTI] CONFETTI BALL
            '\U0001f44d': '[THUMBS_UP]', # [THUMBS_UP] THUMBS UP SIGN
            '\U0001f44e': '[THUMBS_DOWN]', # [THUMBS_DOWN] THUMBS DOWN SIGN
            '\U0001f44f': '[CLAP]',      # [CLAP] CLAPPING HANDS SIGN
            '\U0001f64f': '[PRAY]',      # [PRAY] PERSON WITH FOLDED HANDS
            '\U0001f3af': '[TARGET]',    # [TARGET] DIRECT HIT
            '\U0001f3c6': '[TROPHY]',    # [TROPHY] TROPHY
            '\U0001f3c5': '[MEDAL]',     # [MEDAL] SPORTS MEDAL
            '\U0001f451': '[CROWN]',     # [CROWN] CROWN
            '\U0001f4a5': '[BOOM]',      # [BOOM] COLLISION SYMBOL
            '\U0001f4a6': '[SPLASH]',    # [SPLASH] SPLASHING SWEAT SYMBOL
            '\U0001f4a8': '[DASH]',      # [DASH] DASH SYMBOL
            '\U0001f4ab': '[DIZZY]',     # [DIZZY] DIZZY SYMBOL
            '\U0001f4ac': '[SPEECH]',    # [SPEECH] SPEECH BALLOON
            '\U0001f4ad': '[THOUGHT]',   # [THOUGHT] THOUGHT BALLOON
            '\U0001f590': '[HAND]',      # [HAND][EMOJI] RAISED HAND WITH FINGERS SPLAYED
            '\U0001f595': '[FINGER]',    # [FINGER] REVERSED HAND WITH MIDDLE FINGER EXTENDED
            
            # Weather
            '\u2600': '[SUN]',           # [SUN][EMOJI] BLACK SUN WITH RAYS
            '\u2601': '[CLOUD]',         # [CLOUD][EMOJI] CLOUD
            '\u26c5': '[PARTLY_CLOUDY]', # [PARTLY_CLOUDY] SUN BEHIND CLOUD
            '\u2614': '[RAIN]',          # [RAIN] UMBRELLA WITH RAIN DROPS
            '\u26a1': '[LIGHTNING]',     # [LIGHTNING] HIGH VOLTAGE SIGN
            '\u2744': '[SNOW]',          # [SNOW][EMOJI] SNOWFLAKE
            
            # Symbols
            '\u2764': '[HEART]',         # [HEART][EMOJI] HEAVY BLACK HEART
            '\u2665': '[HEART]',         # [HEART] BLACK HEART SUIT
            '\u2660': '[SPADE]',         # [SPADE] BLACK SPADE SUIT
            '\u2663': '[CLUB]',          # [CLUB] BLACK CLUB SUIT
            '\u2666': '[DIAMOND]',       # [DIAMOND] BLACK DIAMOND SUIT
            '\u2709': '[ENVELOPE]',      # [ENVELOPE][EMOJI] ENVELOPE
            '\u270f': '[PENCIL]',        # [PENCIL][EMOJI] PENCIL
            '\u2712': '[NIB]',           # [NIB][EMOJI] BLACK NIB
            '\u2702': '[SCISSORS]',      # [SCISSORS][EMOJI] BLACK SCISSORS
            '\u2708': '[PLANE]',         # [PLANE][EMOJI] AIRPLANE
            '\u26f5': '[SAILBOAT]',      # [SAILBOAT] SAILBOAT
            '\u26ea': '[CHURCH]',        # [CHURCH] CHURCH
            '\u26fd': '[FUEL]',          # [FUEL] FUEL PUMP
            '\u2699': '[GEAR]',          # [GEAR][EMOJI] GEAR
            '\u269b': '[ATOM]',          # [ATOM][EMOJI] ATOM SYMBOL
            '\u269c': '[FLEUR]',         # [FLEUR][EMOJI] FLEUR-DE-LIS
            '\u26a0': '[WARNING]',       # [WARNING][EMOJI] WARNING SIGN
            '\u26d4': '[NO_ENTRY]',      # [NO_ENTRY] NO ENTRY
            '\u2753': '[QUESTION]',      # [QUESTION] BLACK QUESTION MARK ORNAMENT
            '\u2757': '[EXCLAMATION]',   # [EXCLAMATION] HEAVY EXCLAMATION MARK SYMBOL
            '\u27a1': '[RIGHT_ARROW]',   # [RIGHT_ARROW][EMOJI] BLACK RIGHTWARDS ARROW
            '\u2b06': '[UP_ARROW]',      # [UP_ARROW][EMOJI] UPWARDS BLACK ARROW
            '\u2b07': '[DOWN_ARROW]',    # [DOWN_ARROW][EMOJI] DOWNWARDS BLACK ARROW
            '\u2b05': '[LEFT_ARROW]',    # [LEFT_ARROW][EMOJI] LEFTWARDS BLACK ARROW
            '\u2934': '[CURVE_RIGHT]',   # ->[EMOJI] ARROW POINTING RIGHTWARDS THEN CURVING UPWARDS
            '\u2935': '[CURVE_LEFT]',    # ->[EMOJI] ARROW POINTING RIGHTWARDS THEN CURVING DOWNWARDS
        }
        
        # Generic emoji pattern for anything we missed
        self.emoji_pattern = re.compile(r'[\U0001F600-\U0001F64F]|[\U0001F300-\U0001F5FF]|[\U0001F680-\U0001F6FF]|[\U0001F1E0-\U0001F1FF]|[\U00002702-\U000027B0]|[\U000024C2-\U0001F251]')

    def find_violations(self, file_path: str) -> List[Tuple[int, str, str]]:
        '''Find all Unicode violations in a file.'''
        violations = []
        
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
            
            # Try to decode as ASCII
            try:
                content.decode('ascii')
                return violations  # No violations
            except UnicodeDecodeError:
                pass
            
            # Find all violations by checking each character
            text_content = content.decode('utf-8', errors='replace')
            for i, char in enumerate(text_content):
                if ord(char) > 127:  # Non-ASCII character
                    # Suggest replacement
                    if char in self.replacements:
                        suggestion = self.replacements[char]
                    elif char in self.emoji_replacements:
                        suggestion = self.emoji_replacements[char]
                    elif self.emoji_pattern.match(char):
                        suggestion = '[EMOJI]'
                    else:
                        suggestion = f'[U+{ord(char):04X}]'
                    
                    violations.append((i, char, suggestion))
        
        except Exception as e:
            print(f'Error processing {file_path}: {e}')
        
        return violations

    def fix_file(self, file_path: str, dry_run: bool = False) -> Tuple[bool, int]:
        '''Fix Unicode violations in a file.'''
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            replacements_made = 0
            
            # Apply character replacements
            for unicode_char, ascii_replacement in self.replacements.items():
                if unicode_char in content:
                    content = content.replace(unicode_char, ascii_replacement)
                    replacements_made += content.count(ascii_replacement) - original_content.count(ascii_replacement)
            
            # Apply emoji replacements
            for emoji, replacement in self.emoji_replacements.items():
                if emoji in content:
                    content = content.replace(emoji, replacement)
                    replacements_made += 1
            
            # Handle any remaining emojis with generic replacement
            remaining_emojis = self.emoji_pattern.findall(content)
            if remaining_emojis:
                content = self.emoji_pattern.sub('[EMOJI]', content)
                replacements_made += len(remaining_emojis)
            
            # Handle any remaining non-ASCII characters
            import re
            remaining_unicode = []
            for i, char in enumerate(content):
                if ord(char) > 127:
                    remaining_unicode.append(char)
            
            if remaining_unicode:
                # Replace any remaining Unicode characters with generic markers
                for char in set(remaining_unicode):
                    if ord(char) > 127:
                        content = content.replace(char, f'[U+{ord(char):04X}]')
                        replacements_made += content.count(f'[U+{ord(char):04X}]')
            
            # Write back if changes were made and not in dry run mode
            if not dry_run and content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                return True, replacements_made
            
            return content != original_content, replacements_made
            
        except Exception as e:
            print(f'Error fixing {file_path}: {e}')
            return False, 0

    def process_directory(self, dry_run: bool = False) -> Dict[str, Tuple[bool, int]]:
        '''Process all documentation files in the repository.'''
        results = {}
        
        # File patterns to check
        patterns = [
            'docs/**/*.md',
            'dev-blog/**/*.md', 
            '*.md',
            'tests/**/*.py',  # Only if they have violations
            'src/**/*.py'     # Only if they have violations
        ]
        
        files_to_process = set()
        for pattern in patterns:
            files = glob.glob(pattern, recursive=True)
            for file_path in files:
                if os.path.isfile(file_path):
                    files_to_process.add(file_path)
        
        total_files = len(files_to_process)
        processed = 0
        
        for file_path in sorted(files_to_process):
            violations = self.find_violations(file_path)
            if violations:
                if dry_run:
                    print(f'Would fix {file_path}: {len(violations)} violations')
                    results[file_path] = (True, len(violations))
                else:
                    success, count = self.fix_file(file_path)
                    if success:
                        print(f'Fixed {file_path}: {count} replacements')
                    else:
                        print(f'No changes needed: {file_path}')
                    results[file_path] = (success, count)
            
            processed += 1
            if processed % 10 == 0:
                print(f'Progress: {processed}/{total_files} files processed')
        
        return results

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Fix ASCII compliance issues in P(Doom) documentation')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be changed without making changes')
    parser.add_argument('--file', help='Process a specific file instead of all files')
    
    args = parser.parse_args()
    
    fixer = ASCIIComplianceFixer()
    
    if args.file:
        if os.path.exists(args.file):
            violations = fixer.find_violations(args.file)
            if violations:
                print(f'Found {len(violations)} violations in {args.file}:')
                for pos, char, suggestion in violations[:10]:  # Show first 10
                    print(f'  Position {pos}: \'{char}\' -> \'{suggestion}\'')
                if len(violations) > 10:
                    print(f'  ... and {len(violations) - 10} more')
                
                if not args.dry_run:
                    success, count = fixer.fix_file(args.file)
                    if success:
                        print(f'Fixed {count} violations in {args.file}')
                    else:
                        print('No changes made')
            else:
                print(f'No violations found in {args.file}')
        else:
            print(f'File not found: {args.file}')
    else:
        print('Processing all files...')
        results = fixer.process_directory(dry_run=args.dry_run)
        
        total_files_fixed = sum(1 for success, _ in results.values() if success)
        total_replacements = sum(count for _, count in results.values())
        
        print(f'\nSummary:')
        print(f'Files processed: {len(results)}')
        print(f'Files {'would be ' if args.dry_run else ''}fixed: {total_files_fixed}')
        print(f'Total replacements {'would be ' if args.dry_run else ''}made: {total_replacements}')

if __name__ == '__main__':
    main()
