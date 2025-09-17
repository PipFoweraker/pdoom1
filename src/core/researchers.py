# Enhanced Personnel System with Specialist Researchers
# Implements individual researchers with specializations, traits, and management mechanics

from src.services.deterministic_rng import get_rng
from typing import List, Dict, Any

# Specialization definitions
SPECIALIZATIONS = {
    "safety": {
        "name": "AI Safety",
        "description": "Focuses on reducing doom risk and ensuring safe AI development",
        "doom_reduction_bonus": 0.15,  # 15% doom reduction per research point
        "research_speed_modifier": 1.0,
        "doom_per_research": 0.0
    },
    "capabilities": {
        "name": "AI Capabilities", 
        "description": "Develops advanced AI capabilities and performance improvements",
        "doom_reduction_bonus": 0.0,
        "research_speed_modifier": 1.25,  # 25% faster research
        "doom_per_research": 0.05  # 5% doom increase per research point
    },
    "interpretability": {
        "name": "AI Interpretability",
        "description": "Makes AI systems more transparent and understandable",
        "doom_reduction_bonus": 0.0,
        "research_speed_modifier": 1.0,
        "doom_per_research": 0.0,
        "special_actions": ["audit_competitor"]  # Unlock special actions
    },
    "alignment": {
        "name": "AI Alignment",
        "description": "Ensures AI systems remain aligned with human values",
        "doom_reduction_bonus": 0.0,
        "research_speed_modifier": 1.0,
        "doom_per_research": 0.0,
        "negative_event_reduction": 0.10  # 10% reduction in negative event probability
    }
}

# Trait definitions
POSITIVE_TRAITS = {
    "workaholic": {
        "name": "Workaholic",
        "description": "Works extra hours but burns out faster",
        "productivity_bonus": 0.20,
        "burnout_increase": 2
    },
    "team_player": {
        "name": "Team Player", 
        "description": "Boosts productivity of all researchers when present",
        "team_productivity_bonus": 0.10,
        "productivity_bonus": 0.0
    },
    "media_savvy": {
        "name": "Media Savvy",
        "description": "Generates additional reputation when publishing papers",
        "reputation_bonus": 1,
        "productivity_bonus": 0.0
    },
    "safety_conscious": {
        "name": "Safety Conscious",
        "description": "Reduces doom risk from their research contributions",
        "doom_reduction": 0.10,
        "productivity_bonus": 0.0
    }
}

NEGATIVE_TRAITS = {
    "prima_donna": {
        "name": "Prima Donna",
        "description": "Reduces team productivity if salary expectations aren't met",
        "team_productivity_penalty": 0.10,
        "salary_sensitivity": True
    },
    "leak_prone": {
        "name": "Leak Prone", 
        "description": "5% chance per turn to leak research to competitors",
        "leak_chance": 0.05
    },
    "burnout_prone": {
        "name": "Burnout Prone",
        "description": "Accumulates burnout 50% faster than normal",
        "burnout_multiplier": 1.5
    }
}

