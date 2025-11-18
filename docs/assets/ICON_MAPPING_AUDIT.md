# Icon Mapping Audit

This document provides a complete audit of all game actions and their icon mappings, identifying gaps and mismatches.

## Summary

- **Total 64px Icons Generated**: 91
- **Icons Used in Mapping**: 36
- **Icons Unused (Available)**: 55
- **Icons Needing Generation**: 8

### Action Breakdown
- **Main Action Buttons**: 7 actions + 3 submenus (Hire, Fundraise, Publicity) + 1 Strategic submenu
- **Submenu Actions**: 18 total (5 hiring + 4 fundraising + 5 publicity + 4 strategic)

## Main Action Buttons

| Action ID | Display Name | Icon Status | Icon Path/Notes |
|-----------|-------------|-------------|-----------------|
| `hire_staff` | Hire Staff | Mapped | `buttons_normal/button_hire_normal_64.png` |
| `buy_compute` | Purchase Compute | Mapped | `actions_facilities/action_facility_upgrade_compute_64.png` |
| `safety_research` | Safety Research | Mapped | `actions_research/action_research_alignment_64.png` |
| `capability_research` | Capability Research | Mapped | `actions_research/action_research_capability_control_64.png` |
| `publish_paper` | Publish Safety Paper | Mapped | `actions_research/action_research_formal_verification_64.png` |
| `fundraise` | Fundraising | Mapped | `resources/resource_money_64.png` |
| `publicity` | Publicity | Mapped | `actions_policies/action_policy_transparency_64.png` |
| `strategic` | Strategic | Mapped | `actions_facilities/action_facility_emergency_shutdown_64.png` |
| `team_building` | Team Building | **NEEDS GENERATION** | Group celebration icon needed |
| `audit_safety` | Safety Audit | Mapped | `employee_roles/employee_role_auditor_64.png` |

## Hiring Submenu Options

| Action ID | Display Name | Icon Status | Icon Path |
|-----------|-------------|-------------|-----------|
| `hire_safety_researcher` | Safety Researcher | Mapped | `employee_roles/employee_role_safety_specialist_64.png` |
| `hire_capability_researcher` | Capability Researcher | Mapped | `employee_roles/employee_role_researcher_64.png` |
| `hire_compute_engineer` | Compute Engineer | Mapped | `employee_roles/employee_role_engineer_64.png` |
| `hire_manager` | Manager | Mapped | `employee_roles/employee_role_manager_64.png` |
| `hire_ethicist` | AI Ethicist | Mapped | `employee_roles/employee_role_ethicist_64.png` |

## Fundraising Submenu Options

| Action ID | Display Name | Icon Status | Icon Path/Notes |
|-----------|-------------|-------------|-----------------|
| `fundraise_small` | Modest Funding Round | Mapped | `resources/resource_money_64.png` (shared with main) |
| `fundraise_big` | Major Funding Round | Mapped | `main_navigation/ui_budget_finance_64.png` |
| `take_loan` | Business Loan | **NEEDS GENERATION** | Money bag with chain icon needed |
| `apply_grant` | Research Grant | Mapped | `resources/resource_research_points_64.png` |

## Publicity Submenu Options

| Action ID | Display Name | Icon Status | Icon Path/Notes |
|-----------|-------------|-------------|-----------------|
| `network` | Networking | **NEEDS GENERATION** | Handshake icon needed |
| `media_campaign` | Media Campaign | Mapped | `actions_policies/action_policy_transparency_64.png` |
| `lobby_government` | Lobby Government | **NEEDS GENERATION** | Capitol building icon needed |
| `release_warning` | Public Warning | Mapped | `alert_indicators/indicator_alert_warning_64.png` |
| `open_source_release` | Open Source Tools | **NEEDS GENERATION** | Open book with arrows icon needed |

## Strategic Submenu Options

| Action ID | Display Name | Icon Status | Icon Path/Notes |
|-----------|-------------|-------------|-----------------|
| `acquire_startup` | Acquire AI Startup | **NEEDS GENERATION** | Corporate acquisition icon needed |
| `sabotage_competitor` | Corporate Espionage | **NEEDS GENERATION** | Shadowy figure/espionage icon needed |
| `emergency_pivot` | Emergency Pivot | Mapped | `actions_facilities/action_facility_emergency_shutdown_64.png` |
| `grant_proposal` | Write Grant Proposal | **NEEDS GENERATION** | Document with seal icon needed |

## Resource Icons (Top Bar)

| Resource | Icon Status | Icon Path |
|----------|-------------|-----------|
| Money | Mapped | `resources/resource_money_64.png` |
| Compute | Mapped | `resources/resource_compute_64.png` |
| Research | Mapped | `resources/resource_research_points_64.png` |
| Papers | Mapped | `actions_research/action_research_formal_verification_64.png` |
| Reputation | Mapped | `resources/resource_reputation_64.png` |
| Action Points | Mapped | `resources/resource_action_points_64.png` |

## Icons Needing Generation

### Priority 1 - Currently Visible as Placeholder

1. **team_building** - Group celebration/team spirit
2. **network** - Handshake, professional networking

### Priority 2 - Strategic Actions

3. **acquire_startup** - Corporate acquisition (building absorption)
4. **sabotage_competitor** - Espionage/shadowy figure
5. **lobby_government** - Capitol building with briefcase
6. **open_source_release** - Open book with branching arrows

### Priority 3 - Fundraising Options

