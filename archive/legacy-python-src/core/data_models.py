'''
Typed dataclasses for core P(Doom) game entities.

This module provides strongly typed dataclasses to replace dict-based
implementations while maintaining backward compatibility with legacy
serialisation and existing code.
'''

from dataclasses import dataclass
from typing import Dict, Any, Optional, Callable, Union
from enum import Enum


class ActionType(Enum):
    '''Types of actions available in the game.'''
    GROWTH = 'growth'
    ECONOMIC = 'economic'
    RESEARCH = 'research'
    INTELLIGENCE = 'intelligence'
    MANAGEMENT = 'management'


@dataclass
class Action:
    '''
    Represents a player action in the game.
    
    Provides backward compatibility with existing dict-based action system
    while adding type safety and validation.
    '''
    name: str
    desc: str
    cost: int
    ap_cost: int = 1
    delegatable: bool = False
    delegate_staff_req: int = 0
    delegate_ap_cost: int = 0
    delegate_effectiveness: float = 1.0
    upside: Optional[Callable] = None
    downside: Optional[Callable] = None
    rules: Optional[Callable] = None
    action_type: ActionType = ActionType.MANAGEMENT
    
    def to_dict(self) -> Dict[str, Any]:
        '''Convert to legacy dict format for backward compatibility.'''
        return {
            'name': self.name,
            'desc': self.desc,
            'cost': self.cost,
            'ap_cost': self.ap_cost,
            'delegatable': self.delegatable,
            'delegate_staff_req': self.delegate_staff_req,
            'delegate_ap_cost': self.delegate_ap_cost,
            'delegate_effectiveness': self.delegate_effectiveness,
            'upside': self.upside,
            'downside': self.downside,
            'rules': self.rules,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Action':
        '''Create Action from legacy dict format.'''
        action_type = ActionType.MANAGEMENT  # Default
        # Try to infer action type from name/description
        if 'research' in data['name'].lower() or 'research' in data['desc'].lower():
            action_type = ActionType.RESEARCH
        elif 'money' in data['desc'].lower() or 'fundraise' in data['name'].lower():
            action_type = ActionType.ECONOMIC
        elif 'community' in data['name'].lower() or 'reputation' in data['desc'].lower():
            action_type = ActionType.GROWTH
        elif 'spy' in data['name'].lower() or 'intelligence' in data['desc'].lower():
            action_type = ActionType.INTELLIGENCE
            
        return cls(
            name=data['name'],
            desc=data['desc'],
            cost=data['cost'],
            ap_cost=data.get('ap_cost', 1),
            delegatable=data.get('delegatable', False),
            delegate_staff_req=data.get('delegate_staff_req', 0),
            delegate_ap_cost=data.get('delegate_ap_cost', 0),
            delegate_effectiveness=data.get('delegate_effectiveness', 1.0),
            upside=data.get('upside'),
            downside=data.get('downside'),
            rules=data.get('rules'),
            action_type=action_type,
        )


@dataclass
class Upgrade:
    '''
    Represents a purchasable upgrade in the game.
    
    Provides backward compatibility with existing dict-based upgrade system.
    '''
    name: str
    desc: str
    cost: int
    purchased: bool = False
    effect_key: str = ''
    custom_effect: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        '''Convert to legacy dict format for backward compatibility.'''
        result = {
            'name': self.name,
            'desc': self.desc,
            'cost': self.cost,
            'purchased': self.purchased,
            'effect_key': self.effect_key,
        }
        if self.custom_effect:
            result['custom_effect'] = self.custom_effect
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Upgrade':
        '''Create Upgrade from legacy dict format.'''
        return cls(
            name=data['name'],
            desc=data['desc'],
            cost=data['cost'],
            purchased=data.get('purchased', False),
            effect_key=data.get('effect_key', ''),
            custom_effect=data.get('custom_effect'),
        )


@dataclass
class Event:
    '''
    Represents a game event that can occur during play.
    
    Provides backward compatibility with existing dict-based event system.
    '''
    name: str
    desc: str
    probability: float
    effect: Optional[Callable] = None
    unlock_condition: Optional[str] = None
    category: str = 'general'
    
    def to_dict(self) -> Dict[str, Any]:
        '''Convert to legacy dict format for backward compatibility.'''
        result = {
            'name': self.name,
            'desc': self.desc,
            'probability': self.probability,
        }
        if self.effect:
            result['effect'] = self.effect
        if self.unlock_condition:
            result['unlock_condition'] = self.unlock_condition
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Event':
        '''Create Event from legacy dict format.'''
        # Infer category from event name/description
        category = 'general'
        if any(word in data['name'].lower() for word in ['breakthrough', 'research', 'lab']):
            category = 'research'
        elif any(word in data['name'].lower() for word in ['funding', 'money', 'budget']):
            category = 'economic'
        elif any(word in data['name'].lower() for word in ['staff', 'employee', 'hiring']):
            category = 'personnel'
            
        return cls(
            name=data['name'],
            desc=data['desc'],
            probability=data['probability'],
            effect=data.get('effect'),
            unlock_condition=data.get('unlock_condition'),
            category=category,
        )


@dataclass
class EmployeeSubtype:
    '''
    Represents a specific type of employee that can be hired.
    
    Provides backward compatibility with existing dict-based employee system.
    '''
    name: str
    description: str
    cost: int
    ap_cost: int
    effects: Dict[str, Union[int, float]]
    specialization: Optional[str] = None
    unlock_condition: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        '''Convert to legacy dict format for backward compatibility.'''
        result = {
            'name': self.name,
            'description': self.description,
            'cost': self.cost,
            'ap_cost': self.ap_cost,
            'effects': self.effects.copy(),
        }
        if self.specialization:
            result['specialization'] = self.specialization
        if self.unlock_condition:
            result['unlock_condition'] = self.unlock_condition
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EmployeeSubtype':
        '''Create EmployeeSubtype from legacy dict format.'''
        return cls(
            name=data['name'],
            description=data['description'],
            cost=data['cost'],
            ap_cost=data['ap_cost'],
            effects=data['effects'].copy(),
            specialization=data.get('specialization'),
            unlock_condition=data.get('unlock_condition'),
        )


# Legacy adapter functions for backward compatibility
def actions_to_dicts(actions: list[Action]) -> list[Dict[str, Any]]:
    '''Convert list of Action dataclasses to legacy dict format.'''
    return [action.to_dict() for action in actions]


def dicts_to_actions(action_dicts: list[Dict[str, Any]]) -> list[Action]:
    '''Convert list of legacy dict actions to Action dataclasses.'''
    return [Action.from_dict(action_dict) for action_dict in action_dicts]


def upgrades_to_dicts(upgrades: list[Upgrade]) -> list[Dict[str, Any]]:
    '''Convert list of Upgrade dataclasses to legacy dict format.'''
    return [upgrade.to_dict() for upgrade in upgrades]


def dicts_to_upgrades(upgrade_dicts: list[Dict[str, Any]]) -> list[Upgrade]:
    '''Convert list of legacy dict upgrades to Upgrade dataclasses.'''
    return [Upgrade.from_dict(upgrade_dict) for upgrade_dict in upgrade_dicts]


def events_to_dicts(events: list[Event]) -> list[Dict[str, Any]]:
    '''Convert list of Event dataclasses to legacy dict format.'''
    return [event.to_dict() for event in events]


def dicts_to_events(event_dicts: list[Dict[str, Any]]) -> list[Event]:
    '''Convert list of legacy dict events to Event dataclasses.'''
    return [Event.from_dict(event_dict) for event_dict in event_dicts]


def employee_subtypes_to_dict(subtypes: Dict[str, EmployeeSubtype]) -> Dict[str, Dict[str, Any]]:
    '''Convert employee subtypes dict to legacy format.'''
    return {key: subtype.to_dict() for key, subtype in subtypes.items()}


def dict_to_employee_subtypes(subtype_dicts: Dict[str, Dict[str, Any]]) -> Dict[str, EmployeeSubtype]:
    '''Convert legacy employee subtypes dict to EmployeeSubtype dataclasses.'''
    return {key: EmployeeSubtype.from_dict(subtype_dict) 
            for key, subtype_dict in subtype_dicts.items()}