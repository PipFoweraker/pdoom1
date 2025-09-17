"""
Research Quality System for P(Doom) - Technical Debt vs. Speed Trade-offs

This module implements the research quality mechanics where players choose between
fast/risky approaches and slow/safe approaches for research projects, with long-term
consequences through technical debt accumulation.

Key Components:
- ResearchProject: Individual research projects with quality level selection
- TechnicalDebt: Tracks accumulated shortcuts and their consequences
- QualityModifiers: Calculate effects of different research approaches
- DebtReduction: Mechanisms for paying down technical debt

The system provides strategic choices between short-term speed and long-term stability,
with escalating consequences for accumulated technical debt.
"""

from src.services.deterministic_rng import get_rng
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class ResearchQuality(Enum):
    """
    Research quality levels with different time/cost/risk trade-offs.
    
    RUSHED: Fast and cheap but risky, increases technical debt
    STANDARD: Balanced approach with baseline metrics
    THOROUGH: Slow and expensive but safe, reduces technical debt
    """
    RUSHED = "rushed"
    STANDARD = "standard"
    THOROUGH = "thorough"


class DebtCategory(Enum):
    """
    Categories of technical debt that can accumulate.
    
    Different categories represent different types of shortcuts taken
    during development, each with specific consequences.
    """
    SAFETY_TESTING = "safety_testing"
    CODE_QUALITY = "code_quality"
    DOCUMENTATION = "documentation"
    VALIDATION = "validation"


@dataclass
class QualityModifiers:
    """
    Modifiers applied based on research quality level.
    
    These modifiers affect the outcome of research projects based on
    the chosen quality approach.
    
    Attributes:
        duration_multiplier: Time factor (0.6 = 40% faster, 1.6 = 60% slower)
        cost_multiplier: Cost factor (0.8 = 20% cheaper, 1.4 = 40% more expensive)
        doom_modifier: Doom change modifier (15 = +15% doom, -20 = -20% doom)
        debt_change: Technical debt points added/removed
        success_rate_modifier: Success chance modifier (-10 = -10%, +15 = +15%)
        reputation_bonus: Extra reputation for thorough work
    """
    duration_multiplier: float
    cost_multiplier: float
    doom_modifier: int  # Percentage change to doom impact
    debt_change: int
    success_rate_modifier: int  # Percentage points
    reputation_bonus: int = 0


# Quality level configurations based on the issue specification
QUALITY_MODIFIERS = {
    ResearchQuality.RUSHED: QualityModifiers(
        duration_multiplier=0.6,  # -40% time
        cost_multiplier=0.8,      # -20% cost
        doom_modifier=15,         # +15% doom
        debt_change=2,            # +2 debt points
        success_rate_modifier=-10, # -10% success rate
        reputation_bonus=0
    ),
    ResearchQuality.STANDARD: QualityModifiers(
        duration_multiplier=1.0,  # Base time
        cost_multiplier=1.0,      # Base cost
        doom_modifier=0,          # Base doom
        debt_change=0,            # No debt change
        success_rate_modifier=0,  # Base success rate
        reputation_bonus=0
    ),
    ResearchQuality.THOROUGH: QualityModifiers(
        duration_multiplier=1.6,  # +60% time
        cost_multiplier=1.4,      # +40% cost
        doom_modifier=-20,        # -20% doom
        debt_change=-1,           # -1 debt point (pays down debt)
        success_rate_modifier=15, # +15% success rate
        reputation_bonus=1        # Bonus reputation for thorough work
    )
}


class ResearchProject:
    """
    Represents a research project with configurable quality approach.
    
    Research projects can be executed with different quality levels,
    each affecting time, cost, risk, and technical debt accumulation.
    
    Attributes:
        name: Project name/identifier
        base_cost: Base monetary cost before quality modifiers
        base_duration: Base time cost before quality modifiers
        quality_level: Current quality approach (rushed/standard/thorough)
        technical_debt: Debt accumulated from this project
        safety_verification: Whether extra safety testing was performed
        completed: Whether the project has been completed
    """
    
    def __init__(self, name: str, base_cost: int, base_duration: int):
        """
        Initialize a new research project.
        
        Args:
            name: Project identifier/name
            base_cost: Base monetary cost in game currency
            base_duration: Base time cost in turns/action points
        """
        self.name = name
        self.base_cost = base_cost
        self.base_duration = base_duration
        self.quality_level = ResearchQuality.STANDARD
        self.technical_debt = 0
        self.safety_verification = False
        self.completed = False
    
    def set_quality_level(self, quality: ResearchQuality) -> None:
        """Set the quality approach for this project."""
        self.quality_level = quality
        if quality == ResearchQuality.THOROUGH:
            self.safety_verification = True
    
    def get_modified_cost(self) -> int:
        """Calculate actual cost after quality modifiers."""
        modifiers = QUALITY_MODIFIERS[self.quality_level]
        return int(self.base_cost * modifiers.cost_multiplier)
    
    def get_modified_duration(self) -> int:
        """Calculate actual duration after quality modifiers."""
        modifiers = QUALITY_MODIFIERS[self.quality_level]
        return max(1, int(self.base_duration * modifiers.duration_multiplier))
    
    def get_quality_modifiers(self) -> QualityModifiers:
        """Get the modifiers for the current quality level."""
        return QUALITY_MODIFIERS[self.quality_level]


