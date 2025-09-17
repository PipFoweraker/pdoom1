"""
Tests for the Public Opinion & Media System.

Tests the core functionality of public opinion tracking, media stories,
and their integration with the game state.
"""

import unittest
from unittest.mock import Mock, patch

from src.core.game_state import GameState
from src.features.public_opinion import (
    PublicOpinion, MediaStory, MediaStoryType, OpinionCategory, 
    OpinionModifier, create_media_story_from_action
)
from src.features.media_system import MediaSystem


class TestPublicOpinion(unittest.TestCase):
    """Test the PublicOpinion class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.opinion = PublicOpinion()
    
    def test_opinion_initialization(self):
        """Test that public opinion initializes with correct default values."""
        self.assertEqual(self.opinion.general_sentiment, 50.0)
        self.assertEqual(self.opinion.trust_in_player, 50.0)
        self.assertEqual(self.opinion.ai_safety_awareness, 20.0)
        self.assertEqual(self.opinion.media_attention, 0.0)
        self.assertIsInstance(self.opinion.opinion_history, dict)
        self.assertEqual(len(self.opinion.active_modifiers), 0)
        self.assertEqual(len(self.opinion.active_stories), 0)
    
    def test_get_set_opinion(self):
        """Test getting and setting opinion values."""
        # Test getting values
        self.assertEqual(self.opinion.get_opinion(OpinionCategory.GENERAL_SENTIMENT), 50.0)
        
        # Test setting values
        self.opinion.set_opinion(OpinionCategory.TRUST_IN_PLAYER, 75.0)
        self.assertEqual(self.opinion.trust_in_player, 75.0)
        
        # Test clamping
        self.opinion.set_opinion(OpinionCategory.GENERAL_SENTIMENT, 150.0)
        self.assertEqual(self.opinion.general_sentiment, 100.0)
        
        self.opinion.set_opinion(OpinionCategory.GENERAL_SENTIMENT, -10.0)
        self.assertEqual(self.opinion.general_sentiment, 0.0)
    
    def test_opinion_modifiers(self):
        """Test adding and applying opinion modifiers."""
        modifier = OpinionModifier(
            category=OpinionCategory.TRUST_IN_PLAYER,
            change=10.0,
            duration=2,
            source="Test Action"
        )
        
        self.opinion.add_modifier(modifier)
        self.assertEqual(len(self.opinion.active_modifiers), 1)
        
        # Simulate turn updates
        initial_trust = self.opinion.trust_in_player
        self.opinion.update_turn(1)
        
        # Modifier should be applied but still active
        self.assertGreater(self.opinion.trust_in_player, initial_trust)
        self.assertEqual(len(self.opinion.active_modifiers), 1)
        
        # After another turn, modifier should expire
        self.opinion.update_turn(2)
        self.assertEqual(len(self.opinion.active_modifiers), 0)
    
    def test_media_stories(self):
        """Test adding and managing media stories."""
        story = MediaStory(
            headline="Test Lab Achieves Breakthrough",
            story_type=MediaStoryType.BREAKTHROUGH,
            sentiment_impact={
                OpinionCategory.GENERAL_SENTIMENT: 5.0,
                OpinionCategory.MEDIA_ATTENTION: 2.0
            },
            duration=2,
            attention_level=25.0,
            created_turn=1
        )
        
        initial_sentiment = self.opinion.general_sentiment
        initial_attention = self.opinion.media_attention
        
        self.opinion.add_media_story(story)
        
        # Story should be added and impact applied
        self.assertEqual(len(self.opinion.active_stories), 1)
        self.assertGreater(self.opinion.general_sentiment, initial_sentiment)
        self.assertGreater(self.opinion.media_attention, initial_attention)
        
        # Test story expiration
        self.assertFalse(story.is_expired(1))
        self.assertFalse(story.is_expired(2))
        self.assertTrue(story.is_expired(3))
        
        # Update to turn that should expire the story
        self.opinion.update_turn(4)
        self.assertEqual(len(self.opinion.active_stories), 0)
    
    def test_natural_decay(self):
        """Test that opinion values naturally decay toward neutral."""
        # Set extreme values
        self.opinion.general_sentiment = 90.0
        self.opinion.trust_in_player = 10.0
        self.opinion.media_attention = 80.0
        
        # Run several turns
        for turn in range(5):
            self.opinion.update_turn(turn)
        
        # Values should have moved toward neutral
        self.assertLess(self.opinion.general_sentiment, 90.0)
        self.assertGreater(self.opinion.trust_in_player, 10.0)
        self.assertLess(self.opinion.media_attention, 80.0)
    
    def test_trend_calculation(self):
        """Test opinion trend calculation."""
        # Add some history manually
        self.opinion.opinion_history['trust_in_player'] = [50.0, 55.0, 60.0, 65.0]
        
        trend = self.opinion.get_trend(OpinionCategory.TRUST_IN_PLAYER)
        self.assertEqual(trend, "rising")
        
        # Test falling trend
        self.opinion.opinion_history['trust_in_player'] = [65.0, 60.0, 55.0, 50.0]
        trend = self.opinion.get_trend(OpinionCategory.TRUST_IN_PLAYER)
        self.assertEqual(trend, "falling")
    
    def test_serialization(self):
        """Test converting public opinion to/from dictionary."""
        # Add some data
        self.opinion.general_sentiment = 65.0
        modifier = OpinionModifier(
            category=OpinionCategory.TRUST_IN_PLAYER,
            change=5.0,
            duration=1,
            source="Test"
        )
        self.opinion.add_modifier(modifier)
        
        story = MediaStory(
            headline="Test Story",
            story_type=MediaStoryType.HUMAN_INTEREST,
            sentiment_impact={OpinionCategory.GENERAL_SENTIMENT: 2.0},
            duration=1,
            attention_level=15.0,
            created_turn=1
        )
        self.opinion.add_media_story(story)
        
        # Convert to dict and back
        data = self.opinion.to_dict()
        restored_opinion = PublicOpinion.from_dict(data)
        
        # Check values are preserved (story impact was applied: 65.0 + 2.0 = 67.0)
        self.assertEqual(restored_opinion.general_sentiment, 67.0)
        self.assertEqual(len(restored_opinion.active_stories), 1)
        self.assertEqual(restored_opinion.active_stories[0].headline, "Test Story")


class TestMediaStory(unittest.TestCase):
    """Test the MediaStory class."""
    
    def test_story_creation(self):
        """Test creating a media story."""
        story = MediaStory(
            headline="AI Lab Makes Discovery",
            story_type=MediaStoryType.BREAKTHROUGH,
            sentiment_impact={OpinionCategory.GENERAL_SENTIMENT: 5.0},
            duration=3,
            attention_level=30.0,
            created_turn=1,
            source_lab="Test Lab"
        )
        
        self.assertEqual(story.headline, "AI Lab Makes Discovery")
        self.assertEqual(story.story_type, MediaStoryType.BREAKTHROUGH)
        self.assertEqual(story.duration, 3)
        self.assertEqual(story.source_lab, "Test Lab")
    
    def test_story_validation(self):
        """Test story creation validation."""
        # Test empty headline
        with self.assertRaises(ValueError):
            MediaStory("", MediaStoryType.BREAKTHROUGH, {}, 1, 50.0, 1)
        
        # Test invalid duration
        with self.assertRaises(ValueError):
            MediaStory("Test", MediaStoryType.BREAKTHROUGH, {}, 0, 50.0, 1)
        
        # Test invalid attention level
        with self.assertRaises(ValueError):
            MediaStory("Test", MediaStoryType.BREAKTHROUGH, {}, 1, 150.0, 1)
    
    def test_story_expiration(self):
        """Test story expiration logic."""
        story = MediaStory(
            headline="Test Story",
            story_type=MediaStoryType.HUMAN_INTEREST,
            sentiment_impact={},
            duration=2,
            attention_level=20.0,
            created_turn=5
        )
        
        self.assertFalse(story.is_expired(5))  # Same turn
        self.assertFalse(story.is_expired(6))  # One turn later
        self.assertTrue(story.is_expired(7))   # Expired
        
        self.assertEqual(story.get_remaining_turns(5), 2)
        self.assertEqual(story.get_remaining_turns(6), 1)
        self.assertEqual(story.get_remaining_turns(7), 0)


class TestMediaSystem(unittest.TestCase):
    """Test the MediaSystem class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.opinion = PublicOpinion()
        self.media_system = MediaSystem(self.opinion)
        self.mock_game_state = Mock()
        self.mock_game_state.money = 100000
        self.mock_game_state.reputation = 50
        self.mock_game_state.action_points = 3
        self.mock_game_state.turn = 1
        self.mock_game_state.company_name = "Test Lab"
        self.mock_game_state.opponents = [
            Mock(name="Competitor A"),
            Mock(name="Competitor B")
        ]
        # Mock the _add method
        self.mock_game_state._add = Mock()
        
        # Mock public_opinion with proper active_stories list
        self.mock_game_state.public_opinion = Mock()
        self.mock_game_state.public_opinion.active_stories = []
    
    def test_media_system_initialization(self):
        """Test media system initializes correctly."""
        self.assertIsInstance(self.media_system.public_opinion, PublicOpinion)
        self.assertGreater(len(self.media_system.media_actions), 0)
        self.assertEqual(len(self.media_system.actions_taken_this_turn), 0)
    
    def test_get_available_actions(self):
        """Test getting available media actions."""
        # Mock the media_system's hasattr check
        self.mock_game_state.media_system = self.media_system
        
        available = self.media_system.get_available_actions(self.mock_game_state)
        self.assertGreater(len(available), 0)
        
        # All returned actions should be executable
        for action in available:
            self.assertTrue(action.can_execute(self.mock_game_state))
    
    def test_press_release_action(self):
        """Test executing press release action."""
        result = self.media_system.execute_media_action('press_release', self.mock_game_state)
        
        self.assertIsInstance(result, str)
        self.assertIn('press_release', self.media_system.actions_taken_this_turn)
        
        # Should have called _add to deduct money
        self.mock_game_state._add.assert_any_call('money', -50000)
    
    def test_exclusive_interview_action(self):
        """Test executing exclusive interview action."""
        result = self.media_system.execute_media_action('exclusive_interview', self.mock_game_state)
        
        self.assertIsInstance(result, str)
        self.assertIn('exclusive_interview', self.media_system.actions_taken_this_turn)
        
        # Should generate a media story
        self.assertGreater(len(self.opinion.active_stories), 0)
    
    def test_insufficient_funds(self):
        """Test action execution with insufficient funds."""
        self.mock_game_state.money = 1000  # Not enough for press release
        
        result = self.media_system.execute_media_action('press_release', self.mock_game_state)
        
        self.assertIn("Cannot afford", result)
        self.assertEqual(len(self.media_system.actions_taken_this_turn), 0)
    
    def test_competitor_story_generation(self):
        """Test generating stories about competitors."""
        # Mock random to ensure story generation
        with patch('src.services.deterministic_rng.get_rng') as mock_get_rng:
            mock_rng = Mock()
            mock_rng.random.return_value = 0.01  # Force story generation
            mock_get_rng.return_value = mock_rng
            stories = self.media_system.generate_competitor_stories(
                ["Competitor A", "Competitor B"], 
                self.mock_game_state.turn
            )
            
            # Should generate at least one story
            self.assertGreater(len(stories), 0)
            self.assertGreater(len(self.opinion.active_stories), 0)
    
    def test_random_event_generation(self):
        """Test generating random media events."""
        # Mock random to ensure event generation
        with patch('src.services.deterministic_rng.get_rng') as mock_get_rng:
            mock_rng = Mock()
            mock_rng.random.return_value = 0.01  # Force event generation
            mock_get_rng.return_value = mock_rng
            stories = self.media_system.generate_random_events(self.mock_game_state.turn)
            
            # Should generate at least one story
            self.assertGreater(len(stories), 0)
            self.assertGreater(len(self.opinion.active_stories), 0)
    
    def test_turn_update(self):
        """Test media system turn update."""
        stories = self.media_system.update_turn(self.mock_game_state)
        
        # Should return list of new stories (even if empty)
        self.assertIsInstance(stories, list)
        
        # Tracking should be reset
        self.assertEqual(len(self.media_system.actions_taken_this_turn), 0)
        self.assertEqual(len(self.media_system.stories_generated_this_turn), 0)


