"""
Historical Timeline Data Loader

Loads historical AI safety/capabilities events from JSON files.
Used to populate the "default timeline" - what happens if player takes no action.

Usage:
    from src.data.historical_timeline_loader import TimelineLoader

    loader = TimelineLoader()
    events = loader.load_all_events(start_year=2017)
    events_for_year = loader.load_year(2018)
"""

import json
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime


class TimelineLoader:
    """Loads historical timeline events from data files"""

    def __init__(self, data_dir: Optional[Path] = None):
        """
        Initialize timeline loader

        Args:
            data_dir: Path to historical_timeline directory
                     Defaults to shared/data/historical_timeline
        """
        if data_dir is None:
            # Default to shared/data/historical_timeline
            project_root = Path(__file__).parent.parent.parent
            data_dir = project_root / "shared" / "data" / "historical_timeline"

        self.data_dir = Path(data_dir)

        if not self.data_dir.exists():
            raise FileNotFoundError(
                f"Historical timeline data directory not found: {self.data_dir}"
            )

    def load_year(self, year: int) -> Optional[Dict]:
        """
        Load timeline events for a specific year

        Args:
            year: Year to load (e.g., 2017, 2018)

        Returns:
            Dictionary with year data, or None if file doesn't exist
        """
        year_file = self.data_dir / f"{year}.json"

        if not year_file.exists():
            return None

        try:
            with open(year_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in {year_file}: {e}")
        except Exception as e:
            raise RuntimeError(f"Error loading {year_file}: {e}")

    def load_all_events(self, start_year: int = 2017, end_year: Optional[int] = None) -> List[Dict]:
        """
        Load all timeline events from start_year to end_year

        Args:
            start_year: First year to load (default: 2017)
            end_year: Last year to load (default: current year)

        Returns:
            List of all timeline events, sorted by trigger_date
        """
        if end_year is None:
            end_year = datetime.now().year

        all_events = []

        for year in range(start_year, end_year + 1):
            year_data = self.load_year(year)
            if year_data:
                events = year_data.get('default_timeline_events', [])
                all_events.extend(events)

        # Sort by trigger_date
        all_events.sort(key=lambda e: e.get('trigger_date', '9999-99-99'))

        return all_events

    def get_events_for_date(self, date_str: str, events: Optional[List[Dict]] = None) -> List[Dict]:
        """
        Get all events that trigger on a specific date

        Args:
            date_str: Date in YYYY-MM-DD format
            events: List of events to filter (default: load all)

        Returns:
            List of events that trigger on this date
        """
        if events is None:
            events = self.load_all_events()

        return [e for e in events if e.get('trigger_date') == date_str]

    def get_available_years(self) -> List[int]:
        """
        Get list of years that have timeline data

        Returns:
            Sorted list of years with data files
        """
        years = []
        for file in self.data_dir.glob("*.json"):
            try:
                year = int(file.stem)
                years.append(year)
            except ValueError:
                # Skip non-year files
                continue

        return sorted(years)

    def get_events_by_type(self, event_type: str, events: Optional[List[Dict]] = None) -> List[Dict]:
        """
        Filter events by type

        Args:
            event_type: Type to filter (paper_publication, conference, etc.)
            events: List of events to filter (default: load all)

        Returns:
            List of events matching type
        """
        if events is None:
            events = self.load_all_events()

        return [e for e in events if e.get('type') == event_type]

    def get_events_by_tag(self, tag: str, events: Optional[List[Dict]] = None) -> List[Dict]:
        """
        Filter events by tag

        Args:
            tag: Tag to search for (e.g., 'safety', 'transformers')
            events: List of events to filter (default: load all)

        Returns:
            List of events with this tag
        """
        if events is None:
            events = self.load_all_events()

        return [e for e in events if tag in e.get('tags', [])]

    def get_background_events(self, year: int) -> List[Dict]:
        """
        Get background/flavor events for a year

        Args:
            year: Year to load

        Returns:
            List of background events
        """
        year_data = self.load_year(year)
        if year_data:
            return year_data.get('background_events', [])
        return []


# Convenience function for quick access
def load_timeline(start_year: int = 2017) -> List[Dict]:
    """
    Convenience function to quickly load timeline

    Args:
        start_year: Starting year (default: 2017)

    Returns:
        List of all timeline events
    """
    loader = TimelineLoader()
    return loader.load_all_events(start_year=start_year)


if __name__ == "__main__":
    # Test the loader
    print("=== Historical Timeline Loader Test ===\n")

    loader = TimelineLoader()

    # Show available years
    years = loader.get_available_years()
    print(f"Available years: {years}\n")

    # Load all events
    events = loader.load_all_events()
    print(f"Total events loaded: {len(events)}\n")

    # Show event types
    event_types = {}
    for event in events:
        event_type = event.get('type', 'unknown')
        event_types[event_type] = event_types.get(event_type, 0) + 1

    print("Events by type:")
    for event_type, count in sorted(event_types.items()):
        print(f"  {event_type}: {count}")

    print("\n=== Sample Events ===\n")
    for event in events[:3]:
        print(f"- {event.get('name')} ({event.get('trigger_date')})")
        print(f"  Type: {event.get('type')}")
        print(f"  Source: {event.get('source')}")
        print()
