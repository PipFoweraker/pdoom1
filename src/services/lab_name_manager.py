"""
Lab Name Manager - Handles lab naming for pseudonymous gameplay

This module provides functionality for:
- Loading lab names from CSV assets
- Randomly selecting appropriate lab names
- Managing lab name persistence across game sessions
- Supporting pseudonymous leaderboard integration
"""

import csv
from typing import List, Tuple, Optional
from src.services.deterministic_rng import get_rng
from src.services.resource_manager import get_asset_path

class LabNameManager:
    """Manages lab names for the player's organization"""
    
    def __init__(self):
        self._lab_names: List[Tuple[str, str]] = []
        self._load_lab_names()
    
    def _load_lab_names(self) -> None:
        """Load lab names from CSV file"""
        csv_path = get_asset_path("lab_names.csv")
        
        try:
            with open(csv_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                self._lab_names = [(row['name'], row['theme']) for row in reader]
        except FileNotFoundError:
            # Fallback names if CSV is missing
            self._lab_names = [
                ("Axiom Labs", "mathematical"),
                ("Beacon AI", "guidance"), 
                ("Cerberus Systems", "security"),
                ("Delta Dynamics", "change"),
                ("Enigma Institute", "mystery"),
                ("Frontier Labs", "exploration"),
                ("Genesis AI", "creation"),
                ("Horizon Computing", "future")
            ]
    
    def get_random_lab_name(self, seed: Optional[str] = None) -> str:
        """
        Get a random lab name, optionally using a specific seed
        
        Args:
            seed: Optional seed for deterministic selection
            
        Returns:
            Selected lab name string
        """
        if not self._lab_names:
            return "Unknown Labs"
        
        if seed:
            # Use deterministic selection based on seed if RNG is available
            try:
                rng = get_rng()
                if rng:
                    return rng.choice(self._lab_names, "lab_name_selection")[0]
            except RuntimeError:
                # RNG not initialized yet, fall back to system random with seed
                import random
                temp_rng = random.Random(seed)
                return temp_rng.choice(self._lab_names)[0]
        
        # Fallback to system random
        return random.choice(self._lab_names)[0]
    
    def get_lab_names_by_theme(self, theme: str) -> List[str]:
        """Get all lab names matching a specific theme"""
        return [name for name, lab_theme in self._lab_names if lab_theme == theme]
    
    def get_all_themes(self) -> List[str]:
        """Get all available themes"""
        return list(set(theme for _, theme in self._lab_names))
    
    def validate_lab_name(self, name: str) -> bool:
        """Check if a lab name is valid (exists in our list)"""
        return any(lab_name == name for lab_name, _ in self._lab_names)

# Global instance
_lab_name_manager = None

def get_lab_name_manager() -> LabNameManager:
    """Get the global lab name manager instance"""
    global _lab_name_manager
    if _lab_name_manager is None:
        _lab_name_manager = LabNameManager()
    return _lab_name_manager
