# !/usr/bin/env python3
'''
Intelligent ASCII Converter for P(Doom) Documentation

A sophisticated tool that converts Unicode to ASCII while preserving semantic meaning
and maintaining professional documentation quality. No ugly placeholder brackets.

Philosophy:
- Contextually intelligent replacements that preserve meaning
- Elegant ASCII alternatives that maintain readability  
- Semantic preservation over mechanical replacement
- Professional documentation standards
'''

import re
import argparse
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any, Union
import unicodedata

# Import our logging system
try:
    from scripts.logging_system import LogCategory
    has_logging_system = True
    logcategory_ascii = LogCategory.ASCII if hasattr(LogCategory, 'ASCII') else 'ASCII'
except ImportError:
    has_logging_system = False
    logcategory_ascii = 'ASCII'

class MockLogger:
    def info(self, msg: str, **kwargs: Any) -> None: print(f'[INFO] {msg}')
    def warning(self, msg: str, **kwargs: Any) -> None: print(f'[WARNING] {msg}')
    def error(self, msg: str, **kwargs: Any) -> None: print(f'[ERROR] {msg}')
    def debug(self, msg: str, **kwargs: Any) -> None: print(f'[DEBUG] {msg}')
    def step_start(self, name: str, **kwargs: Any) -> None: print(f'[START] {name}')
    def step_success(self, name: str, **kwargs: Any) -> None: print(f'[SUCCESS] {name}')
    def step_failure(self, name: str, **kwargs: Any) -> None: print(f'[FAILURE] {name}')
    def file_operation(self, op: str, path: str, result: str, **kwargs: Any) -> None: print(f'[FILE] {op} {path}: {result}')
    def metrics(self, name: str, value: Union[str, int, float], unit: Optional[str] = None, **kwargs: Any) -> None: print(f'[METRIC] {name}: {value} {unit or ""}')
    def session_summary(self, success: bool, **kwargs: Any) -> None: print(f'[SUMMARY] Success: {success}')

def get_logger(name: str, category: Optional[Any] = None, verbose: bool = False, structured: bool = False) -> MockLogger:
    return MockLogger()

class TimedOperation:
    def __init__(self, logger: MockLogger, name: str, **kwargs: Any) -> None:
        self.logger = logger
        self.name = name
    def __enter__(self) -> 'TimedOperation': return self
    def __exit__(self, *args: Any) -> None: pass


