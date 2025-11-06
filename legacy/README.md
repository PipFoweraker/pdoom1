# Legacy Python Prototype

This directory contains the original Python prototype game logic that was designed for a pygame/Godot bridge architecture.

## Status: ARCHIVED

**This code is no longer actively used.** The game is being rebuilt natively in Godot using GDScript.

## What's Here

- `shared/core/game_logic.py` - Original game logic with engine interface abstraction
- `shared/core/actions_engine.py` - Python action system
- `shared/core/events_engine.py` - Python event system
- `shared/features/` - Prototype features (achievements, economic cycles, etc.)

## Why Archived?

The bridge architecture added complexity without benefits. Godot is now the primary engine, with all game logic implemented natively in GDScript for:
- Faster iteration
- Better performance
- Simpler debugging
- Native Godot integration

## Historical Reference

This code remains as reference for:
- Original game design intent
- Feature ideas to port to Godot
- Comparison of Python vs GDScript implementations

---
*Archived: 2025-10-31*
*Godot native development begins with Phase 5*
