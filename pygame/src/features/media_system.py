'''
Media System - Handle media actions, cycles, and strategic communications in P(Doom).

This module provides media-related actions that players can take to influence
public opinion, manage their reputation, and respond to media coverage.
'''

from dataclasses import dataclass
from typing import Dict, List, Optional, Callable, Any
from enum import Enum
from src.services.deterministic_rng import get_rng

from src.features.public_opinion import (
    PublicOpinion, MediaStory, MediaStoryType, OpinionCategory, OpinionModifier
)


class MediaActionType(Enum):
    '''Types of media actions available to players.'''
    PRESS_RELEASE = 'press_release'
    EXCLUSIVE_INTERVIEW = 'exclusive_interview'
    DAMAGE_CONTROL = 'damage_control'
    INVESTIGATIVE_TIP = 'investigative_tip'
    PUBLIC_STATEMENT = 'public_statement'
    SOCIAL_MEDIA_CAMPAIGN = 'social_media_campaign'


@dataclass
class MediaAction:
    '''Represents a media action that players can take.'''
    action_type: MediaActionType
    name: str
    description: str
    money_cost: int
    ap_cost: int = 1
    reputation_cost: int = 0
    requirements: Optional[Callable] = None  # Function to check if action is available
    effect: Optional[Callable] = None  # Function to execute the action's effect
    
    def can_execute(self, game_state) -> bool:
        '''Check if this media action can be executed.'''
        if self.requirements:
            return self.requirements(game_state)
        return True
    
    def execute(self, game_state) -> str:
        '''Execute this media action and return a result message.'''
        if self.effect:
            return self.effect(game_state)
        return 'Action completed successfully.'


