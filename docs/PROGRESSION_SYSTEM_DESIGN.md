# Progression System Extensibility Design

## Overview

This document outlines the design for making P(Doom)'s progression system more extensible and maintainable. The current system has various progression elements scattered throughout the codebase that could be unified into a more cohesive, data-driven architecture.

## Current State Analysis

### Existing Progression Elements

1. **Actions System** (`actions.py`)
   - Action unlock rules via `action_rules.py`
   - Delegation mechanics with staff requirements
   - Action Points (AP) costs and management

2. **Upgrades System** (`upgrades.py`)
   - Static upgrade definitions
   - Effect keys for game state modifications
   - Custom effects for special upgrades

3. **Events System** (`events.py`, `event_system.py`)
   - Milestone-triggered events
   - Turn-based progression events
   - Enhanced event system with deferrals

4. **Employee System** (`employee_subtypes.py`, `productive_actions.py`)
   - Employee specialization unlocks
   - Productive action assignments
   - Compute-based effectiveness modifiers

5. **Opponent System** (`opponents.py`)
   - Discovery mechanics
   - Intelligence gathering progression

## Proposed Extensible Architecture

### 1. Unified Progression Tree System

```python
# New file: progression_trees.py

class ProgressionNode:
    """
    Represents a single unlock/milestone in the progression system.
    Can represent actions, upgrades, events, mechanics, or combinations.
    """
    def __init__(self, 
                 node_id: str,
                 name: str,
                 description: str,
                 unlock_conditions: List[UnlockCondition],
                 effects: List[Effect],
                 node_type: NodeType = NodeType.FEATURE,
                 prerequisites: List[str] = None,
                 category: str = "general"):
        pass

class ProgressionTree:
    """
    Manages the complete progression system with dependency tracking.
    """
    def __init__(self):
        self.nodes = {}
        self.unlocked_nodes = set()
        self.dependency_graph = {}
    
    def register_node(self, node: ProgressionNode):
        """Add a progression node to the tree."""
        pass
    
    def check_unlocks(self, game_state):
        """Check and trigger any newly available unlocks."""
        pass
    
    def get_available_nodes(self, category: str = None):
        """Get all currently available progression nodes."""
        pass
```

### 2. Condition-Based Unlock System

```python
# Enhanced condition system

class UnlockCondition(ABC):
    """Base class for all unlock conditions."""
    @abstractmethod
    def check(self, game_state) -> bool:
        pass

class TurnCondition(UnlockCondition):
    def __init__(self, min_turn: int):
        self.min_turn = min_turn
    
    def check(self, game_state) -> bool:
        return game_state.turn >= self.min_turn

class ResourceCondition(UnlockCondition):
    def __init__(self, resource: str, min_amount: int):
        self.resource = resource
        self.min_amount = min_amount
    
    def check(self, game_state) -> bool:
        return getattr(game_state, self.resource) >= self.min_amount

class CompositeCondition(UnlockCondition):
    """Combine multiple conditions with AND/OR logic."""
    def __init__(self, conditions: List[UnlockCondition], 
                 operator: str = "AND"):
        self.conditions = conditions
        self.operator = operator
    
    def check(self, game_state) -> bool:
        if self.operator == "AND":
            return all(c.check(game_state) for c in self.conditions)
        elif self.operator == "OR":
            return any(c.check(game_state) for c in self.conditions)
```

### 3. Effect System Refactor

```python
# Unified effect system

class Effect(ABC):
    """Base class for all progression effects."""
    @abstractmethod
    def apply(self, game_state):
        pass

class ResourceEffect(Effect):
    """Add/subtract resources."""
    def __init__(self, resource: str, amount: int):
        self.resource = resource
        self.amount = amount
    
    def apply(self, game_state):
        game_state._add(self.resource, self.amount)

class UnlockActionEffect(Effect):
    """Unlock new actions."""
    def __init__(self, action_ids: List[str]):
        self.action_ids = action_ids
    
    def apply(self, game_state):
        for action_id in self.action_ids:
            game_state.unlocked_actions.add(action_id)

class EnableMechanicEffect(Effect):
    """Enable new game mechanics."""
    def __init__(self, mechanic_name: str):
        self.mechanic_name = mechanic_name
    
    def apply(self, game_state):
        setattr(game_state, f"{self.mechanic_name}_enabled", True)
```

