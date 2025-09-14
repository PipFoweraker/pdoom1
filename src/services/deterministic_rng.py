"""
Deterministic RNG System for P(Doom): Reproducible Strategic Gameplay

This system enables:
- Perfect competitive integrity through seed-based determinism
- Community challenge sharing with memorable seed names
- Complete reproducibility for analysis and verification
- Tournament-ready standardized scenarios
- Full debug visibility for community engagement

Philosophy: Transform P(Doom) from luck-based to skill-based strategy gaming
"""

import hashlib
import random
import time
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field


@dataclass
class RNGCall:
    """Records individual RNG calls for debugging and analysis."""
    turn: int
    call_type: str  # 'random', 'choice', 'randint', etc.
    parameters: Dict[str, Any]
    result: Any
    seed_state_after: str
    timestamp: float = field(default_factory=time.time)


class DeterministicRNG:
    """
    Community-Focused Deterministic RNG for Competitive P(Doom)
    
    Features:
    - Memorable seed names for community challenges (e.g., "DOOM-WINTER-CRISIS")
    - Complete call logging for analysis and debugging  
    - Tournament-ready reproducible scenarios
    - Context-aware seeding for complex game states
    - Debug-friendly verbose output for community engagement
    - Export capabilities for challenge sharing
    
    Uses seed + context to ensure same game state produces same outcomes
    while allowing different contexts to have independent randomness.
    """
    
    def __init__(self, base_seed: str):
        """Initialize with base game seed."""
        self.base_seed = str(base_seed)
        self.context_counters: Dict[str, int] = {}
        self.call_history: List[RNGCall] = []
        self.verbose_debug = False
        self.current_turn = 0
        
    def set_turn(self, turn: int) -> None:
        """Update the current game turn for call tracking."""
        self.current_turn = turn
    
    def enable_verbose_debug(self, enabled: bool = True) -> None:
        """Enable hyper-verbose debugging for community analysis."""
        self.verbose_debug = enabled
    
    def _record_call(self, call_type: str, parameters: Dict[str, Any], result: Any, context: str) -> None:
        """Record an RNG call for debugging and analysis."""
        call = RNGCall(
            turn=self.current_turn,
            call_type=call_type,
            parameters=parameters,
            result=result,
            seed_state_after=f"{self.base_seed}_{context}_{self.context_counters.get(context, 0)}"
        )
        self.call_history.append(call)
        
        if self.verbose_debug:
            print(f"[RNG] Turn {self.current_turn}: {call_type}({parameters}) -> {result} [seed: {call.seed_state_after}]")
    
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
        result = rng.randint(a, b)
        self._record_call("randint", {"a": a, "b": b, "context": context}, result, context)
        return result
    
    def random(self, context: str) -> float:
        """Generate deterministic random float between 0.0 and 1.0."""
        seed = self._get_context_seed(context)
        rng = random.Random(seed)
        result = rng.random()
        self._record_call("random", {"context": context}, result, context)
        return result
    
    def choice(self, sequence: List[Any], context: str) -> Any:
        """Choose deterministic random element from sequence."""
        seed = self._get_context_seed(context)
        rng = random.Random(seed)
        result = rng.choice(sequence)
        self._record_call("choice", {"sequence_len": len(sequence), "context": context}, result, context)
        return result
    
    def uniform(self, a: float, b: float, context: str) -> float:
        """Generate deterministic random float between a and b."""
        seed = self._get_context_seed(context)
        rng = random.Random(seed)
        result = rng.uniform(a, b)
        self._record_call("uniform", {"a": a, "b": b, "context": context}, result, context)
        return result
    
    def shuffle(self, sequence: List[Any], context: str) -> None:
        """Shuffle sequence deterministically in-place."""
        seed = self._get_context_seed(context)
        rng = random.Random(seed)
        rng.shuffle(sequence)
        self._record_call("shuffle", {"sequence_len": len(sequence), "context": context}, None, context)
    
    def reset_context(self, context: str) -> None:
        """Reset counter for specific context (useful for testing)."""
        self.context_counters[context] = 0
    
    def get_debug_info(self) -> Dict[str, Any]:
        """Get debug information about current RNG state."""
        return {
            'base_seed': self.base_seed,
            'context_counters': self.context_counters.copy(),
            'total_calls': sum(self.context_counters.values()),
            'call_history_count': len(self.call_history),
            'current_turn': self.current_turn,
            'verbose_debug': self.verbose_debug
        }
    
    def get_challenge_info(self) -> Dict[str, Any]:
        """Export challenge information for community sharing."""
        return {
            'seed': self.base_seed,
            'total_rng_calls': len(self.call_history),
            'contexts_used': list(self.context_counters.keys()),
            'turns_played': self.current_turn,
            'deterministic_signature': hashlib.md5(
                f"{self.base_seed}_{self.current_turn}_{len(self.call_history)}".encode()
            ).hexdigest()[:16]
        }
    
    def export_call_history(self) -> List[Dict[str, Any]]:
        """Export complete call history for debugging and analysis."""
        return [
            {
                'turn': call.turn,
                'call_type': call.call_type,
                'parameters': call.parameters,
                'result': call.result,
                'seed_state': call.seed_state_after,
                'timestamp': call.timestamp
            }
            for call in self.call_history
        ]
    
    def generate_memorable_seed(self, base_name: str = "PDOOM") -> str:
        """Generate memorable seed names for community challenges."""
        import time
        timestamp = int(time.time())
        
        # Adjectives and nouns for memorable combinations
        adjectives = ["WINTER", "SHADOW", "STORM", "SILVER", "GOLDEN", "CRIMSON", "DARK", "BRIGHT"]
        nouns = ["CRISIS", "RISE", "FALL", "DAWN", "NIGHT", "EDGE", "FIRE", "STEEL"]
        
        # Use timestamp to pick words deterministically  
        adj_idx = (timestamp // 100) % len(adjectives)
        noun_idx = (timestamp // 10) % len(nouns)
        
        return f"{base_name}-{adjectives[adj_idx]}-{nouns[noun_idx]}-{timestamp % 10000}"


# Global instance - will be initialized by GameState
deterministic_rng: Optional[DeterministicRNG] = None


def init_deterministic_rng(seed: str) -> None:
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


def reset_rng() -> None:
    """Reset the global RNG instance."""
    global deterministic_rng
    deterministic_rng = None


def create_challenge_seed(description: str = "") -> str:
    """Create a memorable seed for community challenges."""
    if deterministic_rng is None:
        # Create temporary instance just for seed generation
        temp_rng = DeterministicRNG("temp")
        return temp_rng.generate_memorable_seed()
    return deterministic_rng.generate_memorable_seed()


def enable_community_debug() -> None:
    """Enable verbose debugging for community engagement."""
    if deterministic_rng is not None:
        deterministic_rng.enable_verbose_debug(True)
        print("[P(Doom) RNG] Hyper-verbose debugging enabled for community analysis!")
        print(f"[P(Doom) RNG] Current seed: {deterministic_rng.base_seed}")
        print(f"[P(Doom) RNG] Total RNG calls so far: {len(deterministic_rng.call_history)}")


def get_challenge_export() -> Optional[Dict[str, Any]]:
    """Export current game as community challenge."""
    if deterministic_rng is None:
        return None
    
    return {
        'challenge_info': deterministic_rng.get_challenge_info(),
        'debug_info': deterministic_rng.get_debug_info(),
        'call_history': deterministic_rng.export_call_history()[-50:]  # Last 50 calls for size
    }
