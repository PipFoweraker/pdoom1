"""
Deterministic Random Number Generator for P(Doom)

Provides seed-based deterministic randomness for competitive play and debugging.
All game randomness should flow through this system to ensure reproducibility.
"""

import random
import hashlib
from typing import List, Any, Union


class DeterministicRNG:
    """
    Centralized deterministic random number generator.
    
    Uses seed + context to ensure same game state produces same outcomes
    while allowing different contexts to have independent randomness.
    """
    
    def __init__(self, base_seed: str):
        """Initialize with base game seed."""
        self.base_seed = str(base_seed)
        self.context_counters = {}
        
    def _get_context_seed(self, context: str, increment: bool = True) -> int:
        """
        Generate deterministic seed for specific context.
        
        Args:
            context: Unique identifier for randomness context (e.g., "turn_5_events")
            increment: Whether to increment counter for this context
            
        Returns:
            Deterministic integer seed
        """
        if context not in self.context_counters:
            self.context_counters[context] = 0
            
        if increment:
            self.context_counters[context] += 1
            
        # Create deterministic seed from base_seed + context + counter
        seed_string = f"{self.base_seed}_{context}_{self.context_counters[context]}"
        seed_hash = hashlib.md5(seed_string.encode()).hexdigest()
        return int(seed_hash[:8], 16)  # Use first 8 hex chars as seed
    
    def randint(self, a: int, b: int, context: str) -> int:
        """Generate deterministic random integer between a and b (inclusive)."""
        seed = self._get_context_seed(context)
        rng = random.Random(seed)
        return rng.randint(a, b)
    
    def random(self, context: str) -> float:
        """Generate deterministic random float between 0.0 and 1.0."""
        seed = self._get_context_seed(context)
        rng = random.Random(seed)
        return rng.random()
    
    def choice(self, sequence: List[Any], context: str) -> Any:
        """Choose deterministic random element from sequence."""
        seed = self._get_context_seed(context)
        rng = random.Random(seed)
        return rng.choice(sequence)
    
    def uniform(self, a: float, b: float, context: str) -> float:
        """Generate deterministic random float between a and b."""
        seed = self._get_context_seed(context)
        rng = random.Random(seed)
        return rng.uniform(a, b)
    
    def shuffle(self, sequence: List[Any], context: str) -> None:
        """Shuffle sequence deterministically in-place."""
        seed = self._get_context_seed(context)
        rng = random.Random(seed)
        rng.shuffle(sequence)
    
    def reset_context(self, context: str) -> None:
        """Reset counter for specific context (useful for testing)."""
        self.context_counters[context] = 0
    
    def get_debug_info(self) -> dict:
        """Get debug information about current RNG state."""
        return {
            'base_seed': self.base_seed,
            'context_counters': self.context_counters.copy(),
            'total_calls': sum(self.context_counters.values())
        }


# Global instance - will be initialized by GameState
deterministic_rng: DeterministicRNG = None


def init_deterministic_rng(seed: str):
    """Initialize global deterministic RNG with game seed."""
    global deterministic_rng
    deterministic_rng = DeterministicRNG(seed)


def get_rng() -> DeterministicRNG:
    """Get current deterministic RNG instance."""
    if deterministic_rng is None:
        raise RuntimeError("Deterministic RNG not initialized. Call init_deterministic_rng() first.")
    return deterministic_rng


# Convenience functions for common patterns
def det_randint(a: int, b: int, context: str) -> int:
    """Shorthand for deterministic randint."""
    return get_rng().randint(a, b, context)


def det_random(context: str) -> float:
    """Shorthand for deterministic random."""
    return get_rng().random(context)


def det_choice(sequence: List[Any], context: str) -> Any:
    """Shorthand for deterministic choice."""
    return get_rng().choice(sequence, context)


def is_deterministic_enabled() -> bool:
    """Check if deterministic RNG is enabled."""
    return deterministic_rng is not None


def reset_rng():
    """Reset the global RNG instance."""
    global deterministic_rng
    deterministic_rng = None