### 4. Data-Driven Configuration

```python
# progression_config.py - Data-driven progression definitions

PROGRESSION_TREES = {
    "intelligence_operations": {
        "name": "Intelligence Operations",
        "description": "Competitive intelligence and opponent monitoring",
        "nodes": [
            {
                "id": "basic_intelligence",
                "name": "Intelligence Network",
                "unlock_conditions": [
                    TurnCondition(6),
                    ResourceCondition("reputation", 10)
                ],
                "effects": [
                    EnableMechanicEffect("scouting"),
                    UnlockActionEffect(["scout_opponents"])
                ]
            },
            {
                "id": "advanced_intelligence", 
                "name": "Advanced Intelligence",
                "prerequisites": ["basic_intelligence"],
                "unlock_conditions": [
                    ResourceCondition("reputation", 25),
                    ResourceCondition("admin_staff", 2)
                ],
                "effects": [
                    UnlockActionEffect(["deep_intelligence", "counter_intelligence"])
                ]
            }
        ]
    },
    
    "research_capabilities": {
        "name": "Research Capabilities",
        "description": "Technical research and compute infrastructure",
        "nodes": [
            {
                "id": "basic_compute",
                "name": "Compute Infrastructure",
                "unlock_conditions": [
                    TurnCondition(3)
                ],
                "effects": [
                    UnlockActionEffect(["buy_compute"])
                ]
            },
            {
                "id": "hpc_systems",
                "name": "High-Performance Computing",
                "prerequisites": ["basic_compute"],
                "unlock_conditions": [
                    ResourceCondition("compute", 30),
                    ResourceCondition("money", 800)
                ],
                "effects": [
                    UnlockUpgradeEffect(["hpc_cluster"])
                ]
            }
        ]
    }
}
```

### 5. Integration with Existing Systems

#### Phase 1: Minimal Integration
- Create progression tree system alongside existing systems
- Migrate milestone events to progression nodes
- Maintain backward compatibility

#### Phase 2: Action System Integration
- Migrate action unlock rules to progression conditions
- Unify action availability checking
- Add progression-based action modifications

#### Phase 3: Complete Integration
- Migrate upgrades to progression nodes
- Unified progression UI
- Achievement/milestone tracking

## Implementation Strategy

### Short Term (Current PR)
1. **Create design documentation** v
2. **Add progression tree infrastructure** (basic classes)
3. **Migrate opponent discovery to progression system**
4. **Create example progression tree for intelligence operations**

### Medium Term (Next PR)
1. **Migrate action unlock rules to progression system**
2. **Create unified progression checking system**
3. **Add progression tree visualization/UI**

### Long Term (Future PRs)
1. **Migrate upgrades to progression trees**
2. **Create achievement system based on progression**
3. **Add save/load for progression state**
4. **Create progression editor/configuration tools**

## Benefits of This Design

1. **Extensibility**: Easy to add new progression paths without code changes
2. **Maintainability**: Centralized progression logic instead of scattered conditions
3. **Data-Driven**: Progression trees can be defined in configuration files
4. **Testability**: Clear separation between conditions, effects, and game state
5. **Modularity**: Different progression trees can be developed independently
6. **UI Integration**: Unified system enables better progression visualization

## Example Usage

```python
# Game state initialization
progression_manager = ProgressionManager()
progression_manager.load_trees(PROGRESSION_TREES)

# Each turn, check for new unlocks
def end_turn(game_state):
    # ... existing end turn logic ...
    progression_manager.check_unlocks(game_state)
    
# Check if action is available
def is_action_available(action_id, game_state):
    return progression_manager.is_unlocked(action_id, game_state)
```

## Migration Guide

### For Developers

1. **Adding New Progression Elements**:
   - Define unlock conditions using condition classes
   - Create effects using effect classes
   - Register progression nodes in configuration
   - Test unlock flow

2. **Extending Condition Types**:
   - Inherit from UnlockCondition
   - Implement check() method
   - Add to condition registry
   - Document usage patterns

3. **Creating New Effect Types**:
   - Inherit from Effect
   - Implement apply() method
   - Handle game state modifications safely
   - Add rollback capability if needed

This design provides a solid foundation for extensible progression while maintaining compatibility with the existing P(Doom) architecture.