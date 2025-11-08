# Deprecated Pygame Development Tools

**Status:** DEPRECATED as of v0.10.2 (2025-11-08)
**Reason:** PDoom migrated from Pygame to Godot engine

## Deprecated Tools

The following tools were designed for the legacy Pygame implementation and are no longer maintained:

### Dev Tools (require `src/core/game_state.py`)
- `tools/dev_tool.py` - Legacy dev testing tool
- `tools/demo_context_aware_buttons.py` - Pygame UI demo
- `tools/dev/dev_tool.py` - Developer testing utilities
- `tools/dev/dev_tool_testing.py` - Dev tool test suite
- `tools/dev/demo_technical_failures.py` - Technical failures demo
- `tools/dev/demo_settings.py` - Settings system demo
- `tools/dev/party_demo.py` - Party mode demo

## Replacement

For Godot development and testing, use:

- **Godot Dev Tools**: [godot/tools/](godot/tools/)
- **GUT Testing Framework**: [godot/test/](godot/test/)
- **Build Scripts**: [scripts/build_all_platforms.py](scripts/build_all_platforms.py)

## Archive Location

Deprecated Pygame code has been moved to:
- `archive/legacy-pygame/` - Full Pygame game implementation
- `archive/legacy-python-src/` - Python source code (`src/`)

## Migration Notes

If you need functionality from these tools:

1. Check if equivalent exists in Godot tools
2. Port logic to GDScript if needed
3. Consider if Python automation script is more appropriate

## Preservation

These tools are preserved in the archive for:
- Historical reference
- Game logic archaeology
- Potential algorithm extraction
- Understanding design decisions

**Do not run these tools** - they will fail with missing dependencies after `src/` is archived.