class IntelligentASCIIConverter:
    '''Converts Unicode to ASCII with contextual intelligence and semantic preservation.'''
    
    def __init__(self, verbose: bool = False):
        self.logger = get_logger('ascii_converter', logcategory_ascii, verbose=verbose)
        self.logger.info('Intelligent ASCII Converter initialized')
        # Intelligent contextual replacements
        self.smart_replacements = {
            # Typography - elegant alternatives
            '\u2013': ' - ',      # EN DASH -> spaced dash
            '\u2014': ' -- ',     # EM DASH -> spaced double dash  
            '\u2015': ' -- ',     # HORIZONTAL BAR -> spaced double dash
            '\u2026': '...',      # ELLIPSIS -> three dots
            
            # Quotation marks - standard ASCII quotes
            '\u201c': ''',        # LEFT DOUBLE QUOTATION 
            '\u201d': ''',        # RIGHT DOUBLE QUOTATION
            '\u2018': ''',        # LEFT SINGLE QUOTATION
            '\u2019': ''',        # RIGHT SINGLE QUOTATION
            '\u00ab': ''',        # LEFT ANGLE QUOTATION
            '\u00bb': ''',        # RIGHT ANGLE QUOTATION
            
            # List markers - clean alternatives
            '\u2022': '* ',       # BULLET -> asterisk with space
            '\u2023': '* ',       # TRIANGULAR BULLET -> asterisk
            '\u2043': '- ',       # HYPHEN BULLET -> dash with space
            '\u25cf': '* ',       # BLACK CIRCLE -> asterisk
            '\u25cb': 'o ',       # WHITE CIRCLE -> letter o
            
            # Arrows - conventional ASCII alternatives
            '\u2192': ' -> ',     # RIGHTWARDS ARROW
            '\u2190': ' <- ',     # LEFTWARDS ARROW  
            '\u2194': ' <-> ',    # LEFT RIGHT ARROW
            '\u21d2': ' => ',     # RIGHTWARDS DOUBLE ARROW
            '\u2191': ' ^ ',      # UPWARDS ARROW
            '\u2193': ' v ',      # DOWNWARDS ARROW
            
            # Mathematical symbols
            '\u00b1': '+/-',      # PLUS-MINUS
            '\u00d7': 'x',        # MULTIPLICATION SIGN
            '\u00f7': '/',        # DIVISION SIGN
            '\u2260': '!=',       # NOT EQUAL TO
            '\u2264': '<=',       # LESS THAN OR EQUAL TO
            '\u2265': '>=',       # GREATER THAN OR EQUAL TO
            '\u221e': 'infinity', # INFINITY
            
            # Currency - written out for clarity
            '\u20ac': 'EUR',      # EURO SIGN
            '\u00a3': 'GBP',      # POUND SIGN
            '\u00a5': 'JPY',      # YEN SIGN
            '\u00a2': 'cents',    # CENT SIGN
            
            # Fractions - standard notation
            '\u00bd': '1/2',      # ONE HALF
            '\u00bc': '1/4',      # ONE QUARTER  
            '\u00be': '3/4',      # THREE QUARTERS
            '\u2153': '1/3',      # ONE THIRD
            '\u2154': '2/3',      # TWO THIRDS
        }
        
        # Box drawing characters - convert to simple ASCII alternatives
        self.box_drawing_replacements = {
            # Tree structure characters
            '\u251c': '|-',       # BOX DRAWINGS LIGHT VERTICAL AND RIGHT
            '\u2500': '-',        # BOX DRAWINGS LIGHT HORIZONTAL
            '\u2502': '|',        # BOX DRAWINGS LIGHT VERTICAL
            '\u2514': '`-',       # BOX DRAWINGS LIGHT UP AND RIGHT
            '\u250c': '+-',       # BOX DRAWINGS LIGHT DOWN AND RIGHT
            '\u2510': '-+',       # BOX DRAWINGS LIGHT DOWN AND LEFT
            '\u2518': '-`',       # BOX DRAWINGS LIGHT UP AND LEFT
            '\u253c': '+',        # BOX DRAWINGS LIGHT VERTICAL AND HORIZONTAL
            '\u252c': '+',        # BOX DRAWINGS LIGHT DOWN AND HORIZONTAL
            '\u2534': '+',        # BOX DRAWINGS LIGHT UP AND HORIZONTAL
            '\u2524': '-|',       # BOX DRAWINGS LIGHT VERTICAL AND LEFT
            
            # Double line variants
            '\u2550': '=',        # BOX DRAWINGS DOUBLE HORIZONTAL
            '\u2551': '||',       # BOX DRAWINGS DOUBLE VERTICAL
            '\u2552': '|=',       # BOX DRAWINGS DOWN SINGLE AND RIGHT DOUBLE
            '\u2553': '||',       # BOX DRAWINGS DOWN DOUBLE AND RIGHT SINGLE
            '\u2554': '+=',       # BOX DRAWINGS DOUBLE DOWN AND RIGHT
            '\u2555': '=|',       # BOX DRAWINGS DOWN SINGLE AND LEFT DOUBLE
            '\u2556': '||',       # BOX DRAWINGS DOWN DOUBLE AND LEFT SINGLE
            '\u2557': '=+',       # BOX DRAWINGS DOUBLE DOWN AND LEFT
            '\u2558': '|=',       # BOX DRAWINGS UP SINGLE AND RIGHT DOUBLE
            '\u2559': '||',       # BOX DRAWINGS UP DOUBLE AND RIGHT SINGLE
            '\u255a': '`=',       # BOX DRAWINGS DOUBLE UP AND RIGHT
            '\u255b': '=|',       # BOX DRAWINGS UP SINGLE AND LEFT DOUBLE
            '\u255c': '||',       # BOX DRAWINGS UP DOUBLE AND LEFT SINGLE
            '\u255d': '=`',       # BOX DRAWINGS DOUBLE UP AND LEFT
            '\u255e': '|+',       # BOX DRAWINGS VERTICAL SINGLE AND RIGHT DOUBLE
            '\u255f': '||',       # BOX DRAWINGS VERTICAL DOUBLE AND RIGHT SINGLE
            '\u2560': '+=',       # BOX DRAWINGS DOUBLE VERTICAL AND RIGHT
            '\u2561': '+|',       # BOX DRAWINGS VERTICAL SINGLE AND LEFT DOUBLE
            '\u2562': '||',       # BOX DRAWINGS VERTICAL DOUBLE AND LEFT SINGLE
            '\u2563': '=+',       # BOX DRAWINGS DOUBLE VERTICAL AND LEFT
            '\u2564': '+=',       # BOX DRAWINGS DOWN SINGLE AND HORIZONTAL DOUBLE
            '\u2565': '+',        # BOX DRAWINGS DOWN DOUBLE AND HORIZONTAL SINGLE
            '\u2566': '+=',       # BOX DRAWINGS DOUBLE DOWN AND HORIZONTAL
            '\u2567': '+=',       # BOX DRAWINGS UP SINGLE AND HORIZONTAL DOUBLE
            '\u2568': '+',        # BOX DRAWINGS UP DOUBLE AND HORIZONTAL SINGLE
            '\u2569': '+=',       # BOX DRAWINGS DOUBLE UP AND HORIZONTAL
            '\u256a': '+=',       # BOX DRAWINGS VERTICAL SINGLE AND HORIZONTAL DOUBLE
            '\u256b': '+',        # BOX DRAWINGS VERTICAL DOUBLE AND HORIZONTAL SINGLE
            '\u256c': '+=',       # BOX DRAWINGS DOUBLE VERTICAL AND HORIZONTAL
        }
        
        # Context-aware emoji conversions - semantic preservation
        self.emoji_contexts = {
            # Status and feedback - professional alternatives
            '\u2705': 'SUCCESS',          # WHITE HEAVY CHECK MARK
            '\u2714': 'DONE',             # HEAVY CHECK MARK  
            '\u2713': 'CHECKED',          # CHECK MARK
            '\u274c': 'ERROR',            # CROSS MARK
            '\u274e': 'FAILED',           # NEGATIVE SQUARED CROSS MARK
            '\u2717': 'FAILED',           # BALLOT X
            '\u2718': 'ERROR',            # HEAVY BALLOT X
            '\u2612': 'CHECKED',          # BALLOT BOX WITH X
            '\u26a0': 'WARNING',          # WARNING SIGN
            '\u2757': 'IMPORTANT',        # HEAVY EXCLAMATION MARK
            '\u2755': 'NOTICE',           # WHITE EXCLAMATION MARK
            '\u2754': 'QUESTION',         # WHITE QUESTION MARK
            '\u2753': 'HELP',             # BLACK QUESTION MARK
            '\u2139': 'INFO',             # INFORMATION SOURCE
            '\ufe0f': '',                 # VARIATION SELECTOR-16 (invisible modifier)
            
            # Development and technical
            '\U0001f680': 'LAUNCH',       # ROCKET -> launch/deploy
            '\U0001f527': 'TOOLS',        # WRENCH -> tools/config
            '\U0001f528': 'HAMMER',       # HAMMER -> build/fix
            '\U0001f52c': 'MICROSCOPE',   # MICROSCOPE -> analysis/debug
            '\U0001f50d': 'SEARCH',       # MAGNIFYING GLASS -> search/find
            '\U0001f512': 'SECURE',       # LOCK -> security/private
            '\U0001f513': 'OPEN',         # UNLOCK -> public/accessible
            '\U0001f514': 'ALERT',        # BELL -> notification/alert
            '\U0001f4bb': 'COMPUTER',     # LAPTOP -> computing/development
            '\U0001f4be': 'SAVE',         # FLOPPY DISK -> save/storage
            '\U0001f4c1': 'FOLDER',       # FILE FOLDER -> directory/organize
            '\U0001f4c4': 'DOCUMENT',     # PAGE DOCUMENT -> file/documentation
            '\U0001f4ca': 'METRICS',      # BAR CHART -> data/analytics
            '\U0001f4c8': 'GROWTH',       # UPWARD CHART -> improvement/increase
            '\U0001f4c9': 'DECLINE',      # DOWNWARD CHART -> decrease/issues
            '\U0001f4dd': 'MEMO',         # MEMO -> documentation/notes
            '\U0001f4cb': 'CLIPBOARD',    # CLIPBOARD -> tasks/checklist
            '\U0001f4d6': 'BOOK',         # OPEN BOOK -> documentation/guide
            '\U0001f310': 'GLOBAL',       # GLOBE WITH MERIDIANS -> worldwide/web
            '\U0001f3e0': 'HOME',         # HOUSE BUILDING -> main/home
            '\U0001f5d1': 'TRASH',        # WASTEBASKET -> delete/remove
            '\U0001f9ed': 'COMPASS',      # COMPASS -> navigation/direction
            '\U0001f3af': 'TARGET',       # DIRECT HIT -> goal/target
            '\u23ed': 'SKIP',             # BLACK RIGHT-POINTING DOUBLE TRIANGLE WITH VERTICAL BAR -> skip/next
            '\u2728': 'SPARKLES',         # SPARKLES -> special/highlight
            
            # Achievement and status
            '\U0001f3c6': 'ACHIEVEMENT',  # TROPHY -> major accomplishment
            '\U0001f3c5': 'MEDAL',        # SPORTS MEDAL -> recognition
            '\U0001f451': 'PRIORITY',     # CROWN -> high priority/important
            '\U0001f4af': 'PERFECT',      # HUNDRED POINTS -> 100%/complete
            '\U0001f525': 'HOT',          # FIRE -> critical/urgent/popular
            '\U0001f389': 'CELEBRATION',  # PARTY POPPER -> milestone/release
            '\U0001f44d': 'APPROVED',     # THUMBS UP -> approved/good
            '\U0001f44e': 'REJECTED',     # THUMBS DOWN -> rejected/bad
            
            # Process and workflow  
            '\U0001f504': 'REFRESH',      # ARROWS CYCLE -> update/reload
            '\U0001f501': 'REPEAT',       # REPEAT -> loop/iterate
            '\U0001f500': 'SHUFFLE',      # TWISTED ARROWS -> randomize/mix
            '\U0001f519': 'BACK',         # BACK ARROW -> return/previous
            '\U0001f51a': 'END',          # END ARROW -> complete/finish
            '\U0001f51b': 'ON',           # ON ARROW -> enable/start
            '\U0001f51c': 'SOON',         # SOON ARROW -> upcoming/planned
            '\U0001f51d': 'TOP',          # TOP ARROW -> priority/featured
            
            # Communication
            '\U0001f4e7': 'MESSAGE',      # EMAIL -> communication
            '\U0001f4e2': 'ANNOUNCE',     # LOUDSPEAKER -> announcement
            '\U0001f4e3': 'BROADCAST',    # MEGAPHONE -> public message
            '\U0001f4ac': 'COMMENT',      # SPEECH BALLOON -> discussion
            '\U0001f4ad': 'THOUGHT',      # THOUGHT BALLOON -> idea/concept
            
            # Time and scheduling
            '\U0001f4c5': 'CALENDAR',     # CALENDAR -> scheduling
            '\U0001f551': 'TIME',         # CLOCK -> timing/duration
            '\U0001f55c': 'DEADLINE',     # CLOCK -> deadline/urgent time
            '\u23f0': 'ALARM',            # ALARM CLOCK -> reminder/alert
            '\u23f1': 'STOPWATCH',        # STOPWATCH -> timing/measurement
            '\u23f2': 'TIMER',            # TIMER -> countdown/duration
        }
        
        # Markdown-specific patterns that need special handling
        self.markdown_patterns: List[Tuple[str, Any]] = [
            # Header markers that might contain Unicode
            (r'^(#{1,6})\s*([^\n]*?)(\s*)$', self._fix_header_line),
            # List items that might have Unicode bullets
            (r'^(\s*)([\u2022\u2023\u2043\u25cf\u25cb\u25aa\u25ab])\s+(.+)$', self._fix_list_item),
            # Emphasis markers  
            (r'\*\*([^*]+)\*\*', self._preserve_emphasis),
            (r'\*([^*]+)\*', self._preserve_emphasis),
            # Code blocks - preserve content
            (r'```([^`]*)```', self._preserve_code_block),
            (r'`([^`]+)`', self._preserve_inline_code),
        ]
    
    def _fix_header_line(self, match: re.Match[str]) -> str:
        '''Fix Unicode in markdown headers while preserving structure.'''
        prefix, content, suffix = match.groups()
        clean_content = self._apply_replacements(content)
        return f'{prefix} {clean_content}{suffix}'
    
    def _fix_list_item(self, match: re.Match[str]) -> str:
        '''Convert Unicode list bullets to standard ASCII.'''
        indent, bullet, content = match.groups()
        ascii_bullet = self.smart_replacements.get(bullet, '*')
        clean_content = self._apply_replacements(content)
        return f'{indent}{ascii_bullet} {clean_content}'
    
    def _preserve_emphasis(self, match: re.Match[str]) -> str:
        '''Preserve markdown emphasis while cleaning content.'''
        return match.group(0)  # Return unchanged for now
    
    def _preserve_code_block(self, match: re.Match[str]) -> str:
        '''Preserve code blocks unchanged.'''
        return match.group(0)
    
    def _preserve_inline_code(self, match: re.Match[str]) -> str:
        '''Preserve inline code unchanged.'''
        return match.group(0)
    
    def _apply_replacements(self, text: str) -> str:
        '''Apply intelligent replacements to text.'''
        # First apply smart typography replacements
        for unicode_char, replacement in self.smart_replacements.items():
            text = text.replace(unicode_char, replacement)
        
        # Apply box drawing character replacements
        for unicode_char, replacement in self.box_drawing_replacements.items():
            text = text.replace(unicode_char, replacement)
        
        # Then apply contextual emoji replacements
        for unicode_char, replacement in self.emoji_contexts.items():
            text = text.replace(unicode_char, replacement)
        
        return text
    
    def _detect_context(self, text: str, position: int) -> str:
        '''Detect context around a Unicode character for smarter replacement.'''
        # Look at surrounding text to determine best replacement
        start = max(0, position - 20)
        end = min(len(text), position + 20)
        context = text[start:end].lower()
        
        # Context-based decision making
        if 'error' in context or 'fail' in context:
            return 'error_context'
        elif 'success' in context or 'complete' in context:
            return 'success_context'
        elif 'warning' in context or 'caution' in context:
            return 'warning_context'
        elif 'feature' in context or 'new' in context:
            return 'feature_context'
        else:
            return 'neutral_context'
    
    def convert_text(self, text: str) -> Tuple[str, List[str]]:
        '''Convert text with intelligent ASCII replacements.'''
        original_text = text
        changes: List[str] = []
        
        self.logger.debug('Starting text conversion', extra_data={
            'text_length': len(text),
            'original_text_preview': text[:100] + '...' if len(text) > 100 else text
        })
        
        with TimedOperation(self.logger, 'markdown_processing'):
            # Apply markdown-aware processing
            for pattern, handler in self.markdown_patterns:
                text = re.sub(pattern, handler, text, flags=re.MULTILINE)
        
        with TimedOperation(self.logger, 'replacement_processing'):
            # Apply general replacements
            text = self._apply_replacements(text)
        
        # Find any remaining non-ASCII characters for reporting
        remaining_unicode: List[str] = []
        for i, char in enumerate(text):
            if ord(char) > 127:
                char_name = unicodedata.name(char, f'U+{ord(char):04X}')
                context = self._detect_context(text, i)
                remaining_unicode.append(f"'{char}' ({char_name}) at position {i} in {context}")
        
        if text != original_text:
            changes.append(f'Applied intelligent ASCII conversion')
            self.logger.metrics('characters_converted', len(original_text) - len(text.encode('ascii', 'ignore').decode('ascii')))
        
        if remaining_unicode:
            changes.extend([f'Remaining Unicode: {char}' for char in remaining_unicode[:5]])
            self.logger.warning(f'Found {len(remaining_unicode)} remaining Unicode characters', 
                              extra_data={'remaining_count': len(remaining_unicode)})
        
        self.logger.debug('Text conversion completed', extra_data={
            'changes_made': len(changes) > 0,
            'remaining_unicode_count': len(remaining_unicode)
        })
        
        return text, changes
    
    def process_file(self, file_path: Path, dry_run: bool = False) -> Tuple[bool, List[str]]:
        '''Process a single file with intelligent conversion.'''
        self.logger.step_start(f'process_file', extra_data={
            'file_path': str(file_path),
            'dry_run': dry_run
        })
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                original_content = f.read()
        except UnicodeDecodeError:
            self.logger.file_operation('READ', str(file_path), 'FAILED - encoding issue')
            return False, [f'Cannot read {file_path} - encoding issue']
        except Exception as e:
            self.logger.error(f'Error reading file: {e}', extra_data={'file_path': str(file_path)})
            return False, [f'Error reading {file_path}: {e}']
        
        converted_content, changes = self.convert_text(original_content)
        
        if original_content == converted_content:
            self.logger.file_operation('PROCESS', str(file_path), 'NO_CHANGES')
            return True, ['No changes needed']
        
        if not dry_run:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(converted_content)
                self.logger.file_operation('WRITE', str(file_path), 'SUCCESS', extra_data={
                    'changes_count': len(changes)
                })
                self.logger.step_success('process_file', extra_data={'file_path': str(file_path)})
                return True, changes + ['File updated successfully']
            except Exception as e:
                self.logger.error(f'Error writing file: {e}', extra_data={'file_path': str(file_path)})
                return False, [f'Error writing {file_path}: {e}']
        
        self.logger.file_operation('SIMULATE', str(file_path), 'WOULD_UPDATE', extra_data={
            'changes_count': len(changes)
        })
        return True, changes + ['Would update file (dry run)']
    
    def process_directory(self, directory: Path, dry_run: bool = False) -> Dict[str, List[str]]:
        '''Process all relevant files in a directory.'''
        results: Dict[str, List[str]] = {}
        
        # File patterns to process
        patterns = [
            '*.md', '*.txt', '*.rst', '*.py', '*.json', '*.yaml', '*.yml',
            '*.toml', '*.cfg', '*.ini', '*.sh', '*.bat'
        ]
        
        files_to_process: List[Path] = []
        for pattern in patterns:
            files_to_process.extend(directory.rglob(pattern))
        
        # Exclude certain directories
        exclude_dirs = {'.git', '__pycache__', '.venv', 'venv', 'node_modules', '.pytest_cache'}
        
        for file_path in files_to_process:
            # Skip files in excluded directories
            if any(excluded in file_path.parts for excluded in exclude_dirs):
                continue
            
            success, messages = self.process_file(file_path, dry_run)
            if not success or len(messages) > 1:  # Only report files with changes or errors
                results[str(file_path.relative_to(directory))] = messages
        
        return results


