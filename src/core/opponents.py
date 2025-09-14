import random
from typing import Dict, List, Optional, Tuple, Union, Any
from src.services.deterministic_rng import get_rng

class Opponent:
    """
    Represents a competing AI lab/organization that the player is racing against.
    Each opponent has hidden stats that can be discovered through espionage.
    """
    
    def __init__(self, name: str, budget: int, capabilities_researchers: int, lobbyists: int, compute: int, description: str = "") -> None:
        """
        Initialize an opponent with hidden stats.
        
        Args:
            name (str): Display name of the opponent organization
            budget (int): Available funding for the opponent
            capabilities_researchers (int): Number of researchers working on capabilities
            lobbyists (int): Number of lobbyists influencing policy
            compute (int): Available compute resources
            description (str): Optional description of the opponent
        """
        self.name: str = name
        self.budget: int = budget
        self.capabilities_researchers: int = capabilities_researchers
        self.lobbyists: int = lobbyists
        self.compute: int = compute
        self.description: str = description
        
        # Progress toward deploying dangerous AGI (0-100)
        self.progress: int = random.randint(15, 40)
        
        # Track what stats have been discovered by the player
        self.discovered_stats: Dict[str, bool] = {
            'budget': False,
            'capabilities_researchers': False,
            'lobbyists': False,
            'compute': False,
            'progress': False
        }
        
        # Track known values (what the player thinks they are)
        self.known_stats: Dict[str, Optional[int]] = {
            'budget': None,
            'capabilities_researchers': None,
            'lobbyists': None,
            'compute': None,
            'progress': None
        }
        
        # Whether this opponent has been discovered at all
        self.discovered: bool = False
        
        # Research Quality System - Risk tolerance profile
        # Each opponent has different approaches to the speed vs safety trade-off
        self.risk_tolerance: str = "moderate"  # Default, will be overridden per opponent
        self.technical_debt: int = 0  # Track opponent's accumulated shortcuts
        self.research_quality_preference: str = "standard"  # Default research approach
        
    def scout_stat(self, stat_name: str) -> Tuple[bool, Optional[int], str]:
        """
        Attempt to scout a specific stat of this opponent.
        Returns tuple (success, revealed_value, message)
        """
        if stat_name not in self.discovered_stats:
            return False, None, f"Unknown stat: {stat_name}"
            
        if self.discovered_stats[stat_name]:
            # Already discovered, return known value
            actual_value = getattr(self, stat_name)
            return True, actual_value, f"{self.name}'s {stat_name}: {actual_value} (already known)"
            
        # Attempt to discover the stat (70% success rate)
        if random.random() < 0.7:
            self.discovered_stats[stat_name] = True
            actual_value = getattr(self, stat_name)
            # Add some noise to the discovered value
            if stat_name == 'progress':
                noise = random.randint(-3, 3)
                revealed_value = max(0, min(100, actual_value + noise))
            else:
                noise = random.randint(-2, 2)
                revealed_value = max(0, actual_value + noise)
                
            self.known_stats[stat_name] = revealed_value
            return True, revealed_value, f"Discovered {self.name}'s {stat_name}: {revealed_value}"
        else:
            return False, None, f"Failed to scout {self.name}'s {stat_name}"
            
    def discover(self) -> None:
        """Mark this opponent as discovered by the player."""
        self.discovered = True
        
    def take_turn(self) -> List[str]:
        """
        Execute the opponent's AI behavior for one turn.
        Returns a list of messages describing what the opponent did.
        """
        messages = []
        
        if not self.discovered:
            # Undiscovered opponents act in secret
            return []
            
        # Simple AI logic: spend budget on various activities
        if self.budget > 0:
            # Prioritize capabilities research if low on progress
            if self.progress < 60 and self.budget >= 50:
                spent = min(50, self.budget)
                self.budget -= spent
                progress_gain = random.randint(3, 8)
                self.progress = min(100, self.progress + progress_gain)
                messages.append(f"{self.name} invested ${spent}k in capabilities research (+{progress_gain} progress)")
                
            # Hire more researchers if budget allows
            elif self.budget >= 80 and self.capabilities_researchers < 20:
                self.budget -= 80
                new_researchers = random.randint(1, 3)
                self.capabilities_researchers += new_researchers
                messages.append(f"{self.name} hired {new_researchers} new researchers")
                
            # Buy compute if needed
            elif self.budget >= 60 and self.compute < 50:
                self.budget -= 60
                new_compute = random.randint(15, 25)
                self.compute += new_compute
                messages.append(f"{self.name} purchased {new_compute} compute units")
                
            # Lobbying efforts
            elif self.budget >= 40 and self.lobbyists < 10:
                self.budget -= 40
                new_lobbyists = random.randint(1, 2)
                self.lobbyists += new_lobbyists
                messages.append(f"{self.name} hired {new_lobbyists} lobbyists")
                
        # Research Quality System - Opponent research approach decisions
        # Each opponent makes quality vs speed trade-offs based on their risk tolerance
        self._choose_research_approach(messages)
        
        # Research progress based on resources and research quality approach
        base_progress = self.capabilities_researchers * 0.5
        compute_bonus = min(self.compute * 0.1, 5)  # Cap compute bonus
        
        # Apply research quality modifiers based on opponent's approach
        quality_modifier = self._get_research_quality_modifier()
        effective_progress = (base_progress + compute_bonus) * quality_modifier
        
        # Apply technical debt penalties (opponents also suffer from shortcuts)
        debt_penalty = max(0.8, 1.0 - (self.technical_debt * 0.02))  # 2% penalty per debt point
        final_progress = effective_progress * debt_penalty
        
        if final_progress > 0:
            actual_gain = random.randint(int(final_progress * 0.5), int(final_progress * 1.5))
            self.progress = min(100, self.progress + actual_gain)
            if actual_gain > 0:
                quality_suffix = f" [{self.research_quality_preference}]" if self.research_quality_preference != "standard" else ""
                messages.append(f"{self.name} made research progress (+{actual_gain}, total: {self.progress}/100){quality_suffix}")
                
        return messages
    
    def _choose_research_approach(self, messages: List[str]) -> None:
        """
        Choose research approach based on risk tolerance and current situation.
        Updates research_quality_preference and may accumulate technical debt.
        """
        # Decision factors
        time_pressure = self.progress < 50  # Behind in the race
        budget_pressure = self.budget < 200  # Low on funds
        
        if self.risk_tolerance == "aggressive":
            # TechCorp: Always rushes, accumulates debt quickly
            if random.random() < 0.8:  # 80% chance to rush
                if self.research_quality_preference != "rushed":
                    self.research_quality_preference = "rushed"
                    messages.append(f"{self.name} adopts aggressive research approach")
                
                # Accumulate technical debt from rushing
                if random.random() < 0.6:  # 60% chance per turn
                    self.technical_debt += random.randint(1, 3)
                    
        elif self.risk_tolerance == "conservative":
            # Government Lab: Prefers thorough, builds sustainable foundation
            if random.random() < 0.7:  # 70% chance to be thorough
                if self.research_quality_preference != "thorough":
                    self.research_quality_preference = "thorough"
                    messages.append(f"{self.name} emphasizes research quality and safety")
                
                # Reduce technical debt with thorough approach
                if self.technical_debt > 0 and random.random() < 0.4:  # 40% chance
                    self.technical_debt = max(0, self.technical_debt - random.randint(1, 2))
                    
        else:  # moderate risk tolerance
            # Frontier Dynamics: Adapts based on situation
            if time_pressure or budget_pressure:
                if self.research_quality_preference != "rushed":
                    self.research_quality_preference = "rushed"
                    messages.append(f"{self.name} accelerates research due to competitive pressure")
                    
                # Moderate debt accumulation
                if random.random() < 0.3:  # 30% chance
                    self.technical_debt += random.randint(1, 2)
            else:
                if self.research_quality_preference != "standard":
                    self.research_quality_preference = "standard"
                    messages.append(f"{self.name} maintains balanced research approach")
    
    def _get_research_quality_modifier(self) -> float:
        """Get research speed modifier based on current research approach."""
        modifiers = {
            "rushed": 1.3,      # 30% faster but accumulates debt
            "standard": 1.0,    # Baseline speed
            "thorough": 0.8     # 20% slower but reduces debt
        }
        return modifiers.get(self.research_quality_preference, 1.0)
        
    def get_impact_on_doom(self) -> int:
        """
        Calculate how much this opponent's capabilities research increases global doom.
        Called during turn processing to add doom pressure.
        Factors in technical debt from rushed research approaches.
        """
        if not self.discovered:
            # Undiscovered opponents still contribute to doom, but less visibly
            return random.randint(0, 2)
            
        # Discovered opponents' doom impact is based on their capabilities research
        base_doom = self.capabilities_researchers * 0.2
        progress_multiplier = 1 + (self.progress / 100)  # More dangerous as they get closer
        
        # Technical debt increases doom risk (shortcuts lead to unsafe AGI)
        debt_multiplier = 1 + (self.technical_debt * 0.05)  # 5% more doom per debt point
        
        return int(base_doom * progress_multiplier * debt_multiplier)