class TechnicalDebt:
    """
    Tracks accumulated technical debt and its consequences.
    
    Technical debt accumulates from taking shortcuts in research and development.
    Different categories of debt have different sources and consequences.
    As debt accumulates, it creates penalties to research speed and increases
    the chance of accidents and system failures.
    
    Debt Level Consequences (from issue specification):
    - 0-5: No penalties
    - 6-10: -5% research speed
    - 11-15: -10% research speed, +5% accident chance
    - 16-20: -15% research speed, +10% accident chance, reputation risk
    - 20+: Major system failure events become possible
    """
    
    def __init__(self):
        """Initialize technical debt tracking."""
        self.accumulated_debt = 0
        self.debt_categories = {
            DebtCategory.SAFETY_TESTING: 0,
            DebtCategory.CODE_QUALITY: 0,
            DebtCategory.DOCUMENTATION: 0,
            DebtCategory.VALIDATION: 0
        }
    
    def add_debt(self, amount: int, category: Optional[DebtCategory] = None) -> None:
        """
        Add technical debt to the total and optionally to a specific category.
        
        Args:
            amount: Debt points to add
            category: Optional specific category to add debt to
        """
        self.accumulated_debt += amount
        
        if category:
            self.debt_categories[category] += amount
        else:
            # Distribute among categories if no specific category given
            categories = list(self.debt_categories.keys())
            for _ in range(amount):
                cat = get_rng().choice(categories)
                self.debt_categories[cat] += 1
    
    def reduce_debt(self, amount: int, category: Optional[DebtCategory] = None) -> int:
        """
        Reduce technical debt and return actual amount reduced.
        
        Args:
            amount: Maximum debt points to reduce
            category: Optional specific category to reduce debt from
            
        Returns:
            Actual amount of debt reduced
        """
        if category and category in self.debt_categories:
            category_debt = self.debt_categories[category]
            reduction = min(amount, category_debt)
            self.debt_categories[category] -= reduction
            self.accumulated_debt -= reduction
            return reduction
        else:
            # Reduce from total and distribute across categories
            actual_reduction = min(amount, self.accumulated_debt)
            remaining = actual_reduction
            
            # Reduce from categories with highest debt first
            sorted_categories = sorted(
                self.debt_categories.items(),
                key=lambda x: x[1],
                reverse=True
            )
            
            for category, debt in sorted_categories:
                if remaining <= 0:
                    break
                reduction = min(remaining, debt)
                self.debt_categories[category] -= reduction
                remaining -= reduction
            
            self.accumulated_debt -= actual_reduction
            return actual_reduction
    
    def get_research_speed_penalty(self) -> float:
        """
        Calculate research speed penalty based on accumulated debt.
        
        Returns:
            Multiplier for research speed (0.85 = 15% slower)
        """
        if self.accumulated_debt <= 5:
            return 1.0
        elif self.accumulated_debt <= 10:
            return 0.95  # -5% speed
        elif self.accumulated_debt <= 15:
            return 0.90  # -10% speed
        elif self.accumulated_debt <= 20:
            return 0.85  # -15% speed
        else:
            return 0.80  # -20% speed for very high debt
    
    def get_accident_chance(self) -> float:
        """
        Calculate chance of accidents based on accumulated debt.
        
        Returns:
            Probability of accidents (0.1 = 10% chance)
        """
        if self.accumulated_debt <= 10:
            return 0.0
        elif self.accumulated_debt <= 15:
            return 0.05  # 5% accident chance
        elif self.accumulated_debt <= 20:
            return 0.10  # 10% accident chance
        else:
            return 0.15  # 15% accident chance for very high debt
    
    def has_reputation_risk(self) -> bool:
        """Check if debt level creates reputation risk."""
        return self.accumulated_debt >= 16
    
    def can_trigger_system_failure(self) -> bool:
        """Check if debt level can trigger major system failure events."""
        return self.accumulated_debt > 20
    
    def get_debt_summary(self) -> Dict[str, int]:
        """Get a summary of debt by category for display."""
        return {
            "total": self.accumulated_debt,
            "safety_testing": self.debt_categories[DebtCategory.SAFETY_TESTING],
            "code_quality": self.debt_categories[DebtCategory.CODE_QUALITY],
            "documentation": self.debt_categories[DebtCategory.DOCUMENTATION],
            "validation": self.debt_categories[DebtCategory.VALIDATION]
        }


