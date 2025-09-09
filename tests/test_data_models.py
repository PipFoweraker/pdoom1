"""
Tests for typed dataclasses in data_models.py

Tests cover:
- Dataclass creation and field validation
- Conversion to/from legacy dict format
- Backward compatibility with existing systems
- Type safety and validation
"""

import unittest
from unittest.mock import Mock
from src.core.data_models import (
    Action, Upgrade, Event, EmployeeSubtype, ActionType,
    actions_to_dicts, dicts_to_actions,
    upgrades_to_dicts, dicts_to_upgrades,
    employee_subtypes_to_dict, dict_to_employee_subtypes
)


class TestActionDataclass(unittest.TestCase):
    """Test the Action dataclass."""
    
    def test_action_creation(self):
        """Test basic Action creation with required fields."""
        action = Action(
            name="Test Action",
            desc="A test action",
            cost=50,
            ap_cost=2
        )
        
        self.assertEqual(action.name, "Test Action")
        self.assertEqual(action.desc, "A test action") 
        self.assertEqual(action.cost, 50)
        self.assertEqual(action.ap_cost, 2)
        self.assertEqual(action.action_type, ActionType.MANAGEMENT)  # Default
    
    def test_action_with_delegation(self):
        """Test Action with delegation parameters."""
        mock_upside = Mock()
        mock_downside = Mock()
        mock_rules = Mock()
        
        action = Action(
            name="Delegatable Action",
            desc="Can be delegated",
            cost=100,
            ap_cost=1,
            delegatable=True,
            delegate_staff_req=2,
            delegate_ap_cost=0,
            delegate_effectiveness=0.8,
            upside=mock_upside,
            downside=mock_downside,
            rules=mock_rules,
            action_type=ActionType.ECONOMIC
        )
        
        self.assertTrue(action.delegatable)
        self.assertEqual(action.delegate_staff_req, 2)
        self.assertEqual(action.delegate_ap_cost, 0)
        self.assertEqual(action.delegate_effectiveness, 0.8)
        self.assertEqual(action.upside, mock_upside)
        self.assertEqual(action.downside, mock_downside)
        self.assertEqual(action.rules, mock_rules)
        self.assertEqual(action.action_type, ActionType.ECONOMIC)
    
    def test_action_to_dict(self):
        """Test converting Action to legacy dict format."""
        mock_upside = Mock()
        action = Action(
            name="Test",
            desc="Test action",
            cost=25,
            ap_cost=1,
            upside=mock_upside
        )
        
        result = action.to_dict()
        
        expected_keys = {
            "name", "desc", "cost", "ap_cost", "delegatable",
            "delegate_staff_req", "delegate_ap_cost", "delegate_effectiveness",
            "upside", "downside", "rules"
        }
        self.assertEqual(set(result.keys()), expected_keys)
        self.assertEqual(result["name"], "Test")
        self.assertEqual(result["upside"], mock_upside)
    
    def test_action_from_dict(self):
        """Test creating Action from legacy dict format."""
        legacy_dict = {
            "name": "Fundraise",
            "desc": "+Money (scaled by rep), small rep risk.",
            "cost": 0,
            "ap_cost": 1,
            "delegatable": True,
            "delegate_staff_req": 1,
            "delegate_ap_cost": 1,
            "delegate_effectiveness": 0.9,
            "upside": Mock(),
            "downside": Mock(),
            "rules": None
        }
        
        action = Action.from_dict(legacy_dict)
        
        self.assertEqual(action.name, "Fundraise")
        self.assertEqual(action.cost, 0)
        self.assertTrue(action.delegatable)
        self.assertEqual(action.action_type, ActionType.ECONOMIC)  # Inferred from name
    
    def test_action_type_inference(self):
        """Test that action types are correctly inferred from name/description."""
        test_cases = [
            ({"name": "Research Project", "desc": "Do research"}, ActionType.RESEARCH),
            ({"name": "Fundraise", "desc": "Raise money"}, ActionType.ECONOMIC),
            ({"name": "Grow Community", "desc": "Increase reputation"}, ActionType.GROWTH),
            ({"name": "Spy Network", "desc": "Intelligence gathering"}, ActionType.INTELLIGENCE),
            ({"name": "Generic Action", "desc": "Generic description"}, ActionType.MANAGEMENT),
        ]
        
        for test_dict, expected_type in test_cases:
            test_dict.update({"cost": 0, "ap_cost": 1})
            action = Action.from_dict(test_dict)
            self.assertEqual(action.action_type, expected_type)