def main():
    parser = argparse.ArgumentParser(
        description='Intelligent ASCII converter for P(Doom) documentation',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  python intelligent_ascii_converter.py --dry-run
  python intelligent_ascii_converter.py --file README.md
  python intelligent_ascii_converter.py --directory docs/
        '''
    )
    
    parser.add_argument('--dry-run', action='store_true',
                       help='Show what would be changed without making changes')
    parser.add_argument('--file', type=Path,
                       help='Process a specific file')
    parser.add_argument('--directory', type=Path, default=Path('.'),
                       help='Process all files in directory (default: current)')
    parser.add_argument('--verbose', action='store_true',
                       help='Show detailed output')
    parser.add_argument('--structured', action='store_true',
                       help='Use structured JSON output for CI/CD')
    
    args = parser.parse_args()
    
    # Initialize converter with logging
    converter = IntelligentASCIIConverter(verbose=args.verbose)
    
    # Log session start
    converter.logger.info('ASCII Converter session started', extra_data={
        'dry_run': args.dry_run,
        'target_file': str(args.file) if args.file else None,
        'target_directory': str(args.directory),
        'verbose': args.verbose,
        'structured': args.structured
    })
    
    success = True
    results: Dict[str, List[str]] = {}
    
    if args.file:
        if not args.file.exists():
            converter.logger.error(f'File does not exist: {args.file}')
            return 1
        
        with TimedOperation(converter.logger, f'process_single_file'):
            file_success, messages = converter.process_file(args.file, args.dry_run)
        
        if args.verbose or not file_success or len(messages) > 1:
            print(f'\n{args.file}:')
            for message in messages:
                print(f'  {message}')
        
        if not file_success:
            success = False
    
    else:
        if not args.directory.exists():
            converter.logger.error(f'Directory does not exist: {args.directory}')
            return 1
        
        with TimedOperation(converter.logger, 'process_directory', extra_data={
            'directory': str(args.directory)
        }):
            results = converter.process_directory(args.directory, args.dry_run)
        
        converter.logger.metrics('files_processed', len(results), 'files')
        
        if not results:
            print('All files are ASCII compliant - no changes needed')
            converter.logger.info('All files ASCII compliant')
        else:
            print(f'\nProcessed {len(results)} files with changes:')
            for file_path, messages in results.items():
                print(f'\n{file_path}:')
                for message in messages:
                    print(f'  {message}')
            
            if args.dry_run:
                print(f'\nDry run complete. Run without --dry-run to apply changes.')
                converter.logger.info('Dry run completed', extra_data={
                    'files_with_changes': len(results)
                })
            else:
                print(f'\nConversion complete. {len(results)} files updated.')
                converter.logger.info('Conversion completed', extra_data={
                    'files_updated': len(results)
                })
    
    # Log session summary
    results_count = len(results) if 'results' in locals() and results else 0
    converter.logger.session_summary(success, extra_data={
        'mode': 'single_file' if args.file else 'directory',
        'dry_run': args.dry_run,
        'files_processed': 1 if args.file else results_count
    })
    
    return 0 if success else 1


if __name__ == '__main__':
    exit(main())