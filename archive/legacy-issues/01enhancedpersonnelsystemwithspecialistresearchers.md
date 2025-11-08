# (0.1)  Enhanced Personnel System with Specialist Researchers\n\nIssue Summary
Title: Implement specialist researcher system with unique skills and management mechanics
Problem: Current staffing system is generic - all researchers contribute equally without specialization, personality, or management complexity.
Solution: Add individual researchers with specializations, traits, and management requirements that create strategic hiring/retention decisions.
Technical Specification
Core Data Structure


pythonclass Researcher:
    def __init__(self, name, specialization, skill_level, traits, salary_expectation):
        self.name = name
        self.specialization = specialization  # "safety", "capabilities", "interpretability", "alignment"
        self.skill_level = skill_level  # 1-10
        self.traits = traits  # list of personality traits
        self.salary_expectation = salary_expectation
        self.productivity = 1.0  # modified by traits, events
        self.loyalty = 50  # 0-100, affects poaching resistance
        self.burnout = 0   # 0-100, reduces productivity when high

Specialization Effects

Safety Researchers: Reduce p(Doom) per research point by 15%
Capabilities Researchers: +25% research speed, +5% p(Doom) per research point
Interpretability Researchers: Unlock special "Audit Competitor" actions
Alignment Researchers: Reduce negative event probability by 10%

Trait System
Positive Traits:

Workaholic: +20% productivity, +2 burnout per turn
Team Player: +10% productivity to all researchers when present
Media Savvy: +reputation when publishing papers
Safety Conscious: -10% p(Doom) from their research

Negative Traits:

Prima Donna: -10% team productivity if salary expectations not met
Leak Prone: 5% chance per turn to leak research to competitors
Burnout Prone: +50% burnout accumulation rate

Management Actions

Salary Review: Increase/decrease individual salaries (affects loyalty/productivity)
Team Building: Cost money, reduce burnout, improve team cohesion
Performance Review: Identify underperformers, boost high performers
Poaching Defense: Spend money to retain researchers targeted by competitors

Integration Points

Hiring Phase: Each turn, available researchers with randomized stats/traits
Competitor Actions: Competitors can poach your best researchers
Event System: Personal events (researcher breakthrough, family emergency, ethical crisis)
Research Output: Specialized bonuses apply to relevant research tracks

UI Requirements

Researcher roster screen with filterable/sortable list
Individual researcher detail panels
Hiring interface with researcher comparison tools
Management action buttons in main interface

Complexity Settings

Simple: Generic researchers, no traits, basic hire/fire
Standard: Specializations active, basic traits
Complex: Full trait system, management actions, poaching mechanics\n\n<!-- GitHub Issue #197 -->