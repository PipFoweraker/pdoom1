# Enhancement: Advanced Menu Consolidation

**Priority**: Medium  
**Epic**: Menu System Improvements  
**Estimated Effort**: 2-3 sessions

## Overview
Build on the successful fundraising and research dialog patterns to consolidate additional action groups into strategic submenus.

## Target Action Groups for Consolidation

### 1. Staff Management Menu
Currently scattered actions:
- 'Hire Staff' (already dialog-based)
- 'Fire Staff' (if exists)
- 'Training Programs' 
- 'Staff Morale Initiatives'

**Proposed**: 'Staff Options' submenu with hiring, management, and development choices.

### 2. Upgrade & Technology Menu  
Currently scattered actions:
- 'Buy Compute'
- 'Better Computers'
- 'Research Automation'
- 'HPC Cluster'
- Various other upgrades

**Proposed**: 'Technology Options' submenu with infrastructure and upgrade paths.

### 3. External Relations Menu
Currently scattered actions:
- 'Scout Opponents'  
- 'Public Relations'
- 'Industry Networking'
- 'Government Relations'

**Proposed**: 'External Affairs' submenu for all outward-facing strategic actions.

## Technical Implementation

### Reuse Dialog Framework
- Extend existing dialog system from fundraising/research
- Consistent UI patterns and interaction models
- Shared keyboard navigation and modal behavior

### Progressive Unlocks
- Apply progressive unlock pattern (like Quality Research)
- Unlock advanced options based on milestones, reputation, or previous actions
- Create meaningful advancement progression

### Strategic Depth
- Each submenu should offer meaningful choices with trade-offs
- Avoid simply grouping actions without strategic consideration
- Include risk/reward profiles and long-term consequences

## Benefits
- **Cleaner UI**: Fewer top-level actions, better organization
- **Strategic Focus**: Players make conscious choices rather than clicking available actions
- **Scalability**: Easy to add new options within existing menus
- **Consistency**: Unified interaction patterns across all menus

## Implementation Phases
1. **Phase 1**: Identify and catalog all current actions by category
2. **Phase 2**: Design submenu structures with strategic considerations
3. **Phase 3**: Implement Staff Options submenu (lowest risk)
4. **Phase 4**: Implement Technology Options submenu
5. **Phase 5**: Implement External Affairs submenu

## Success Metrics
- Reduced number of top-level actions by 60%+
- Maintained or improved strategic depth
- Consistent user experience across all dialog systems
- No regression in game performance or usability

## Dependencies
- Current dialog framework (completed in v0.4.0)
- UI layout system accommodating fewer action buttons
- Sound system integration for dialog interactions

## Future Extensions
- **Dynamic Menus**: Menu options that change based on game state
- **Nested Submenus**: Multi-level menu hierarchies for complex systems  
- **Context-Aware Options**: Different choices available in different game phases
- **Visual Previews**: Show potential outcomes before selection
