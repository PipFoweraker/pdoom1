'''
Public Opinion System - Track public sentiment and media coverage in P(Doom).

This module implements dynamic public opinion tracking that responds to player actions,
competitor actions, and external events. It integrates with the existing reputation
system while providing more nuanced public sentiment mechanics.
'''

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum
from src.services.deterministic_rng import get_rng



class OpinionCategory(Enum):
    '''Categories of public opinion that can be tracked.'''
    GENERAL_SENTIMENT = 'general_sentiment'
    TRUST_IN_PLAYER = 'trust_in_player'
    AI_SAFETY_AWARENESS = 'ai_safety_awareness'
    MEDIA_ATTENTION = 'media_attention'


class MediaStoryType(Enum):
    '''Types of media stories that can occur.'''
    BREAKTHROUGH = 'breakthrough'
    SCANDAL = 'scandal'
    HUMAN_INTEREST = 'human_interest'
    POLICY = 'policy'
    SAFETY_CONCERN = 'safety_concern'
    INDUSTRY_NEWS = 'industry_news'


@dataclass
class OpinionModifier:
    '''Represents a modifier to public opinion metrics.'''
    category: OpinionCategory
    change: float
    duration: int = 1  # Number of turns the modifier lasts
    source: str = 'unknown'  # What caused this modifier
    
    def apply(self, current_value: float) -> float:
        '''Apply this modifier to a current opinion value.'''
        return max(0.0, min(100.0, current_value + self.change))


@dataclass
class MediaStory:
    '''Represents a media story affecting public opinion.'''
    headline: str
    story_type: MediaStoryType
    sentiment_impact: Dict[OpinionCategory, float]
    duration: int  # Turns the story stays active
    attention_level: float  # How much media attention this generates (0-100)
    created_turn: int
    source_lab: Optional[str] = None  # Which lab triggered this story
    
    def __post_init__(self):
        '''Validate story data after creation.'''
        if not self.headline:
            raise ValueError('Media story must have a headline')
        if self.duration < 1:
            raise ValueError('Media story duration must be at least 1 turn')
        if not 0 <= self.attention_level <= 100:
            raise ValueError('Attention level must be between 0 and 100')
    
    def is_expired(self, current_turn: int) -> bool:
        '''Check if this story has expired.'''
        return current_turn >= self.created_turn + self.duration
    
    def get_remaining_turns(self, current_turn: int) -> int:
        '''Get remaining turns before story expires.'''
        return max(0, self.created_turn + self.duration - current_turn)


