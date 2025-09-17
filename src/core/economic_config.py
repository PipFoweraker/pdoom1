# Economic Configuration System
# Provides configurable economic parameters for bootstrap AI safety lab model

import json
import os
from typing import Dict, Any, Tuple
from src.services.deterministic_rng import get_rng

class EconomicConfig:
    """
    Manages economic configuration and calibration for P(Doom) gameplay.
    
    Supports:
    - Configurable cost structures for all game systems
    - Historical compute cost reduction modeling
    - Deterministic fundraising with delayed payoffs
    - Bootstrap nonprofit economic model
    """
    
    def __init__(self, config_path: str = None):
        """Initialize economic configuration."""
        self.config_path = config_path or "configs/default.json"
        self.config = self._load_config()
        self.economic_config = self.config.get("economic_calibration", {})
        
        # Track historical compute cost reduction
        self.compute_cost_reduction_turns = 0
        
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from JSON file."""
        try:
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Warning: Could not load economic config from {self.config_path}: {e}")
            return {}
    
    def get_staff_maintenance_cost(self, staff_count: int) -> int:
        """
        Calculate weekly staff maintenance costs.
        
        Bootstrap model:
        - First employee: $600/week ($31k annually) 
        - Additional employees: $800/week each ($42k annually)
        - Reflects junior research assistant to researcher salary range
        """
        if staff_count == 0:
            return 0
        elif staff_count == 1:
            return self.economic_config.get("staff_maintenance", {}).get("first_employee_weekly", 600)
        else:
            first_cost = self.economic_config.get("staff_maintenance", {}).get("first_employee_weekly", 600)
            additional_cost = self.economic_config.get("staff_maintenance", {}).get("additional_employee_weekly", 800)
            return first_cost + (staff_count - 1) * additional_cost
    
    def get_hiring_cost(self, employee_type: str) -> int:
        """
        Get hiring costs for different employee types.
        
        Bootstrap model: No signing bonuses for nonprofit.
        All hiring costs are $0 (advertising/interview overhead absorbed).
        """
        hiring_costs = self.economic_config.get("hiring_costs", {})
        return hiring_costs.get(employee_type, 0)
    
    def get_research_cost(self, quality: str = "standard") -> int:
        """
        Get weekly research project costs based on quality.
        
        Base: $3k/week ($156k annually)
        Quality modifiers: rushed (80%), standard (100%), thorough (140%)
        """
        base_cost = self.economic_config.get("research_costs", {}).get("base_research_weekly", 3000)
        quality_modifier = self.economic_config.get("research_costs", {}).get("quality_modifiers", {}).get(quality, 1.0)
        return int(base_cost * quality_modifier)
    
    def get_compute_cost(self, flops_amount: int = 10) -> int:
        """
        Get compute costs with historical cost reduction modeling.
        
        Features Moore's Law simulation:
        - Base cost decreases 2% per turn (week)
        - Minimum cost floor to prevent zero-cost compute
        - Appeals to Kurzwelian technological optimism
        """
        compute_config = self.economic_config.get("compute_costs", {})
        base_cost = compute_config.get("base_cost_per_10_flops", 5000)
        
        # Apply historical cost reduction if enabled
        if compute_config.get("historical_cost_reduction", {}).get("enabled", True):
            reduction_per_turn = compute_config.get("historical_cost_reduction", {}).get("reduction_per_turn", 0.02)
            minimum_cost = compute_config.get("historical_cost_reduction", {}).get("minimum_cost", 1000)
            
            # Calculate cost with exponential reduction
            reduced_cost = base_cost * ((1 - reduction_per_turn) ** self.compute_cost_reduction_turns)
            final_cost = max(reduced_cost, minimum_cost)
        else:
            final_cost = base_cost
        
        # Scale for different flop amounts
        return int(final_cost * (flops_amount / 10))
    
    def advance_compute_cost_reduction(self):
        """Advance the historical compute cost reduction by one turn."""
        self.compute_cost_reduction_turns += 1
    
    def get_fundraising_amount_range(self, fundraising_type: str) -> Tuple[int, int]:
        """
        Get fundraising amount ranges for different types.
        
        Calibrated for bootstrap runway:
        - Small: $5-10k (covers 2-3 weeks with small team)
        - Big: $15-25k (provides 4-6 weeks runway)
        """
        fundraising_config = self.economic_config.get("fundraising_amounts", {})
        
        if fundraising_type == "small":
            return tuple(fundraising_config.get("small_range", [5000, 10000]))
        elif fundraising_type == "big":
            return tuple(fundraising_config.get("big_range", [15000, 25000]))
        else:
            return (8000, 15000)  # Default range
    
    def get_fundraising_success_probability(self, fundraising_type: str, reputation: int, seed: str) -> float:
        """
        Calculate deterministic fundraising success probability.
        
        Features:
        - Deterministic based on seed for strategy game consistency
        - Base success rate modified by reputation
        - Different probabilities for different fundraising types
        """
        success_config = self.economic_config.get("fundraising_amounts", {}).get("success_probability", {})
        
        if not success_config.get("deterministic_seed_based", True):
            # Fallback to simple probability if deterministic disabled
            base_rate = success_config.get("base_success_rate", 0.7)
            reputation_modifier = success_config.get("reputation_modifier", 0.02)
            return min(0.95, base_rate + (reputation * reputation_modifier))
        
        # Deterministic calculation based on seed
        seed_hash = hash(f"{seed}_{fundraising_type}_{reputation}")
        get_rng().seed(seed_hash)
        
        base_rate = success_config.get("base_success_rate", 0.7)
        reputation_modifier = success_config.get("reputation_modifier", 0.02)
        
        # Add some variation but keep it deterministic
        variation = (get_rng().random("random_context") - 0.5) * 0.2  # +/- 10% variation
        
        final_probability = base_rate + (reputation * reputation_modifier) + variation
        return max(0.1, min(0.95, final_probability))
    
    def get_fundraising_delay_turns(self, fundraising_type: str) -> int:
        """
        Get number of turns before fundraising pays off.
        
        Implements delayed gratification:
        - Small fundraising: 1 turn delay
        - Big fundraising: 2 turn delay  
        - Alternative funding: 3 turn delay
        """
        delay_config = self.economic_config.get("fundraising_amounts", {}).get("success_probability", {}).get("delay_turns", {})
        
        delays = {
            "small": delay_config.get("small", 1),
            "big": delay_config.get("big", 2), 
            "alternative": delay_config.get("alternative", 3),
            "borrow": 0  # Borrowing is immediate but creates debt
        }
        
        return delays.get(fundraising_type, 1)
    
    def get_intelligence_cost(self, action_type: str) -> int:
        """
        Get costs for intelligence gathering actions.
        
        Calibrated for bootstrap operations:
        - Espionage: $500 (minimal operational costs)
        - Scout opponents: $0 (free internet browsing/research)
        """
        intelligence_costs = self.economic_config.get("intelligence_costs", {})
        return intelligence_costs.get(action_type, 0)
    
    def get_technical_debt_cost(self, action_type: str) -> int:
        """
        Get costs for technical debt management actions.
        
        Bootstrap model:
        - Staff naturally reduce debt by 0.5 points per week
        - Refactoring sprint: $3k for focused effort
        - External safety audit: $12k (realistic professional audit cost)
        """
        debt_config = self.economic_config.get("technical_debt", {})
        return debt_config.get(action_type, 0)
    
    def get_staff_debt_reduction_rate(self) -> float:
        """Get how much technical debt staff naturally reduce per week."""
        return self.economic_config.get("technical_debt", {}).get("staff_debt_reduction_per_week", 0.5)
    
    def get_media_pr_cost(self, action_type: str) -> int:
        """
        Get costs for media and PR actions.
        
        Bootstrap model:
        - Press releases: $0 (self-published via social media/blog)
        - Social media campaigns: $0 (organic reach)
        - Damage control: $2k (real crisis management costs)
        """
        media_config = self.economic_config.get("media_pr", {})
        return media_config.get(action_type, 0)
    
    def get_config_summary(self) -> Dict[str, Any]:
        """Get a summary of current economic configuration for debugging."""
        return {
            "staff_maintenance_example": {
                "1_employee": self.get_staff_maintenance_cost(1),
                "5_employees": self.get_staff_maintenance_cost(5),
                "10_employees": self.get_staff_maintenance_cost(10)
            },
            "research_costs": {
                "rushed": self.get_research_cost("rushed"),
                "standard": self.get_research_cost("standard"), 
                "thorough": self.get_research_cost("thorough")
            },
            "compute_cost_current": self.get_compute_cost(10),
            "compute_cost_reduction_turns": self.compute_cost_reduction_turns,
            "fundraising_ranges": {
                "small": self.get_fundraising_amount_range("small"),
                "big": self.get_fundraising_amount_range("big")
            },
            "zero_cost_actions": {
                "hiring": "All hiring costs are $0",
                "scout_opponents": f"${self.get_intelligence_cost('scout_opponents')}",
                "press_release": f"${self.get_media_pr_cost('press_release')}",
                "social_media": f"${self.get_media_pr_cost('social_media_campaign')}"
            }
        }