class Researcher:
    """Individual researcher with specialization, traits, and management needs."""
    
    def __init__(self, name: str, specialization: str, skill_level: int = None, 
                 traits: List[str] = None, salary_expectation: int = None):
        # Generate unique ID based on name and random suffix for tracking
        import uuid
        self.id = f"{name.replace(' ', '_').lower()}_{str(uuid.uuid4())[:8]}"
        self.name = name
        self.specialization = specialization
        self.skill_level = skill_level if skill_level is not None else get_rng().randint(3, 8)
        self.traits = traits if traits is not None else []
        self.salary_expectation = salary_expectation if salary_expectation is not None else get_rng().randint(70, 120)
        
        # Management attributes
        self.current_salary = self.salary_expectation
        self.productivity = 1.0  # Base productivity multiplier
        self.loyalty = 50  # 0-100, affects poaching resistance
        self.burnout = 0   # 0-100, reduces productivity when high
        self.turns_employed = 0
        
        # Apply trait effects
        self._apply_trait_effects()
    
    def _apply_trait_effects(self):
        """Apply initial trait effects to researcher attributes."""
        for trait_name in self.traits:
            if trait_name in POSITIVE_TRAITS:
                trait = POSITIVE_TRAITS[trait_name]
                if "productivity_bonus" in trait:
                    self.productivity += trait["productivity_bonus"]
            elif trait_name in NEGATIVE_TRAITS:
                trait = NEGATIVE_TRAITS[trait_name]
                # Negative traits are applied dynamically during gameplay
    
    def get_effective_productivity(self) -> float:
        """Calculate current productivity considering burnout and other factors."""
        # Base productivity modified by traits
        effective = self.productivity
        
        # Burnout reduces productivity
        if self.burnout > 0:
            burnout_penalty = min(self.burnout / 100.0 * 0.5, 0.5)  # Max 50% penalty
            effective *= (1.0 - burnout_penalty)
        
        # Salary satisfaction affects productivity
        if "prima_donna" in self.traits:
            if self.current_salary < self.salary_expectation:
                effective *= 0.8  # 20% penalty for unsatisfied prima donna
        
        return max(effective, 0.1)  # Minimum 10% productivity
    
    def get_specialization_effects(self) -> Dict[str, float]:
        """Get the effects this researcher's specialization provides."""
        if self.specialization not in SPECIALIZATIONS:
            return {}
        
        spec = SPECIALIZATIONS[self.specialization]
        effects = {}
        
        # Apply skill level scaling
        skill_multiplier = self.skill_level / 5.0  # Scale around skill level 5
        
        if "doom_reduction_bonus" in spec and spec["doom_reduction_bonus"] > 0:
            effects["doom_reduction_bonus"] = spec["doom_reduction_bonus"] * skill_multiplier
        
        if "research_speed_modifier" in spec:
            base_modifier = spec["research_speed_modifier"] - 1.0  # Get bonus portion
            effects["research_speed_modifier"] = 1.0 + (base_modifier * skill_multiplier)
        
        if "doom_per_research" in spec and spec["doom_per_research"] > 0:
            effects["doom_per_research"] = spec["doom_per_research"] * skill_multiplier
        
        if "negative_event_reduction" in spec:
            effects["negative_event_reduction"] = spec["negative_event_reduction"] * skill_multiplier
        
        return effects
    
    def advance_turn(self):
        """Advance researcher state by one turn."""
        self.turns_employed += 1
        
        # Apply burnout from traits
        burnout_increase = 1  # Base burnout per turn
        
        for trait_name in self.traits:
            if trait_name == "workaholic":
                burnout_increase += POSITIVE_TRAITS[trait_name]["burnout_increase"]
            elif trait_name == "burnout_prone":
                burnout_increase *= NEGATIVE_TRAITS[trait_name]["burnout_multiplier"]
        
        self.burnout = min(self.burnout + burnout_increase, 100)
        
        # Loyalty naturally decays slightly
        self.loyalty = max(self.loyalty - 1, 0)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert researcher to dictionary for serialization."""
        return {
            "id": self.id,
            "name": self.name,
            "specialization": self.specialization,
            "skill_level": self.skill_level,
            "traits": self.traits,
            "salary_expectation": self.salary_expectation,
            "current_salary": self.current_salary,
            "productivity": self.productivity,
            "loyalty": self.loyalty,
            "burnout": self.burnout,
            "turns_employed": self.turns_employed
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Researcher':
        """Create researcher from dictionary."""
        researcher = cls(
            data["name"],
            data["specialization"], 
            data["skill_level"],
            data["traits"],
            data["salary_expectation"]
        )
        # Override the generated ID with saved ID for consistency
        if "id" in data:
            researcher.id = data["id"]
        researcher.current_salary = data.get("current_salary", researcher.salary_expectation)
        researcher.productivity = data.get("productivity", 1.0)
        researcher.loyalty = data.get("loyalty", 50)
        researcher.burnout = data.get("burnout", 0)
        researcher.turns_employed = data.get("turns_employed", 0)
        return researcher

# Researcher generation functions
def generate_researcher_name() -> str:
    """Generate a random researcher name."""
    first_names = [
        "Alex", "Jordan", "Casey", "Riley", "Avery", "Morgan", "Blake", "Quinn",
        "Cameron", "Sage", "Emery", "Rowan", "Phoenix", "River", "Sky", "Indigo",
        "Adrian", "Elena", "Marcus", "Sophia", "David", "Maya", "James", "Aria",
        "Lucas", "Zoe", "Nathan", "Iris", "Samuel", "Luna", "Gabriel", "Nova"
    ]
    
    last_names = [
        "Chen", "Patel", "Garcia", "Johnson", "Williams", "Brown", "Davis", "Miller",
        "Wilson", "Moore", "Taylor", "Anderson", "Thomas", "Jackson", "White", "Harris",
        "Martin", "Thompson", "Rodriguez", "Lewis", "Lee", "Walker", "Hall", "Allen",
        "Kim", "Singh", "Martinez", "Clark", "Lopez", "Gonzalez", "Young", "King"
    ]
    
    return f"{get_rng().choice(first_names)} {get_rng().choice(last_names)}"

def generate_random_traits(num_traits: int = None) -> List[str]:
    """Generate random traits for a researcher."""
    if num_traits is None:
        num_traits = get_rng().choices([0, 1, 2], weights=[40, 45, 15])[0]  # Mostly 0-1 traits
    
    if num_traits == 0:
        return []
    
    all_traits = list(POSITIVE_TRAITS.keys()) + list(NEGATIVE_TRAITS.keys())
    return get_rng().sample(all_traits, min(num_traits, len(all_traits)))

def generate_researcher(specialization: str = None) -> Researcher:
    """Generate a random researcher with given or random specialization."""
    if specialization is None:
        specialization = get_rng().choice(list(SPECIALIZATIONS.keys()))
    
    name = generate_researcher_name()
    skill_level = get_rng().randint(3, 8)
    traits = generate_random_traits()
    salary_expectation = get_rng().randint(70, 120)
    
    return Researcher(name, specialization, skill_level, traits, salary_expectation)

# Management action functions
def adjust_researcher_salary(researcher: Researcher, new_salary: int) -> Dict[str, Any]:
    """Adjust researcher salary and return effects."""
    old_salary = researcher.current_salary
    researcher.current_salary = new_salary
    
    # Calculate loyalty change
    if new_salary > old_salary:
        loyalty_change = min((new_salary - old_salary) // 5, 20)  # Up to +20 loyalty
        researcher.loyalty = min(researcher.loyalty + loyalty_change, 100)
        message = f"{researcher.name}'s salary increased to ${new_salary}. Loyalty increased by {loyalty_change}."
    elif new_salary < old_salary:
        loyalty_change = max((new_salary - old_salary) // 3, -30)  # Up to -30 loyalty  
        researcher.loyalty = max(researcher.loyalty + loyalty_change, 0)
        message = f"{researcher.name}'s salary reduced to ${new_salary}. Loyalty decreased by {abs(loyalty_change)}."
    else:
        message = f"{researcher.name}'s salary maintained at ${new_salary}."
    
    return {
        "success": True,
        "message": message,
        "loyalty_change": researcher.loyalty - (researcher.loyalty - (new_salary - old_salary) // 5 if new_salary > old_salary else researcher.loyalty - abs((new_salary - old_salary) // 3))
    }

def conduct_team_building(researchers: List[Researcher], cost: int) -> Dict[str, Any]:
    """Conduct team building activity to reduce burnout and improve cohesion."""
    if not researchers:
        return {"success": False, "message": "No researchers available for team building."}
    
    # Reduce burnout for all researchers
    burnout_reduction = min(15 + (cost // 10), 30)  # 15-30 burnout reduction based on cost
    affected_researchers = []
    
    for researcher in researchers:
        if researcher.burnout > 0:
            old_burnout = researcher.burnout
            researcher.burnout = max(researcher.burnout - burnout_reduction, 0)
            affected_researchers.append(f"{researcher.name} (-{old_burnout - researcher.burnout} burnout)")
    
    if affected_researchers:
        message = f"Team building reduced burnout: {', '.join(affected_researchers)}"
    else:
        message = "Team building completed, but no researchers had significant burnout."
    
    return {
        "success": True,
        "message": message,
        "burnout_reduction": burnout_reduction,
        "cost": cost
    }

def conduct_performance_review(researcher: Researcher) -> Dict[str, Any]:
    """Conduct performance review for individual researcher."""
    # Generate performance insights
    insights = []
    
    productivity = researcher.get_effective_productivity()
    if productivity >= 1.2:
        insights.append("Exceptional performer - consider promotion opportunities")
    elif productivity <= 0.7:
        insights.append("Below expectations - may need additional support or training")
    
    if researcher.burnout > 60:
        insights.append("High burnout risk - recommend workload reduction or vacation")
    
    if researcher.loyalty < 30:
        insights.append("Low loyalty - at risk of leaving or being poached")
    
    if "workaholic" in researcher.traits and researcher.burnout > 40:
        insights.append("Workaholic trait causing burnout - monitor closely")
    
    if not insights:
        insights.append("Performance within normal parameters")
    
    return {
        "success": True,
        "researcher": researcher.name,
        "productivity": productivity,
        "burnout": researcher.burnout,
        "loyalty": researcher.loyalty,
        "insights": insights
    }