def calculate_research_outcome(
    base_doom_reduction: int,
    base_reputation_gain: int,
    quality: ResearchQuality,
    technical_debt: TechnicalDebt
) -> Tuple[int, int, int, List[str]]:
    """
    Calculate the outcome of a research project based on quality and debt.
    
    This function applies quality modifiers and technical debt penalties
    to determine the actual effects of research actions.
    
    Args:
        base_doom_reduction: Base doom reduction before modifiers
        base_reputation_gain: Base reputation gain before modifiers
        quality: Research quality level chosen
        technical_debt: Current technical debt state
        
    Returns:
        Tuple of (doom_change, reputation_change, debt_change, messages)
    """
    modifiers = QUALITY_MODIFIERS[quality]
    messages = []
    
    # Apply quality modifiers to doom reduction
    # For rushed research: +15% doom means LESS effective at reducing doom
    # For thorough research: -20% doom means MORE effective at reducing doom
    if modifiers.doom_modifier > 0:
        # Positive doom modifier means research is less effective (reduces doom reduction)
        doom_modifier = 1.0 - (modifiers.doom_modifier / 100.0)
    else:
        # Negative doom modifier means research is more effective (increases doom reduction) 
        doom_modifier = 1.0 + (abs(modifiers.doom_modifier) / 100.0)
    
    actual_doom_reduction = int(base_doom_reduction * doom_modifier)
    
    # Apply technical debt penalty to research effectiveness
    debt_penalty = technical_debt.get_research_speed_penalty()
    actual_doom_reduction = int(actual_doom_reduction * debt_penalty)
    
    # Calculate reputation gain with quality bonus
    actual_reputation_gain = base_reputation_gain + modifiers.reputation_bonus
    
    # Apply debt penalty to reputation gain too
    actual_reputation_gain = int(actual_reputation_gain * debt_penalty)
    
    # Technical debt change
    debt_change = modifiers.debt_change
    
    # Add quality-specific messages
    if quality == ResearchQuality.RUSHED:
        messages.append("[LIGHTNING] Rushed research completed quickly but with shortcuts")
    elif quality == ResearchQuality.THOROUGH:
        messages.append("? Thorough research completed with extra safety verification")
    
    # Add debt penalty messages if applicable
    if debt_penalty < 1.0:
        penalty_percent = int((1.0 - debt_penalty) * 100)
        messages.append(f"[WARNING]? Technical debt reduced research effectiveness by {penalty_percent}%")
    
    return actual_doom_reduction, actual_reputation_gain, debt_change, messages


def get_debt_reduction_actions() -> List[Dict]:
    """
    Get available technical debt reduction actions.
    
    Returns:
        List of action dictionaries for debt reduction options
    """
    return [
        {
            "name": "Refactoring Sprint",
            "desc": "Major code cleanup and improvement. Costs 1 turn + $100k, reduces debt by 3-5 points.",
            "cost": 100,  # $100k in game units
            "ap_cost": 2,  # Takes significant time
            "debt_reduction": (3, 5),  # Range of debt reduction
            "requires_staff": True,
            "staff_type": "research_staff",
            "min_staff": 2
        },
        {
            "name": "Safety Audit", 
            "desc": "Comprehensive safety review. Costs $200k, reduces debt by 2 points, +reputation.",
            "cost": 200,  # $200k in game units
            "ap_cost": 1,
            "debt_reduction": (2, 2),  # Fixed reduction
            "reputation_bonus": 1,
            "requires_staff": False
        },
        {
            "name": "Code Review",
            "desc": "Peer review process. Costs $50k per researcher, reduces debt by 1 point per researcher.",
            "cost_per_researcher": 50,  # $50k per researcher
            "ap_cost": 1,
            "debt_reduction_per_researcher": 1,
            "requires_staff": True,
            "staff_type": "research_staff",
            "min_staff": 1
        }
    ]