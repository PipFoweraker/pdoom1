"""
End Game Scenarios System

This module provides varied and contextual end game scenarios based on different conditions
such as survival time, cause of defeat, resource levels, and game progression.
Each scenario provides detailed explanations of what led to the defeat and how long the player lasted.
"""

import random
from typing import Dict, Any, Optional


class EndGameScenario:
    """Represents a specific end game scenario with detailed narrative."""
    
    def __init__(self, title: str, description: str, cause_analysis: str, legacy_note: str = ""):
        self.title = title
        self.description = description
        self.cause_analysis = cause_analysis
        self.legacy_note = legacy_note


class EndGameScenariosManager:
    """Manages end game scenarios and determines which one applies to a given game state."""
    
    def __init__(self):
        self.scenarios = self._initialize_scenarios()
    
    def _initialize_scenarios(self) -> Dict[str, Dict[str, list]]:
        """Initialize the dictionary of end game scenarios organized by cause and duration."""
        return {
            "max_doom": {
                "early": [  # Turns 1-10
                    EndGameScenario(
                        "Catastrophic Miscalculation",
                        "Your organization's hasty push toward artificial general intelligence has resulted in immediate catastrophe. The AI system you developed achieved dangerous capabilities far sooner than anticipated, overwhelming all safety measures within just a few turns.",
                        "Early doom escalation suggests insufficient safety research and overly aggressive development. The rapid failure indicates a lack of proper safeguards and risk assessment protocols.",
                        "Your brief but impactful attempt serves as a cautionary tale about the dangers of rushing toward AGI without adequate preparation."
                    ),
                    EndGameScenario(
                        "Reckless Acceleration",
                        "In an attempt to quickly establish dominance in the AI race, your team pushed development beyond safe limits. The resulting system's capabilities spiral out of control, leading to immediate global consequences.",
                        "The rapid doom increase indicates a fundamental misunderstanding of AI development risks. Critical safety measures were likely skipped in favor of speed.",
                        "Though short-lived, your organization's failure highlights the importance of measured, safety-conscious AI development."
                    )
                ],
                "mid": [  # Turns 11-25
                    EndGameScenario(
                        "Safety Measures Overwhelmed",
                        "Despite establishing some basic safety protocols, your organization's AI development eventually outpaced your ability to control it. The system achieved dangerous capabilities that your safeguards couldn't contain.",
                        "Mid-game doom escalation suggests that initial safety measures were insufficient for the scale of development undertaken. More robust safety research and risk mitigation were needed.",
                        "Your organization managed to operate for a significant period but ultimately fell to the challenge of balancing progress with safety."
                    ),
                    EndGameScenario(
                        "Competitive Pressure Compromise",
                        "Pressure from competing organizations led to increasingly risky decisions. While you maintained operations longer than some, the competitive environment ultimately forced compromises that led to catastrophic AI development.",
                        "The moderate survival time indicates good initial planning but eventual capitulation to external pressures. Better risk assessment and stakeholder management could have prevented this outcome.",
                        "Your sustained effort shows promise, but the competitive AI landscape proved too challenging to navigate safely."
                    )
                ],
                "late": [  # Turns 26+
                    EndGameScenario(
                        "Long-Term Risk Accumulation",
                        "Your organization demonstrated impressive resilience and safety consciousness, operating for an extended period while managing AI development risks. However, the cumulative effects of long-term high-stakes development eventually overwhelmed even your robust safety measures.",
                        "Late-game doom suggests excellent risk management and safety protocols that held for an extended period. The eventual failure likely represents the inherent difficulty of long-term AI safety rather than poor planning.",
                        "Your organization's extended operation serves as a model for responsible AI development, showing how proper safety measures can provide significant protection."
                    ),
                    EndGameScenario(
                        "The Slow Burn",
                        "Your careful, methodical approach to AI development allowed for extended operations and significant progress. However, the gradual accumulation of small risks and the inherent unpredictability of advanced AI systems eventually led to a cascade failure.",
                        "Extended survival with eventual doom escalation indicates excellent safety practices that couldn't ultimately overcome the fundamental challenges of AI alignment and control.",
                        "Your organization's impressive longevity demonstrates the value of cautious, safety-first approaches to AI development."
                    )
                ]
            },
            "opponent_victory": {
                "early": [
                    EndGameScenario(
                        "Outpaced by Competition",
                        "A rival organization achieved dangerous AGI deployment while your team was still establishing basic operations. Their rapid development caught the entire field off-guard, leading to global consequences before safety measures could be implemented.",
                        "Early defeat by opponents suggests either insufficient competitive analysis or overly conservative initial strategy. More aggressive early development or better intelligence gathering might have provided warning.",
                        "Though brief, your organization's focus on safety over speed may have been the right approach in a better world."
                    ),
                    EndGameScenario(
                        "Startup Disruption",
                        "A well-funded startup with a 'move fast and break things' mentality achieved AGI breakthrough while your organization was still building foundational capabilities. Their disregard for safety protocols proved catastrophically effective.",
                        "Rapid defeat suggests underestimating the competitive landscape and the willingness of others to take extreme risks. Earlier competitive positioning was needed.",
                        "Your cautious approach was overwhelmed by others' recklessness, highlighting the challenges of responsible development in an unregulated environment."
                    )
                ],
                "mid": [
                    EndGameScenario(
                        "Arms Race Escalation",
                        "Despite maintaining competitive development for a reasonable period, a rival organization's breakthrough in a critical capability allowed them to achieve dangerous AGI first. The competitive pressure may have led both organizations to take increasing risks.",
                        "Mid-game defeat by opponents indicates good competitive positioning initially, but eventual loss in a key capability race. Better resource allocation or different strategic priorities might have changed the outcome.",
                        "Your organization held its own in the AI race for a significant period, demonstrating competent strategy and execution."
                    ),
                    EndGameScenario(
                        "Resource Disadvantage",
                        "While your organization maintained operations and made steady progress, a competitor with superior resources ultimately achieved dangerous AGI deployment first. Your efforts, though valiant, couldn't overcome their advantages in funding, talent, or compute.",
                        "Moderate survival before opponent victory suggests good strategy execution but insufficient resources to compete long-term. Alternative approaches or partnerships might have provided better competitive positioning.",
                        "Your organization's sustained effort against better-resourced competitors demonstrates determination and skill in the face of challenging odds."
                    )
                ],
                "late": [
                    EndGameScenario(
                        "Final Sprint Lost",
                        "Your organization maintained strong competitive positioning for an extended period, developing significant capabilities and safety measures. However, in the final stages of the race to AGI, a competitor's breakthrough allowed them to cross the finish line first.",
                        "Late-game defeat suggests excellent long-term strategy and execution. The loss may have come down to specific technical breakthroughs or final resource allocation decisions.",
                        "Your organization's extended competitive performance demonstrates world-class capabilities in AI development and safety research."
                    ),
                    EndGameScenario(
                        "The Photo Finish",
                        "After a long and closely contested race, your organization was narrowly defeated by a competitor who achieved dangerous AGI just ahead of your own timeline. Both organizations had reached advanced stages of development when the decisive moment arrived.",
                        "Very close late-game defeat indicates excellent competitive strategy and execution. The outcome may have hinged on minor advantages in specific capabilities or timing.",
                        "Your organization's performance in the extended AI race showcases the highest levels of technical and strategic competence."
                    )
                ]
            },
            "no_staff": {
                "early": [
                    EndGameScenario(
                        "Staffing Crisis",
                        "Your organization failed to maintain adequate staffing levels to continue operations. Early departure of key personnel suggests fundamental issues with working conditions, compensation, or organizational culture.",
                        "Rapid staff loss indicates critical failures in human resources management, organizational culture, or project appeal. Staff retention should have been a higher priority.",
                        "Though brief, your organization's experience highlights the importance of building sustainable, attractive working environments for critical projects."
                    ),
                    EndGameScenario(
                        "Talent Exodus",
                        "Key staff members abandoned the project early, citing concerns about safety, ethics, or organizational direction. The mass departure left the organization unable to continue meaningful operations.",
                        "Early staff exodus suggests misalignment between organizational goals and staff values, or inadequate communication about the project's importance and approach.",
                        "Your organization's quick dissolution serves as a reminder that even the most important projects require staff buy-in and ethical alignment."
                    )
                ],
                "mid": [
                    EndGameScenario(
                        "Gradual Attrition",
                        "Despite maintaining operations for a reasonable period, your organization gradually lost key personnel to competitors, burnout, or changing priorities. The slow drain of talent eventually made continued operations impossible.",
                        "Mid-game staff loss indicates initial success in retention but eventual failure to maintain competitive working conditions or project momentum.",
                        "Your organization showed promise in its early stages but couldn't maintain the human capital necessary for sustained operations."
                    ),
                    EndGameScenario(
                        "Competitive Poaching",
                        "Rival organizations systematically recruited your key personnel with better offers, superior resources, or more appealing project directions. Despite your efforts to retain talent, the competitive pressure proved overwhelming.",
                        "Staff loss to competitors suggests good initial team building but insufficient resources or appeal to retain talent long-term. Better competitive positioning in the talent market was needed.",
                        "Your organization's ability to attract talent initially shows promise, but the competitive AI talent market proved challenging to navigate."
                    )
                ],
                "late": [
                    EndGameScenario(
                        "Mission Accomplished Departure",
                        "After extended successful operations, key staff members departed for various reasons - some felt the mission was complete, others were recruited by competitors who could offer career advancement. The loss of institutional knowledge made continuation difficult.",
                        "Late-game staff departure often indicates successful project execution that created valuable, marketable expertise. Staff retention in mature projects requires ongoing career development and mission evolution.",
                        "Your organization's extended operation created significant value and expertise, even if it couldn't maintain the team indefinitely."
                    ),
                    EndGameScenario(
                        "Burnout After Long Campaign",
                        "Following an extended period of high-intensity AI development work, key staff members reached burnout and left for less demanding positions. The psychological toll of long-term high-stakes work proved unsustainable.",
                        "Extended operation followed by staff burnout indicates good initial retention but insufficient attention to long-term staff welfare and sustainable work practices.",
                        "Your organization's impressive longevity demonstrates strong initial team building, though sustainable work practices could have extended operations further."
                    )
                ]
            }
        }
    
    def get_scenario(self, game_state) -> EndGameScenario:
        """
        Determine and return the appropriate end game scenario based on game state.
        
        Args:
            game_state: GameState object containing all game information
            
        Returns:
            EndGameScenario object with detailed narrative for this specific game end
        """
        # Determine the primary cause of defeat
        cause = self._determine_defeat_cause(game_state)
        
        # Determine the time period based on survival turns
        time_period = self._determine_time_period(game_state.turn)
        
        # Get appropriate scenarios for this cause and time period
        scenarios = self.scenarios.get(cause, {}).get(time_period, [])
        
        if not scenarios:
            # Fallback to a generic scenario
            return self._create_fallback_scenario(game_state, cause, time_period)
        
        # Select a scenario (could be random or based on specific conditions)
        return self._select_scenario(scenarios, game_state)
    
    def _determine_defeat_cause(self, game_state) -> str:
        """Determine the primary cause of defeat from game state."""
        if game_state.doom >= game_state.max_doom:
            return "max_doom"
        elif game_state.staff == 0:
            return "no_staff"
        else:
            # Check if any opponent won
            for opponent in game_state.opponents:
                if opponent.progress >= 100:
                    return "opponent_victory"
        
        # Default fallback
        return "max_doom"
    
    def _determine_time_period(self, turns: int) -> str:
        """Determine time period category based on number of turns survived."""
        if turns <= 10:
            return "early"
        elif turns <= 25:
            return "mid"
        else:
            return "late"
    
    def _select_scenario(self, scenarios: list, game_state) -> EndGameScenario:
        """Select the most appropriate scenario from available options."""
        # For now, use random selection, but this could be enhanced with
        # additional game state analysis (resource levels, specific events, etc.)
        random.seed(game_state.seed + game_state.turn)  # Deterministic based on game
        return random.choice(scenarios)
    
    def _create_fallback_scenario(self, game_state, cause: str, time_period: str) -> EndGameScenario:
        """Create a generic fallback scenario when specific ones aren't available."""
        return EndGameScenario(
            "Unexpected Conclusion",
            f"Your organization's journey came to an end after {game_state.turn} turns. Despite your efforts to navigate the complex challenges of AI development, circumstances led to an unavoidable conclusion.",
            f"The end came through {cause.replace('_', ' ')} during the {time_period} phase of operations. More detailed analysis of this situation may be needed for future reference.",
            f"Your organization's {game_state.turn}-turn operation provides valuable lessons for future AI safety efforts."
        )


# Global instance for use throughout the application
end_game_scenarios = EndGameScenariosManager()