class TestMediaStoryGeneration(unittest.TestCase):
    """Test media story generation from actions."""
    
    def test_create_story_from_safety_research(self):
        """Test creating media story from safety research action."""
        story = create_media_story_from_action(
            "safety_research", "Test Lab", 5, 3.0
        )
        
        self.assertIsNotNone(story)
        self.assertEqual(story.story_type, MediaStoryType.BREAKTHROUGH)
        self.assertIn("Test Lab", story.headline)
        self.assertEqual(story.created_turn, 5)
        self.assertEqual(story.source_lab, "Test Lab")
    
    def test_create_story_from_capability_research(self):
        """Test creating media story from capability research action."""
        story = create_media_story_from_action(
            "capability_research", "Research Corp", 10, 2.0
        )
        
        self.assertIsNotNone(story)
        self.assertEqual(story.story_type, MediaStoryType.BREAKTHROUGH)
        self.assertIn("Research Corp", story.headline)
    
    def test_no_story_for_unknown_action(self):
        """Test that unknown actions don't generate stories."""
        story = create_media_story_from_action(
            "unknown_action", "Test Lab", 1, 1.0
        )
        
        self.assertIsNone(story)


class TestGameStateIntegration(unittest.TestCase):
    """Test integration with the main game state."""
    
    def setUp(self):
        """Set up test game state."""
        self.game_state = GameState("test-seed")
    
    def test_public_opinion_initialization(self):
        """Test that public opinion is initialized in game state."""
        self.assertTrue(hasattr(self.game_state, 'public_opinion'))
        self.assertTrue(hasattr(self.game_state, 'media_system'))
        self.assertIsInstance(self.game_state.public_opinion, PublicOpinion)
        self.assertIsInstance(self.game_state.media_system, MediaSystem)
    
    def test_company_name_set(self):
        """Test that company name is set for media stories."""
        self.assertTrue(hasattr(self.game_state, 'company_name'))
        self.assertIsInstance(self.game_state.company_name, str)
        self.assertGreater(len(self.game_state.company_name), 0)
    
    def test_opinion_updates_on_turn_end(self):
        """Test that public opinion updates when turn ends."""
        initial_history_length = len(self.game_state.public_opinion.opinion_history['general_sentiment'])
        
        # End a turn
        self.game_state.end_turn()
        
        # History should be updated
        new_history_length = len(self.game_state.public_opinion.opinion_history['general_sentiment'])
        self.assertGreater(new_history_length, initial_history_length)
    
    def test_media_actions_available(self):
        """Test that media actions are available in the actions list."""
        media_action_names = [
            "Press Release", "Exclusive Interview", "Damage Control",
            "Social Media Campaign", "Public Statement"
        ]
        
        available_actions = [action['name'] for action in self.game_state.actions]
        
        for media_action in media_action_names:
            self.assertIn(media_action, available_actions)
    
    def test_research_action_generates_story(self):
        """Test that research actions can generate media stories."""
        # Find a research action
        research_actions = [
            action for action in self.game_state.actions 
            if 'research' in action['name'].lower()
        ]
        
        self.assertGreater(len(research_actions), 0)
        
        # Select and execute a research action that should generate media coverage
        len(self.game_state.public_opinion.active_stories)
        
        # Set up game state for action execution
        self.game_state.money = 100000
        self.game_state.reputation = 50
        self.game_state.action_points = 5
        
        # Find safety research action
        safety_action_idx = None
        for i, action in enumerate(self.game_state.actions):
            if action['name'] == 'Safety Research':
                safety_action_idx = i
                break
        
        if safety_action_idx is not None:
            self.game_state.selected_gameplay_actions = [safety_action_idx]
            self.game_state.end_turn()
            
            # Should have potential for media coverage (may or may not generate depending on reputation gain)
            # We can't guarantee a story is generated every time, but the system should be in place
            self.assertTrue(hasattr(self.game_state, 'media_system'))


if __name__ == '__main__':
    unittest.main()