def create_default_opponents() -> List[Opponent]:
    """
    Create the default set of 3 opponents for the game.
    Returns a list of Opponent objects with varied stats and personalities.
    """
    opponents = []
    
    # Opponent 1: TechCorp - High technical debt, fast progress (aggressive)
    techcorp = Opponent(
        name="TechCorp Labs",
        budget=random.randint(800, 1200),
        capabilities_researchers=random.randint(15, 25),
        lobbyists=random.randint(8, 12),
        compute=random.randint(60, 100),
        description="A massive tech corporation with deep pockets and aggressive timelines"
    )
    techcorp.risk_tolerance = "aggressive"
    techcorp.research_quality_preference = "rushed"
    techcorp.technical_debt = random.randint(5, 15)  # Start with existing debt
    opponents.append(techcorp)
    
    # Opponent 2: Government Lab - Low technical debt, slow but steady (conservative)
    gov_lab = Opponent(
        name="National AI Initiative",
        budget=random.randint(600, 900),
        capabilities_researchers=random.randint(12, 20),
        lobbyists=random.randint(15, 20),
        compute=random.randint(40, 80),
        description="Government-funded program with strong regulatory influence"
    )
    gov_lab.risk_tolerance = "conservative"
    gov_lab.research_quality_preference = "thorough"
    gov_lab.technical_debt = random.randint(0, 3)  # Very low debt
    opponents.append(gov_lab)
    
    # Opponent 3: Frontier Dynamics - Moderate debt, unpredictable (moderate)
    frontier = Opponent(
        name="Frontier Dynamics",
        budget=random.randint(400, 800),
        capabilities_researchers=random.randint(8, 15),
        lobbyists=random.randint(2, 6),
        compute=random.randint(20, 60),
        description="Secretive startup with mysterious funding and rapid development"
    )
    frontier.risk_tolerance = "moderate"
    frontier.research_quality_preference = "standard"
    frontier.technical_debt = random.randint(2, 8)  # Moderate debt
    opponents.append(frontier)
    
    # Opponent 4: Palandir - Advanced surveillance corporation (aggressive but well-funded)
    palandir = Opponent(
        name="Palandir",
        budget=random.randint(1000, 1500),
        capabilities_researchers=random.randint(20, 30),
        lobbyists=random.randint(12, 18),
        compute=random.randint(80, 120),
        description="Advanced surveillance technology corporation with global data monitoring capabilities"
    )
    palandir.risk_tolerance = "aggressive"
    palandir.research_quality_preference = "rushed"
    palandir.technical_debt = random.randint(8, 20)  # High debt from aggressive approach
    opponents.append(palandir)
    
    return opponents