class TestUpgradeDataclass(unittest.TestCase):
    """Test the Upgrade dataclass."""
    
    def test_upgrade_creation(self):
        """Test basic Upgrade creation."""
        upgrade = Upgrade(
            name="Better Computers",
            desc="Faster processing",
            cost=200,
            effect_key="better_computers"
        )
        
        self.assertEqual(upgrade.name, "Better Computers")
        self.assertEqual(upgrade.cost, 200)
        self.assertFalse(upgrade.purchased)  # Default
        self.assertEqual(upgrade.effect_key, "better_computers")
    
    def test_upgrade_with_custom_effect(self):
        """Test Upgrade with custom effect."""
        upgrade = Upgrade(
            name="Accounting Software",
            desc="Track finances",
            cost=500,
            purchased=True,
            effect_key="accounting_software",
            custom_effect="buy_accounting_software"
        )
        
        self.assertTrue(upgrade.purchased)
        self.assertEqual(upgrade.custom_effect, "buy_accounting_software")
    
    def test_upgrade_to_dict(self):
        """Test converting Upgrade to legacy dict format."""
        upgrade = Upgrade(
            name="Test Upgrade",
            desc="Test description",
            cost=100,
            purchased=True,
            effect_key="test_effect",
            custom_effect="custom_test"
        )
        
        result = upgrade.to_dict()
        
        self.assertEqual(result["name"], "Test Upgrade")
        self.assertEqual(result["cost"], 100)
        self.assertTrue(result["purchased"])
        self.assertEqual(result["custom_effect"], "custom_test")
    
    def test_upgrade_from_dict(self):
        """Test creating Upgrade from legacy dict format."""
        legacy_dict = {
            "name": "Office Chairs",
            "desc": "Comfy seating",
            "cost": 120,
            "purchased": False,
            "effect_key": "comfy_chairs"
        }
        
        upgrade = Upgrade.from_dict(legacy_dict)
        
        self.assertEqual(upgrade.name, "Office Chairs")
        self.assertEqual(upgrade.cost, 120)
        self.assertFalse(upgrade.purchased)
        self.assertIsNone(upgrade.custom_effect)  # Not in dict


class TestEventDataclass(unittest.TestCase):
    """Test the Event dataclass."""
    
    def test_event_creation(self):
        """Test basic Event creation."""
        mock_effect = Mock()
        event = Event(
            name="Test Event",
            desc="A test event occurs",
            probability=0.3,
            effect=mock_effect,
            category="research"
        )
        
        self.assertEqual(event.name, "Test Event")
        self.assertEqual(event.probability, 0.3)
        self.assertEqual(event.effect, mock_effect)
        self.assertEqual(event.category, "research")
    
    def test_event_category_inference(self):
        """Test that event categories are correctly inferred."""
        test_cases = [
            ({"name": "Lab Breakthrough", "desc": "Research advance"}, "research"),
            ({"name": "Funding Cut", "desc": "Budget problems"}, "economic"),
            ({"name": "Staff Departure", "desc": "Employee leaves"}, "personnel"),
            ({"name": "Random Event", "desc": "Something happens"}, "general"),
        ]
        
        for test_dict, expected_category in test_cases:
            test_dict.update({"probability": 0.1})
            event = Event.from_dict(test_dict)
            self.assertEqual(event.category, expected_category)
    
    def test_event_to_dict(self):
        """Test converting Event to legacy dict format."""
        mock_effect = Mock()
        event = Event(
            name="Test Event",
            desc="Test description",
            probability=0.2,
            effect=mock_effect,
            unlock_condition="turn >= 5"
        )
        
        result = event.to_dict()
        
        self.assertEqual(result["name"], "Test Event")
        self.assertEqual(result["probability"], 0.2)
        self.assertEqual(result["effect"], mock_effect)
        self.assertEqual(result["unlock_condition"], "turn >= 5")