class MediaSystem:
    '''
    Manages media-related mechanics, actions, and story generation.
    
    Integrates with the PublicOpinion system to provide dynamic media coverage
    and player agency in managing their public image.
    '''
    
    def __init__(self, public_opinion: PublicOpinion):
        self.public_opinion = public_opinion
        self.media_actions = self._initialize_media_actions()
        self.competitor_stories_pool = self._initialize_competitor_stories()
        self.random_events_pool = self._initialize_random_events()
        
        # Tracking
        self.actions_taken_this_turn = []
        self.stories_generated_this_turn = []
    
    def _initialize_media_actions(self) -> Dict[str, MediaAction]:
        '''Initialize available media actions.'''
        actions = {}
        
        # Press Release - Control narrative around your actions
        actions['press_release'] = MediaAction(
            action_type=MediaActionType.PRESS_RELEASE,
            name='Issue Press Release',
            description='Control the narrative around recent developments. Costs $50k.',
            money_cost=50000,
            effect=self._execute_press_release
        )
        
        # Exclusive Interview - Deep dive story with high impact
        actions['exclusive_interview'] = MediaAction(
            action_type=MediaActionType.EXCLUSIVE_INTERVIEW,
            name='Exclusive Interview',
            description='In-depth interview with major outlet. High impact, costs reputation and time.',
            money_cost=0,
            ap_cost=1,
            reputation_cost=5,  # Risk of saying something wrong
            requirements=lambda gs: gs.reputation >= 10,  # Need some reputation to be newsworthy
            effect=self._execute_exclusive_interview
        )
        
        # Damage Control - Reduce negative story impact
        actions['damage_control'] = MediaAction(
            action_type=MediaActionType.DAMAGE_CONTROL,
            name='Damage Control',
            description='Reduce impact of negative media coverage by 50%. Costs $200k.',
            money_cost=200000,
            requirements=lambda gs: any(story.story_type == MediaStoryType.SCANDAL for story in gs.public_opinion.active_stories),
            effect=self._execute_damage_control
        )
        
        # Investigative Tip - Plant negative story about competitor
        actions['investigative_tip'] = MediaAction(
            action_type=MediaActionType.INVESTIGATIVE_TIP,
            name='Investigative Tip',
            description='Tip off journalists about competitor issues. Costs $100k, reduces trust if discovered.',
            money_cost=100000,
            requirements=lambda gs: gs.reputation >= 20,  # Need credibility for tips to be believed
            effect=self._execute_investigative_tip
        )
        
        # Public Statement - Quick response to current events
        actions['public_statement'] = MediaAction(
            action_type=MediaActionType.PUBLIC_STATEMENT,
            name='Public Statement',
            description='Issue statement on current events. Low cost, moderate impact.',
            money_cost=10000,
            effect=self._execute_public_statement
        )
        
        # Social Media Campaign - Reach younger demographics
        actions['social_media_campaign'] = MediaAction(
            action_type=MediaActionType.SOCIAL_MEDIA_CAMPAIGN,
            name='Social Media Campaign',
            description='Targeted social media push to improve public sentiment. $75k.',
            money_cost=75000,
            effect=self._execute_social_media_campaign
        )
        
        return actions
    
    def _initialize_competitor_stories(self) -> List[Dict[str, Any]]:
        '''Initialize pool of stories that can be generated about competitors.'''
        return [
            {
                'headline_template': '{lab} Researchers Raise Safety Concerns Internally',
                'type': MediaStoryType.SCANDAL,
                'sentiment_impact': {
                    OpinionCategory.GENERAL_SENTIMENT: -3,
                    OpinionCategory.AI_SAFETY_AWARENESS: 4,
                    OpinionCategory.MEDIA_ATTENTION: 2
                },
                'duration': 3,
                'attention': 30,
                'trigger_chance': 0.15
            },
            {
                'headline_template': '{lab} Achieves Breakthrough in Language Models',
                'type': MediaStoryType.BREAKTHROUGH,
                'sentiment_impact': {
                    OpinionCategory.GENERAL_SENTIMENT: 4,
                    OpinionCategory.MEDIA_ATTENTION: 3,
                    OpinionCategory.AI_SAFETY_AWARENESS: -1
                },
                'duration': 2,
                'attention': 25,
                'trigger_chance': 0.10
            },
            {
                'headline_template': '{lab} Executive Discusses AI\'s Future in Interview',
                'type': MediaStoryType.HUMAN_INTEREST,
                'sentiment_impact': {
                    OpinionCategory.GENERAL_SENTIMENT: 2,
                    OpinionCategory.MEDIA_ATTENTION: 1
                },
                'duration': 1,
                'attention': 15,
                'trigger_chance': 0.20
            }
        ]
    
    def _initialize_random_events(self) -> List[Dict[str, Any]]:
        '''Initialize pool of random media events not tied to specific labs.'''
        return [
            {
                'headline': 'Celebrity Endorses AI Development for Social Good',
                'type': MediaStoryType.HUMAN_INTEREST,
                'sentiment_impact': {
                    OpinionCategory.GENERAL_SENTIMENT: 5,
                    OpinionCategory.MEDIA_ATTENTION: 2
                },
                'duration': 2,
                'attention': 20,
                'trigger_chance': 0.05
            },
            {
                'headline': 'Congressional Hearing on AI Regulation Announced',
                'type': MediaStoryType.POLICY,
                'sentiment_impact': {
                    OpinionCategory.AI_SAFETY_AWARENESS: 6,
                    OpinionCategory.MEDIA_ATTENTION: 4,
                    OpinionCategory.GENERAL_SENTIMENT: -2
                },
                'duration': 3,
                'attention': 35,
                'trigger_chance': 0.08
            },
            {
                'headline': 'AI System Helps Solve Climate Research Challenge',
                'type': MediaStoryType.BREAKTHROUGH,
                'sentiment_impact': {
                    OpinionCategory.GENERAL_SENTIMENT: 6,
                    OpinionCategory.MEDIA_ATTENTION: 2
                },
                'duration': 2,
                'attention': 25,
                'trigger_chance': 0.06
            }
        ]
    
    def get_available_actions(self, game_state) -> List[MediaAction]:
        '''Get list of media actions available to the player.'''
        available = []
        for action in self.media_actions.values():
            if action.can_execute(game_state):
                available.append(action)
        return available
    
    def execute_media_action(self, action_name: str, game_state) -> str:
        '''Execute a media action and return the result.'''
        if action_name not in self.media_actions:
            return f'Unknown media action: {action_name}'
        
        action = self.media_actions[action_name]
        
        if not action.can_execute(game_state):
            return f'Cannot execute {action.name} - requirements not met.'
        
        # Check costs
        if game_state.money < action.money_cost:
            return f'Cannot afford {action.name} - costs ${action.money_cost:,}'
        
        if game_state.reputation < action.reputation_cost:
            return f'Insufficient reputation for {action.name} - costs {action.reputation_cost} reputation'
        
        if game_state.action_points < action.ap_cost:
            return f'Insufficient action points for {action.name} - costs {action.ap_cost} AP'
        
        # Pay costs
        game_state._add('money', -action.money_cost)
        game_state._add('reputation', -action.reputation_cost)
        game_state.action_points -= action.ap_cost
        
        # Execute effect
        result = action.execute(game_state)
        
        # Track action
        self.actions_taken_this_turn.append(action_name)
        # Note: Logging would happen here with proper turn information
        
        return result
    
    def generate_competitor_stories(self, competitors: List[str], current_turn: int):
        '''Generate media stories about competitor labs.'''
        new_stories = []
        
        for competitor in competitors:
            for story_template in self.competitor_stories_pool:
                if get_rng().random('random_context') < story_template['trigger_chance']:
                    # Adjust chance based on media attention level
                    attention_multiplier = 1 + (self.public_opinion.media_attention / 100)
                    if get_rng().random('random_context') < story_template['trigger_chance'] * attention_multiplier:
                        story = MediaStory(
                            headline=story_template['headline_template'].format(lab=competitor),
                            story_type=story_template['type'],
                            sentiment_impact=story_template['sentiment_impact'],
                            duration=story_template['duration'],
                            attention_level=story_template['attention'],
                            created_turn=current_turn,
                            source_lab=competitor
                        )
                        new_stories.append(story)
                        self.public_opinion.add_media_story(story)
        
        return new_stories
    
    def generate_random_events(self, current_turn: int):
        '''Generate random media events not tied to specific labs.'''
        new_stories = []
        
        for event_template in self.random_events_pool:
            if get_rng().random('random_context') < event_template['trigger_chance']:
                story = MediaStory(
                    headline=event_template['headline'],
                    story_type=event_template['type'],
                    sentiment_impact=event_template['sentiment_impact'],
                    duration=event_template['duration'],
                    attention_level=event_template['attention'],
                    created_turn=current_turn
                )
                new_stories.append(story)
                self.public_opinion.add_media_story(story)
        
        return new_stories
    
    def update_turn(self, game_state):
        '''Update media system for new turn.'''
        # Clear tracking
        self.actions_taken_this_turn = []
        self.stories_generated_this_turn = []
        
        # Generate competitor stories
        competitor_names = [opponent.name for opponent in game_state.opponents]
        competitor_stories = self.generate_competitor_stories(competitor_names, game_state.turn)
        
        # Generate random events
        random_stories = self.generate_random_events(game_state.turn)
        
        # Store generated stories for reference
        self.stories_generated_this_turn = competitor_stories + random_stories
        
        return self.stories_generated_this_turn
    
    # Media Action Effects
    
    def _execute_press_release(self, game_state) -> str:
        '''Execute press release action.'''
        # Moderate positive impact on trust and sentiment
        self.public_opinion.add_modifier(OpinionModifier(
            category=OpinionCategory.TRUST_IN_PLAYER,
            change=3,
            duration=2,
            source='Press Release'
        ))
        
        self.public_opinion.add_modifier(OpinionModifier(
            category=OpinionCategory.GENERAL_SENTIMENT,
            change=1,
            duration=1,
            source='Press Release'
        ))
        
        return 'Press release successfully shapes public narrative in your favor.'
    
    def _execute_exclusive_interview(self, game_state) -> str:
        '''Execute exclusive interview action.'''
        # High impact but with some risk
        trust_change = get_rng().randint(4, 8, 'randint_context')
        sentiment_change = get_rng().randint(1, 4, 'randint_context')
        
        # Small chance of negative outcome if reputation is low
        if game_state.reputation < 30 and get_rng().random('random_context') < 0.2:
            trust_change = -2
            sentiment_change = -1
            result_msg = 'Interview goes poorly, raising questions about your leadership.'
        else:
            result_msg = 'Exclusive interview showcases your expertise and vision.'
        
        self.public_opinion.add_modifier(OpinionModifier(
            category=OpinionCategory.TRUST_IN_PLAYER,
            change=trust_change,
            duration=3,
            source='Exclusive Interview'
        ))
        
        self.public_opinion.add_modifier(OpinionModifier(
            category=OpinionCategory.GENERAL_SENTIMENT,
            change=sentiment_change,
            duration=2,
            source='Exclusive Interview'
        ))
        
        # Generate media story about the interview
        interview_story = MediaStory(
            headline=f'{game_state.company_name} CEO Discusses AI Future in Exclusive Interview',
            story_type=MediaStoryType.HUMAN_INTEREST,
            sentiment_impact={
                OpinionCategory.TRUST_IN_PLAYER: trust_change * 0.5,
                OpinionCategory.GENERAL_SENTIMENT: sentiment_change * 0.5
            },
            duration=2,
            attention_level=20,
            created_turn=game_state.turn,
            source_lab=game_state.company_name
        )
        self.public_opinion.add_media_story(interview_story)
        
        return result_msg
    
    def _execute_damage_control(self, game_state) -> str:
        '''Execute damage control action.'''
        scandal_stories = [story for story in self.public_opinion.active_stories 
                          if story.story_type == MediaStoryType.SCANDAL]
        
        if not scandal_stories:
            return 'No negative stories to control.'
        
        # Reduce impact of most recent scandal
        latest_scandal = max(scandal_stories, key=lambda s: s.created_turn)
        
        # Halve the remaining impact
        for category, impact in latest_scandal.sentiment_impact.items():
            if impact < 0:  # Only reduce negative impacts
                recovery_modifier = OpinionModifier(
                    category=category,
                    change=-impact * 0.5,  # Recover half the negative impact
                    duration=1,
                    source='Damage Control'
                )
                self.public_opinion.add_modifier(recovery_modifier)
        
        # Reduce the story's duration
        latest_scandal.duration = max(1, latest_scandal.duration - 1)
        
        return f'Damage control reduces impact of \'{latest_scandal.headline}\''
    
    def _execute_investigative_tip(self, game_state) -> str:
        '''Execute investigative tip action.'''
        if not game_state.opponents:
            return 'No competitors to target.'
        
        # Select random competitor
        target = get_rng().choice(game_state.opponents, 'choice_context')
        target_name = target['name']
        
        # Risk of discovery based on reputation
        discovery_chance = max(0.1, 0.3 - (game_state.reputation / 200))
        
        if get_rng().random('random_context') < discovery_chance:
            # Discovered! Take reputation hit
            self.public_opinion.add_modifier(OpinionModifier(
                category=OpinionCategory.TRUST_IN_PLAYER,
                change=-5,
                duration=3,
                source='Exposed Manipulation'
            ))
            return f'Investigative tip backfires! Your involvement is exposed, damaging trust.'
        
        # Success - generate negative story about competitor
        scandal_headlines = [
            f'{target_name} Under Investigation for Safety Protocol Violations',
            f'Former {target_name} Employee Raises Serious Concerns',
            f'Questions Mount About {target_name}\'s Rushed Development Timeline'
        ]
        
        scandal_story = MediaStory(
            headline=get_rng().choice(scandal_headlines, 'choice_context'),
            story_type=MediaStoryType.SCANDAL,
            sentiment_impact={
                OpinionCategory.GENERAL_SENTIMENT: -2,
                OpinionCategory.AI_SAFETY_AWARENESS: 3,
                OpinionCategory.MEDIA_ATTENTION: 2
            },
            duration=3,
            attention_level=25,
            created_turn=game_state.turn,
            source_lab=target_name
        )
        
        self.public_opinion.add_media_story(scandal_story)
        
        return f'Anonymous tip generates negative coverage of {target_name}.'
    
    def _execute_public_statement(self, game_state) -> str:
        '''Execute public statement action.'''
        # Moderate positive impact, especially if there's high media attention
        base_trust_change = 2
        base_sentiment_change = 1
        
        # Boost effect if media attention is high
        if self.public_opinion.media_attention > 50:
            base_trust_change += 1
            base_sentiment_change += 1
        
        self.public_opinion.add_modifier(OpinionModifier(
            category=OpinionCategory.TRUST_IN_PLAYER,
            change=base_trust_change,
            duration=1,
            source='Public Statement'
        ))
        
        self.public_opinion.add_modifier(OpinionModifier(
            category=OpinionCategory.GENERAL_SENTIMENT,
            change=base_sentiment_change,
            duration=1,
            source='Public Statement'
        ))
        
        return 'Public statement reinforces your position on key issues.'
    
    def _execute_social_media_campaign(self, game_state) -> str:
        '''Execute social media campaign action.'''
        # Good for general sentiment, less for trust
        sentiment_boost = get_rng().randint(3, 6, 'randint_context')
        trust_boost = get_rng().randint(1, 3, 'randint_context')
        
        self.public_opinion.add_modifier(OpinionModifier(
            category=OpinionCategory.GENERAL_SENTIMENT,
            change=sentiment_boost,
            duration=2,
            source='Social Media Campaign'
        ))
        
        self.public_opinion.add_modifier(OpinionModifier(
            category=OpinionCategory.TRUST_IN_PLAYER,
            change=trust_boost,
            duration=1,
            source='Social Media Campaign'
        ))
        
        # Small chance of backlash if overused
        campaign_count = sum(1 for action in self.actions_taken_this_turn 
                           if action == 'social_media_campaign')
        
        if campaign_count > 2:  # Multiple campaigns this turn
            self.public_opinion.add_modifier(OpinionModifier(
                category=OpinionCategory.TRUST_IN_PLAYER,
                change=-2,
                duration=1,
                source='Campaign Overexposure'
            ))
            return 'Social media campaign shows mixed results due to overexposure.'
        
        return 'Social media campaign successfully improves public sentiment.'
    
    def get_media_summary(self) -> str:
        '''Get a summary of current media landscape.'''
        active_count = len(self.public_opinion.active_stories)
        if active_count == 0:
            return 'Media landscape is quiet with no major AI-related stories.'
        
        story_types = {}
        for story in self.public_opinion.active_stories:
            story_types[story.story_type] = story_types.get(story.story_type, 0) + 1
        
        type_descriptions = {
            MediaStoryType.BREAKTHROUGH: 'breakthrough stories',
            MediaStoryType.SCANDAL: 'scandal stories',
            MediaStoryType.HUMAN_INTEREST: 'human interest pieces',
            MediaStoryType.POLICY: 'policy discussions',
            MediaStoryType.SAFETY_CONCERN: 'safety concerns',
            MediaStoryType.INDUSTRY_NEWS: 'industry news'
        }
        
        descriptions = []
        for story_type, count in story_types.items():
            desc = type_descriptions.get(story_type, str(story_type.value))
            descriptions.append(f'{count} {desc}')
        
        return f'Current media: {', '.join(descriptions)} ({active_count} total stories active)'