@dataclass
class PublicOpinion:
    '''
    Tracks public opinion metrics and handles their evolution over time.
    
    Integrates with the existing reputation system while providing more
    granular tracking of public sentiment.
    '''
    # Core opinion metrics (0-100 scale)
    general_sentiment: float = 50.0  # Overall optimism about AI
    trust_in_player: float = 50.0    # Specific trust in player's organization
    ai_safety_awareness: float = 20.0  # How much public cares about AI safety
    media_attention: float = 0.0     # How much media is watching AI sector
    
    # Historical tracking
    opinion_history: Dict[str, List[float]] = field(default_factory=dict)
    
    # Active modifiers and stories
    active_modifiers: List[OpinionModifier] = field(default_factory=list)
    active_stories: List[MediaStory] = field(default_factory=list)
    
    # Configuration
    decay_rate: float = 0.5  # How quickly extreme opinions return to neutral
    volatility: float = 1.0  # Multiplier for opinion changes
    
    def __post_init__(self):
        '''Initialize history tracking if not provided.'''
        if not self.opinion_history:
            self.opinion_history = {
                'general_sentiment': [self.general_sentiment],
                'trust_in_player': [self.trust_in_player],
                'ai_safety_awareness': [self.ai_safety_awareness],
                'media_attention': [self.media_attention]
            }
    
    def get_opinion(self, category: OpinionCategory) -> float:
        '''Get the current value for an opinion category.'''
        if category == OpinionCategory.GENERAL_SENTIMENT:
            return self.general_sentiment
        elif category == OpinionCategory.TRUST_IN_PLAYER:
            return self.trust_in_player
        elif category == OpinionCategory.AI_SAFETY_AWARENESS:
            return self.ai_safety_awareness
        elif category == OpinionCategory.MEDIA_ATTENTION:
            return self.media_attention
        else:
            raise ValueError(f'Unknown opinion category: {category}')
    
    def set_opinion(self, category: OpinionCategory, value: float):
        '''Set the value for an opinion category.'''
        value = max(0.0, min(100.0, value))
        
        if category == OpinionCategory.GENERAL_SENTIMENT:
            self.general_sentiment = value
        elif category == OpinionCategory.TRUST_IN_PLAYER:
            self.trust_in_player = value
        elif category == OpinionCategory.AI_SAFETY_AWARENESS:
            self.ai_safety_awareness = value
        elif category == OpinionCategory.MEDIA_ATTENTION:
            self.media_attention = value
        else:
            raise ValueError(f'Unknown opinion category: {category}')
    
    def add_modifier(self, modifier: OpinionModifier):
        '''Add a temporary modifier to public opinion.'''
        self.active_modifiers.append(modifier)
        # Note: GameLogger requires a turn parameter, but we don't have access to it here
        # This is fine since the add_modifier method is typically called during game actions
        # where turn information isn't always available
    
    def add_media_story(self, story: MediaStory):
        '''Add a new media story.'''
        self.active_stories.append(story)
        
        # Apply initial sentiment impact
        for category, impact in story.sentiment_impact.items():
            current = self.get_opinion(category)
            new_value = max(0.0, min(100.0, current + impact * self.volatility))
            self.set_opinion(category, new_value)
        
        # Increase media attention
        self.media_attention = min(100.0, self.media_attention + story.attention_level)
        
        # Note: We would log here if we had access to turn information
    
    def update_turn(self, current_turn: int):
        '''Update public opinion for a new turn.'''
        # Apply active modifiers
        for modifier in self.active_modifiers[:]:  # Copy list to allow removal during iteration
            current = self.get_opinion(modifier.category)
            new_value = modifier.apply(current)
            self.set_opinion(modifier.category, new_value)
            
            modifier.duration -= 1
            if modifier.duration <= 0:
                self.active_modifiers.remove(modifier)
        
        # Remove expired stories
        expired_stories = [story for story in self.active_stories if story.is_expired(current_turn)]
        for story in expired_stories:
            self.active_stories.remove(story)
            # Note: We would log story expiration here if needed
        
        # Apply natural decay toward neutral values
        self._apply_natural_decay()
        
        # Record history
        self._record_history()
    
    def _apply_natural_decay(self):
        '''Apply natural decay to bring extreme values toward neutral.'''
        # General sentiment drifts toward 50 (neutral)
        if self.general_sentiment > 50:
            self.general_sentiment = max(50, self.general_sentiment - self.decay_rate)
        elif self.general_sentiment < 50:
            self.general_sentiment = min(50, self.general_sentiment + self.decay_rate)
        
        # Trust in player drifts toward 50 (neutral)
        if self.trust_in_player > 50:
            self.trust_in_player = max(50, self.trust_in_player - self.decay_rate)
        elif self.trust_in_player < 50:
            self.trust_in_player = min(50, self.trust_in_player + self.decay_rate)
        
        # Media attention naturally decreases
        self.media_attention = max(0, self.media_attention - self.decay_rate * 2)
        
        # AI safety awareness slowly decreases if no events
        if not any(story.story_type == MediaStoryType.SAFETY_CONCERN for story in self.active_stories):
            self.ai_safety_awareness = max(0, self.ai_safety_awareness - self.decay_rate * 0.5)
    
    def _record_history(self):
        '''Record current values in history.'''
        self.opinion_history['general_sentiment'].append(self.general_sentiment)
        self.opinion_history['trust_in_player'].append(self.trust_in_player)
        self.opinion_history['ai_safety_awareness'].append(self.ai_safety_awareness)
        self.opinion_history['media_attention'].append(self.media_attention)
        
        # Keep only last 20 turns of history to prevent memory bloat
        for key in self.opinion_history:
            if len(self.opinion_history[key]) > 20:
                self.opinion_history[key] = self.opinion_history[key][-20:]
    
    def get_trend(self, category: OpinionCategory, turns: int = 3) -> str:
        '''Get trend direction for an opinion category.'''
        history_key = category.value
        if history_key not in self.opinion_history or len(self.opinion_history[history_key]) < 2:
            return 'stable'
        
        recent_values = self.opinion_history[history_key][-min(turns + 1, len(self.opinion_history[history_key])):]
        
        if len(recent_values) < 2:
            return 'stable'
        
        # Calculate average change over the period
        total_change = recent_values[-1] - recent_values[0]
        
        if total_change > 2:
            return 'rising'
        elif total_change < -2:
            return 'falling'
        else:
            return 'stable'
    
    def get_summary(self) -> str:
        '''Get a text summary of current public opinion.'''
        sentiment_desc = 'optimistic' if self.general_sentiment > 60 else 'pessimistic' if self.general_sentiment < 40 else 'neutral'
        trust_desc = 'high' if self.trust_in_player > 70 else 'low' if self.trust_in_player < 30 else 'moderate'
        awareness_desc = 'high' if self.ai_safety_awareness > 60 else 'low' if self.ai_safety_awareness < 30 else 'moderate'
        attention_desc = 'intense' if self.media_attention > 70 else 'minimal' if self.media_attention < 20 else 'moderate'
        
        return f'Public is {sentiment_desc} about AI, has {trust_desc} trust in your lab, shows {awareness_desc} safety awareness, with {attention_desc} media attention.'
    
    def to_dict(self) -> Dict[str, Any]:
        '''Convert to dictionary for serialization.'''
        return {
            'general_sentiment': self.general_sentiment,
            'trust_in_player': self.trust_in_player,
            'ai_safety_awareness': self.ai_safety_awareness,
            'media_attention': self.media_attention,
            'opinion_history': self.opinion_history,
            'active_stories': [
                {
                    'headline': story.headline,
                    'story_type': story.story_type.value,
                    'sentiment_impact': {cat.value: impact for cat, impact in story.sentiment_impact.items()},
                    'duration': story.duration,
                    'attention_level': story.attention_level,
                    'created_turn': story.created_turn,
                    'source_lab': story.source_lab
                }
                for story in self.active_stories
            ],
            'decay_rate': self.decay_rate,
            'volatility': self.volatility
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PublicOpinion':
        '''Create from dictionary for deserialization.'''
        opinion = cls(
            general_sentiment=data.get('general_sentiment', 50.0),
            trust_in_player=data.get('trust_in_player', 50.0),
            ai_safety_awareness=data.get('ai_safety_awareness', 20.0),
            media_attention=data.get('media_attention', 0.0),
            opinion_history=data.get('opinion_history', {}),
            decay_rate=data.get('decay_rate', 0.5),
            volatility=data.get('volatility', 1.0)
        )
        
        # Restore active stories
        for story_data in data.get('active_stories', []):
            sentiment_impact = {
                OpinionCategory(cat): impact 
                for cat, impact in story_data['sentiment_impact'].items()
            }
            story = MediaStory(
                headline=story_data['headline'],
                story_type=MediaStoryType(story_data['story_type']),
                sentiment_impact=sentiment_impact,
                duration=story_data['duration'],
                attention_level=story_data['attention_level'],
                created_turn=story_data['created_turn'],
                source_lab=story_data.get('source_lab')
            )
            opinion.active_stories.append(story)
        
        return opinion


def create_media_story_from_action(action_name: str, player_lab: str, turn: int, 
                                 reputation_change: float = 0) -> Optional[MediaStory]:
    '''
    Create a media story based on a player action.
    
    Returns None if the action doesn't warrant media coverage.
    '''
    # Define story templates for different action types
    story_templates = {
        'safety_research': {
            'headlines': [
                f'{player_lab} Publishes Groundbreaking AI Safety Research',
                f'New Safety Protocols Developed by {player_lab}',
                f'{player_lab} Leads Industry in AI Safety Innovation'
            ],
            'type': MediaStoryType.BREAKTHROUGH,
            'sentiment_impact': {
                OpinionCategory.TRUST_IN_PLAYER: 3 + reputation_change * 0.5,
                OpinionCategory.AI_SAFETY_AWARENESS: 5,
                OpinionCategory.GENERAL_SENTIMENT: 2
            },
            'duration': 2,
            'attention': 20
        },
        'capability_research': {
            'headlines': [
                f'{player_lab} Achieves Major AI Breakthrough',
                f'Revolutionary AI Technology from {player_lab}',
                f'{player_lab} Pushes Boundaries of AI Capability'
            ],
            'type': MediaStoryType.BREAKTHROUGH,
            'sentiment_impact': {
                OpinionCategory.GENERAL_SENTIMENT: 5,
                OpinionCategory.MEDIA_ATTENTION: 3,
                OpinionCategory.AI_SAFETY_AWARENESS: -1  # Slight concern about rapid progress
            },
            'duration': 2,
            'attention': 25
        },
        'transparency_action': {
            'headlines': [
                f'{player_lab} Opens Doors with Unprecedented Transparency',
                f'Inside Look: How {player_lab} Operates',
                f'{player_lab} Sets New Standard for AI Lab Transparency'
            ],
            'type': MediaStoryType.HUMAN_INTEREST,
            'sentiment_impact': {
                OpinionCategory.TRUST_IN_PLAYER: 5,
                OpinionCategory.GENERAL_SENTIMENT: 2
            },
            'duration': 1,
            'attention': 15
        }
    }
    
    # Map action names to story types
    action_to_story = {
        'safety_research': 'safety_research',
        'peer_review': 'safety_research',
        'safety_standards': 'safety_research',
        'interpretability': 'safety_research',
        'capability_research': 'capability_research',
        'scaling_research': 'capability_research',
        'deep_learning': 'capability_research',
        'transparency_report': 'transparency_action',
        'transparency_action': 'transparency_action'
    }
    
    story_type = action_to_story.get(action_name)
    if not story_type or story_type not in story_templates:
        return None
    
    template = story_templates[story_type]
    
    return MediaStory(
        headline=get_rng().choice(template['headlines'], 'choice_context'),
        story_type=template['type'],
        sentiment_impact=template['sentiment_impact'],
        duration=template['duration'],
        attention_level=template['attention'],
        created_turn=turn,
        source_lab=player_lab
    )