class TestEmployeeSubtypeDataclass(unittest.TestCase):
    """Test the EmployeeSubtype dataclass."""
    
    def test_employee_subtype_creation(self):
        """Test basic EmployeeSubtype creation."""
        effects = {"staff": 1, "research_progress": 5}
        subtype = EmployeeSubtype(
            name="Researcher",
            description="PhD specialist",
            cost=75,
            ap_cost=2,
            effects=effects,
            specialization="research",
            unlock_condition="turn >= 3"
        )
        
        self.assertEqual(subtype.name, "Researcher")
        self.assertEqual(subtype.cost, 75)
        self.assertEqual(subtype.ap_cost, 2)
        self.assertEqual(subtype.effects, effects)
        self.assertEqual(subtype.specialization, "research")
    
    def test_employee_subtype_to_dict(self):
        """Test converting EmployeeSubtype to legacy dict format."""
        effects = {"staff": 1, "admin_staff": 1}
        subtype = EmployeeSubtype(
            name="Administrator",
            description="Admin specialist",
            cost=70,
            ap_cost=1,
            effects=effects,
            specialization="admin"
        )
        
        result = subtype.to_dict()
        
        self.assertEqual(result["name"], "Administrator")
        self.assertEqual(result["cost"], 70)
        self.assertEqual(result["effects"], effects)
        self.assertEqual(result["specialization"], "admin")
    
    def test_employee_subtype_from_dict(self):
        """Test creating EmployeeSubtype from legacy dict format."""
        legacy_dict = {
            "name": "Generalist",
            "description": "Versatile employee",
            "cost": 60,
            "ap_cost": 1,
            "effects": {"staff": 1},
            "specialization": None,
            "unlock_condition": None
        }
        
        subtype = EmployeeSubtype.from_dict(legacy_dict)
        
        self.assertEqual(subtype.name, "Generalist")
        self.assertEqual(subtype.cost, 60)
        self.assertEqual(subtype.effects, {"staff": 1})
        self.assertIsNone(subtype.specialization)


class TestLegacyAdapters(unittest.TestCase):
    """Test the legacy adapter functions."""
    
    def test_actions_conversion_roundtrip(self):
        """Test that Actions can be converted to dicts and back without loss."""
        original_actions = [
            Action("Action 1", "Description 1", 50, 1),
            Action("Action 2", "Description 2", 100, 2, delegatable=True)
        ]
        
        # Convert to dicts and back
        dicts = actions_to_dicts(original_actions)
        converted_actions = dicts_to_actions(dicts)
        
        self.assertEqual(len(converted_actions), 2)
        self.assertEqual(converted_actions[0].name, "Action 1")
        self.assertEqual(converted_actions[1].delegatable, True)
    
    def test_upgrades_conversion_roundtrip(self):
        """Test that Upgrades can be converted to dicts and back without loss."""
        original_upgrades = [
            Upgrade("Upgrade 1", "Description 1", 200),
            Upgrade("Upgrade 2", "Description 2", 300, purchased=True)
        ]
        
        # Convert to dicts and back
        dicts = upgrades_to_dicts(original_upgrades)
        converted_upgrades = dicts_to_upgrades(dicts)
        
        self.assertEqual(len(converted_upgrades), 2)
        self.assertEqual(converted_upgrades[0].cost, 200)
        self.assertTrue(converted_upgrades[1].purchased)
    
    def test_employee_subtypes_conversion_roundtrip(self):
        """Test that EmployeeSubtypes can be converted to dicts and back."""
        original_subtypes = {
            "researcher": EmployeeSubtype(
                "Researcher", "PhD specialist", 75, 2, 
                {"staff": 1, "research_progress": 5}, "research"
            ),
            "admin": EmployeeSubtype(
                "Administrator", "Admin specialist", 70, 1,
                {"staff": 1, "admin_staff": 1}, "admin"
            )
        }
        
        # Convert to dicts and back
        dicts = employee_subtypes_to_dict(original_subtypes)
        converted_subtypes = dict_to_employee_subtypes(dicts)
        
        self.assertEqual(len(converted_subtypes), 2)
        self.assertEqual(converted_subtypes["researcher"].name, "Researcher")
        self.assertEqual(converted_subtypes["admin"].specialization, "admin")


if __name__ == '__main__':
    unittest.main()