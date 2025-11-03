# Contributing Guidelines

## Multi-Repository Integration Guidelines

### Cross-Repository Documentation Standards
- **Shared Documentation**: All documentation intended for multiple repositories must be placed in `docs/shared/`
- **ASCII-Only Content**: All documentation must use ASCII characters only for maximum compatibility
- **Sync Markers**: Include sync test markers in shared documents to validate automation
- **Hub-and-Spoke Architecture**: pdoom1 repository is the source of truth for all shared documentation

### Version Management Requirements  
- **Semantic Versioning**: All releases must follow semantic versioning (MAJOR.MINOR.PATCH)
- **GitHub Releases**: Use GitHub releases with proper tags for automatic website sync
- **Version Consistency**: Ensure version alignment across all repositories in the ecosystem
- **Changelog Integration**: All version changes must be documented in CHANGELOG.md

### Automation Workflow Standards
- **Token Authentication**: All cross-repository automation must use secure token authentication
- **Workflow Testing**: Test all GitHub Actions workflows before production deployment
- **Error Handling**: Include comprehensive error handling and retry logic in automation
- **Status Monitoring**: Maintain status dashboards and health checks for all automated processes

### Quality Assurance Rules
- **Documentation Sync**: Verify documentation synchronization after all shared content changes
- **Version Compatibility**: Validate version compatibility matrices for all ecosystem integrations
- **Schema Validation**: Use schema validation for all data batch integrations
- **Rollback Procedures**: Maintain documented rollback procedures for all automated systems

## Table of Contents
- [Multi-Repository Integration Guidelines](#multi-repository-integration-guidelines) (Line 13)  
- [Copilot and Automation Instructions](#copilot-and-automation-instructions) (Line 25)
- [UI Enhancement Development Protocols](#ui-enhancement-development-protocols) (Line 33)
  - [Keyboard Shortcut Implementation](#keyboard-shortcut-implementation) (Line 37)
  - [Action Point (AP) Feedback System](#action-point-ap-feedback-system) (Line 44)
  - [Employee Blob Positioning](#employee-blob-positioning) (Line 50)
  - [Testing Requirements](#testing-requirements) (Line 56)
  - [Sound Integration](#sound-integration) (Line 62)
  - [Documentation Updates](#documentation-updates) (Line 68)

## Copilot and Automation Instructions

- Always install dependencies (`pip install -r requirements.txt`) before running code or tests.
- The `main` branch is stable and does not need runtime bug checks for every PR.
- Always include `import pygame` at the start of any Python file that uses pygame.
- Only update documentation files (README.md, PLAYERGUIDE.md) if there are user-facing changes.
- When updating DEVELOPERGUIDE.md, it's okay to be verbose and include a table of contents.
- The game includes enhanced user experience systems like contextual end game scenarios that provide rich feedback instead of generic messages.

## UI Enhancement Development Protocols

When implementing UI and visual feedback enhancements, follow these protocols:

### Keyboard Shortcut Implementation
- **Mapping**: Use 1-9 keys for first 9 actions in action list
- **Visual Integration**: Display shortcuts as '[N] Action Name' on buttons  
- **Error Handling**: Provide clear error messages for insufficient resources/AP
- **Validation**: Use `execute_action_by_keyboard()` method with full validation
- **Sound Feedback**: Play `play_ap_spend_sound()` on successful action execution

### Action Point (AP) Feedback System
- **Visual Feedback**: Set `ap_glow_timer = 30` for 30-frame glow effect
- **Audio Feedback**: Use `SoundManager.play_ap_spend_sound()` for AP spend
- **Error Tracking**: Use `track_error()` method for easter egg detection  
- **Button States**: Update button states to reflect AP availability

### Employee Blob Positioning
- **Safe Zones**: Use `_calculate_blob_position()` to avoid UI overlap
- **Screen Responsive**: Scale positions with screen dimensions (w, h parameters)
- **Grid Layout**: Automatic grid arrangement within safe zones
- **Animation**: Support smooth transitions for blob movement

### Testing Requirements
- **Keyboard Tests**: Test all shortcut keys with valid/invalid conditions
- **AP Feedback Tests**: Verify visual and audio feedback triggering
- **Blob Position Tests**: Validate safe zone positioning and screen scaling
- **Error Handling Tests**: Test easter egg system and error tracking

### Sound Integration
- **Sound Manager**: Use existing `SoundManager` class for audio feedback
- **Error Beeps**: Use `play_error_beep()` for easter egg system
- **AP Sounds**: Use `play_ap_spend_sound()` for Action Point feedback
- **Headless Testing**: Ensure sound systems work in headless environments

### Documentation Updates
- **DEVELOPERGUIDE.md**: Add verbose technical details and code examples
- **PLAYERGUIDE.md**: Update controls section with keyboard shortcuts
- **Test Coverage**: Document all new test cases and their purposes

### Productive Actions System
When adding or editing employee productive actions, follow these guidelines:

**Action Design Principles:**
- **Balanced Bonuses**: Keep effectiveness bonuses between 1.06 (6%) and 1.18 (18%)
- **Clear Requirements**: Use specific, measurable requirements (compute, reputation, staff counts)
- **Logical Progression**: Higher bonuses should require more substantial organizational development
- **Thematic Consistency**: Actions should match employee specialization and organizational stage

**Implementation Requirements:**
- **Clear Logging**: Always provide descriptive failure reasons for unmet requirements
- **Graceful Degradation**: Apply 10% penalty (0.9 multiplier) when requirements aren't met
- **Requirement Validation**: Test all requirement types with edge cases (zero values, high values)
- **Category Mapping**: Ensure all employee subtypes map to appropriate action categories

**Testing Standards:**
- **Requirement Testing**: Test all combinations of met/unmet requirements  
- **Bonus Calculation**: Verify productivity bonuses apply correctly to research generation
- **Integration Testing**: Test with various game state scenarios (early/mid/late game)
- **Message Validation**: Ensure logging output is clear and not spammy

**Code Quality:**
- **Descriptive Names**: Use clear action names that immediately convey purpose
- **Comprehensive Descriptions**: Write detailed descriptions explaining the action's impact
- **Consistent Structure**: Follow the established pattern in `PRODUCTIVE_ACTIONS` 
- **Documentation**: Update DEVELOPERGUIDE.md extension points when adding new requirement types

Cheers!