7. **take_loan** - Money bag with chain/lock
8. **grant_proposal** - Document with official seal

## Unused Generated Assets (55 icons)

The following icon categories have been generated but are not yet mapped to game actions.

Run `python tools/assets/audit_icons.py` for the latest inventory.

### Actions - Facilities (4 icons)
- `action_facility_build_lab_64.png`
- `action_facility_data_center_64.png`
- `action_facility_expand_office_64.png`
- `action_facility_security_upgrade_64.png`

*Potential use: Infrastructure upgrades, facility expansion actions*

### Actions - Policies (5 icons)
- `action_policy_audit_requirement_64.png`
- `action_policy_capability_limit_64.png`
- `action_policy_ethics_board_64.png`
- `action_policy_international_cooperation_64.png`
- `action_policy_whistleblower_64.png`

*Potential use: Governance actions, regulatory compliance*

### Actions - Research (5 icons)
- `action_research_interpretability_64.png`
- `action_research_ml_fundamentals_64.png`
- `action_research_monitoring_64.png`
- `action_research_red_teaming_64.png`
- `action_research_robustness_64.png`

*Potential use: Advanced research specializations*

### Button States (17 icons)
**Normal (5):** action, cancel, confirm, fire, upgrade
**Hover (6):** action, cancel, confirm, fire, hire, upgrade
**Disabled (6):** action, cancel, confirm, fire, hire, upgrade

*Potential use: Replace/supplement ThemeManager button styling*

### Employee Roles (2 icons)
- `employee_role_bureaucrat_64.png`
- `employee_role_security_64.png`

*Potential use: Additional hireable roles*

### Employee Status (8 icons)
- `employee_status_absent_64.png`
- `employee_status_active_64.png`
- `employee_status_burned_out_64.png`
- `employee_status_compromised_64.png`
- `employee_status_excellent_64.png`
- `employee_status_investigating_64.png`
- `employee_status_stressed_64.png`
- `employee_status_training_64.png`

*Potential use: Employee screen status indicators*

### Main Navigation (9 icons)
- `ui_alerts_incidents_64.png`
- `ui_governance_oversight_64.png`
- `ui_home_hq_64.png`
- `ui_infrastructure_facilities_64.png`
- `ui_research_tech_64.png`
- `ui_risk_meter_pdoom_64.png`
- `ui_save_archive_64.png`
- `ui_staff_management_64.png`
- `ui_system_settings_64.png`

*Potential use: Tab buttons, menu navigation, settings*

### Resources (5 icons)
- `resource_data_64.png`
- `resource_morale_64.png`
- `resource_power_64.png`
- `resource_safety_score_64.png`
- `resource_space_64.png`

*Potential use: Additional resource types, employee metrics*

### Decorative Elements (mapped but unused in UI)
Corners (4), dividers (2), frames (1), headers (1)

*Potential use: Panel decorations, UI polish*

### Risk Indicators (mapped but unused in UI)
All 5 risk levels mapped in icon_mapping.json but not actively displayed

*Potential use: Doom meter visualization, action risk warnings*

### Alert Indicators (mapped but unused in UI)
Info, warning, error, success - mapped but only warning is actively used

*Potential use: Notification system, message log, event feedback*

## Naming Convention

### Action Icons
```
action_{category}_{specific_action}_64.png
```
Examples:
- `action_research_alignment_64.png`
- `action_facility_upgrade_compute_64.png`
- `action_policy_transparency_64.png`

### Employee Icons
```
employee_role_{role}_64.png
employee_status_{status}_64.png
```

### Resource Icons
```
resource_{resource_name}_64.png
```

### UI/Navigation Icons
```
ui_{purpose}_{detail}_64.png
```

### Indicator Icons
```
indicator_{type}_{state}_64.png
```

## File Locations

- **Icon assets**: `godot/assets/icons/`
- **Icon mapping**: `godot/data/icon_mapping.json`
- **IconLoader autoload**: `godot/autoload/icon_loader.gd`
- **Audit script**: `tools/assets/audit_icons.py`

## Action ID to Display Name Mapping

For reference when generating prompts or documentation:

| Action ID | User-Facing Name |
|-----------|-----------------|
| `hire_staff` | Hire Staff |
| `hire_safety_researcher` | Safety Researcher |
| `hire_capability_researcher` | Capability Researcher |
| `hire_compute_engineer` | Compute Engineer |
| `hire_manager` | Manager |
| `hire_ethicist` | AI Ethicist |
| `buy_compute` | Purchase Compute |
| `safety_research` | Safety Research |
| `capability_research` | Capability Research |
| `publish_paper` | Publish Safety Paper |
| `fundraise` | Fundraising |
| `fundraise_small` | Modest Funding Round |
| `fundraise_big` | Major Funding Round |
| `take_loan` | Business Loan |
| `apply_grant` | Research Grant |
| `publicity` | Publicity |
| `network` | Networking |
| `media_campaign` | Media Campaign |
| `lobby_government` | Lobby Government |
| `release_warning` | Public Warning |
| `open_source_release` | Open Source Tools |
| `team_building` | Team Building |
| `audit_safety` | Safety Audit |
| `acquire_startup` | Acquire AI Startup |
| `sabotage_competitor` | Corporate Espionage |
| `emergency_pivot` | Emergency Pivot |
| `grant_proposal` | Write Grant Proposal |

| `strategic` | Strategic |

---

*Last updated: 2025-11-18*
*Audit script: `python tools/assets/audit_icons.py`*
