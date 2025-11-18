# P(Doom) Asset Generation Batch

Comprehensive list of all icons, textures, and UI elements needed to achieve visual consistency across the game. Organized for batch generation through the AI asset pipeline.

**Total New Assets Needed: ~120 items**

---

## Generation Pipeline

Use: `python tools/assets/generate_images.py`

All prompts follow the established style: **dark tech/laboratory aesthetic, cyan/blue accents, sci-fi UI feel**

---

## BATCH 1: Missing Action Icons (8 icons)

**Priority:** CRITICAL - These show as neon placeholder in game

| Asset Name | Filename | Prompt |
|------------|----------|--------|
| Network | `action_publicity_network_64.png` | Professional networking handshake icon, two stylized hands meeting, tech interface style, cyan accents, dark background, 64x64px |
| Team Building | `action_management_team_building_64.png` | Group of figures with raised arms celebrating, team spirit, simplified silhouettes, tech style, 64x64px |
| Acquire Startup | `action_strategic_acquire_startup_64.png` | Corporate acquisition icon, small building being absorbed by larger building, merger visual, tech style, 64x64px |
| Sabotage Competitor | `action_strategic_sabotage_64.png` | Corporate espionage icon, shadowy figure with mask or hood, covert operations feel, dark with red accents, 64x64px |
| Lobby Government | `action_strategic_lobby_government_64.png` | Capitol building dome with briefcase, government lobbying visual, formal style, 64x64px |
| Open Source Release | `action_publicity_open_source_64.png` | Open book or document with branching arrows, sharing/distribution visual, community feel, 64x64px |
| Take Loan | `action_funding_loan_64.png` | Money bag with chain or lock attached, debt/obligation visual, business loan icon, 64x64px |
| Grant Proposal | `action_funding_grant_proposal_64.png` | Document with official seal and checkmark, grant approval visual, formal document, 64x64px |

---

## BATCH 2: Screen Backgrounds (6 textures)

**Priority:** HIGH - Replaces solid color rectangles

| Asset Name | Filename | Prompt |
|------------|----------|--------|
| Main Background | `bg_main_tech_grid.png` | Dark laboratory interface background, subtle hexagonal grid pattern, tech aesthetic, dark blue-gray (#1a1e28) with faint cyan circuit traces, 1920x1080px, tileable |
| Welcome Background | `bg_welcome_laboratory.png` | AI laboratory control room background, dark with subtle tech elements, glowing screens in background, atmospheric, 1920x1080px |
| Settings Background | `bg_settings_panel.png` | Configuration interface background, dark steel with subtle panel lines, organized grid feel, 1920x1080px |
| Game Over Victory | `bg_gameover_victory.png` | Victory celebration background, dark with golden/green glow radiating from center, triumphant feel, 1920x1080px |
| Game Over Defeat | `bg_gameover_defeat.png` | Defeat/doom background, dark with red ominous glow, warning feel, system failure aesthetic, 1920x1080px |
| Panel Texture | `bg_panel_steel.png` | Dark brushed steel panel texture, subtle grain, slightly lighter than background (#1e2430), 512x512px tileable |

---

## BATCH 3: Resource Icons (10 icons)

**Priority:** HIGH - Top bar resource display

| Asset Name | Filename | Prompt |
|------------|----------|--------|
| Money | `resource_money_small_32.png` | Dollar sign icon, green metallic sheen, clear and bold, top bar resource, 32x32px |
| Compute | `resource_compute_small_32.png` | Computer processor chip icon, blue tech glow, circuit board style, 32x32px |
| Research | `resource_research_small_32.png` | Scientific beaker icon, purple/magenta liquid, research visual, 32x32px |
| Papers | `resource_papers_small_32.png` | Academic paper/document stack icon, orange tint, published papers, 32x32px |
| Reputation | `resource_reputation_small_32.png` | Star badge icon, gold metallic, prestige/reputation indicator, 32x32px |
| Action Points | `resource_ap_small_32.png` | Lightning bolt icon, cyan electric glow, energy/action visual, 32x32px |
| Turn Counter | `resource_turn_small_32.png` | Circular clock or calendar page icon, turn indicator, white/gray, 32x32px |
| Doom Indicator | `resource_doom_small_32.png` | Warning probability icon, red danger triangle with percentage, 32x32px |
| Safety Score | `resource_safety_small_32.png` | Shield with checkmark icon, safety metric, green tint, 32x32px |
| Morale | `resource_morale_small_32.png` | Happy face or heart icon, team morale indicator, warm colors, 32x32px |

---

## BATCH 4: UI Control Icons (20 icons)

**Priority:** HIGH - Button and control icons

| Asset Name | Filename | Prompt |
|------------|----------|--------|
| Play/Start | `ui_control_play_32.png` | Play triangle icon, start/begin action, cyan glow, 32x32px |
| Pause | `ui_control_pause_32.png` | Pause bars icon, pause action, white/cyan, 32x32px |
| Confirm/Check | `ui_control_confirm_32.png` | Checkmark icon, confirm/accept action, green tint, 32x32px |
| Cancel/X | `ui_control_cancel_32.png` | X icon, cancel/close action, red tint, 32x32px |
| Clear/Trash | `ui_control_clear_32.png` | Trash bin icon, delete/clear action, gray/red, 32x32px |
| Refresh | `ui_control_refresh_32.png` | Circular refresh arrows icon, reload action, cyan, 32x32px |
| Settings Gear | `ui_control_settings_32.png` | Gear/cog icon, settings access, metallic gray, 32x32px |
| Back Arrow | `ui_control_back_32.png` | Left arrow icon, navigation back, white/cyan, 32x32px |
| Forward Arrow | `ui_control_forward_32.png` | Right arrow icon, navigation forward, white/cyan, 32x32px |
| Up Arrow | `ui_control_up_32.png` | Up arrow icon, scroll up or increase, white/cyan, 32x32px |
| Down Arrow | `ui_control_down_32.png` | Down arrow icon, scroll down or decrease, white/cyan, 32x32px |
| Lock | `ui_control_lock_32.png` | Padlock closed icon, reserve/lock action, gold/yellow, 32x32px |
| Unlock | `ui_control_unlock_32.png` | Padlock open icon, unlock/release, gray, 32x32px |
| Plus/Add | `ui_control_add_32.png` | Plus symbol icon, add action, green tint, 32x32px |
| Minus/Remove | `ui_control_remove_32.png` | Minus symbol icon, remove action, red tint, 32x32px |
| Info | `ui_control_info_32.png` | Information 'i' icon, help/info tooltip, blue, 32x32px |
| Question | `ui_control_help_32.png` | Question mark icon, help query, blue, 32x32px |
| Bug Report | `ui_control_bug_32.png` | Bug insect icon, bug report, orange/yellow, 32x32px |
| Save | `ui_control_save_32.png` | Floppy disk icon, save action, blue, 32x32px |
| Load | `ui_control_load_32.png` | Folder with arrow icon, load action, blue, 32x32px |

---

## BATCH 5: Status & Alert Icons (12 icons)

**Priority:** MEDIUM - Message log and notifications

| Asset Name | Filename | Prompt |
|------------|----------|--------|
| Info Alert | `indicator_status_info_24.png` | Information circle icon, blue 'i' in circle, informational, 24x24px |
| Success Alert | `indicator_status_success_24.png` | Success checkmark circle, green check in circle, positive, 24x24px |
| Warning Alert | `indicator_status_warning_24.png` | Warning triangle icon, yellow/orange exclamation triangle, caution, 24x24px |
| Error Alert | `indicator_status_error_24.png` | Error X circle icon, red X in circle, negative/error, 24x24px |
| Neutral | `indicator_status_neutral_24.png` | Neutral dot icon, gray circle, no status, 24x24px |
| Pending | `indicator_status_pending_24.png` | Hourglass or clock icon, waiting/pending state, amber, 24x24px |
| Active | `indicator_status_active_24.png` | Glowing dot icon, active state indicator, green pulse, 24x24px |
| Inactive | `indicator_status_inactive_24.png` | Hollow circle icon, inactive state, gray outline, 24x24px |
| Doom Rising | `indicator_doom_rising_24.png` | Up arrow with danger, doom increasing, red glow, 24x24px |
| Doom Falling | `indicator_doom_falling_24.png` | Down arrow with safe, doom decreasing, green glow, 24x24px |
| Doom Stable | `indicator_doom_stable_24.png` | Horizontal line or equals, doom stable, yellow, 24x24px |
| Critical | `indicator_status_critical_24.png` | Flashing warning icon, critical state, red pulsing, 24x24px |

---

## BATCH 6: Settings Section Icons (8 icons)

**Priority:** MEDIUM - Settings menu categories

| Asset Name | Filename | Prompt |
|------------|----------|--------|
| Audio Settings | `ui_settings_audio_32.png` | Speaker with sound waves icon, audio settings, white/cyan, 32x32px |
| Graphics Settings | `ui_settings_graphics_32.png` | Monitor or display icon, graphics settings, white/cyan, 32x32px |
| Gameplay Settings | `ui_settings_gameplay_32.png` | Game controller icon, gameplay settings, white/cyan, 32x32px |
| Theme Settings | `ui_settings_theme_32.png` | Color palette icon, UI theme settings, colorful, 32x32px |
| Controls Settings | `ui_settings_controls_32.png` | Keyboard icon, keybindings, white/cyan, 32x32px |
| Accessibility | `ui_settings_accessibility_32.png` | Universal access icon, accessibility options, blue, 32x32px |
| Account | `ui_settings_account_32.png` | User profile icon, account settings, white, 32x32px |
| Reset Defaults | `ui_settings_reset_32.png` | Reset/undo arrow icon, restore defaults, orange, 32x32px |

---

## BATCH 7: Leaderboard & Rankings (8 icons)

**Priority:** MEDIUM - Competition and scoring

| Asset Name | Filename | Prompt |
|------------|----------|--------|
| Trophy | `ui_leaderboard_trophy_32.png` | Trophy cup icon, championship/leaderboard, gold metallic, 32x32px |
| Gold Medal | `ui_rank_gold_32.png` | Gold medal with ribbon, 1st place, shiny gold, 32x32px |
| Silver Medal | `ui_rank_silver_32.png` | Silver medal with ribbon, 2nd place, shiny silver, 32x32px |
| Bronze Medal | `ui_rank_bronze_32.png` | Bronze medal with ribbon, 3rd place, shiny bronze, 32x32px |
| Crown | `ui_rank_crown_32.png` | Royal crown icon, top rank indicator, gold, 32x32px |
| Filter | `ui_leaderboard_filter_32.png` | Funnel filter icon, filter options, gray/cyan, 32x32px |
| Sort Ascending | `ui_leaderboard_sort_asc_32.png` | Sort ascending icon, A-Z or low-high, white, 32x32px |
| Sort Descending | `ui_leaderboard_sort_desc_32.png` | Sort descending icon, Z-A or high-low, white, 32x32px |

---

## BATCH 8: Guide & Help Icons (8 icons)

**Priority:** MEDIUM - Player guide sections

| Asset Name | Filename | Prompt |
|------------|----------|--------|
| Objective | `ui_guide_objective_32.png` | Target/bullseye icon, game objective, red/white, 32x32px |
| Controls | `ui_guide_controls_32.png` | Keyboard keys icon, control instructions, white, 32x32px |
| Resources | `ui_guide_resources_32.png` | Money bag or treasure icon, resources section, yellow, 32x32px |
| Strategy | `ui_guide_strategy_32.png` | Chess knight piece icon, strategy tips, white, 32x32px |
| Actions | `ui_guide_actions_32.png` | Hand clicking icon, actions guide, cyan, 32x32px |
| Tips | `ui_guide_tips_32.png` | Lightbulb icon, tips and hints, yellow glow, 32x32px |
| Warning | `ui_guide_warning_32.png` | Exclamation icon, important warnings, orange, 32x32px |
| Book/Manual | `ui_guide_book_32.png` | Open book icon, full guide reference, white, 32x32px |

---

## BATCH 9: Difficulty & Mode Icons (6 icons)

**Priority:** MEDIUM - Game configuration

| Asset Name | Filename | Prompt |
|------------|----------|--------|
| Easy | `ui_difficulty_easy_32.png` | Green shield icon, easy difficulty, protective, 32x32px |
| Standard | `ui_difficulty_standard_32.png` | Blue balanced scales icon, standard difficulty, balanced, 32x32px |
| Hard | `ui_difficulty_hard_32.png` | Red warning skull or danger icon, hard difficulty, challenging, 32x32px |
| Randomize | `ui_config_random_32.png` | Dice icon, randomize option, white with colored pips, 32x32px |
| Seed | `ui_config_seed_32.png` | Plant seed or key icon, seed configuration, green/gold, 32x32px |
| Calendar | `ui_config_date_32.png` | Calendar page icon, date selector, white, 32x32px |

---

## BATCH 10: Panel Frames & Decorative (10 textures)

**Priority:** MEDIUM - Panel styling

| Asset Name | Filename | Prompt |
|------------|----------|--------|
| Panel Frame Top | `ui_frame_top_256.png` | Horizontal panel frame top edge, tech style, blue accent line, beveled, 256x16px |
| Panel Frame Bottom | `ui_frame_bottom_256.png` | Horizontal panel frame bottom edge, matching top, 256x16px |
| Panel Frame Left | `ui_frame_left_256.png` | Vertical panel frame left edge, tech style, blue accent, 16x256px |
| Panel Frame Right | `ui_frame_right_256.png` | Vertical panel frame right edge, matching left, 16x256px |
| Corner TL | `ui_frame_corner_tl_32.png` | Panel corner top-left, tech frame corner piece, 32x32px |
| Corner TR | `ui_frame_corner_tr_32.png` | Panel corner top-right, tech frame corner piece, 32x32px |
| Corner BL | `ui_frame_corner_bl_32.png` | Panel corner bottom-left, tech frame corner piece, 32x32px |
| Corner BR | `ui_frame_corner_br_32.png` | Panel corner bottom-right, tech frame corner piece, 32x32px |
| Separator Horizontal | `ui_separator_h_256.png` | Horizontal separator line, tech style, cyan glow center, 256x4px |
| Separator Vertical | `ui_separator_v_256.png` | Vertical separator line, tech style, cyan glow center, 4x256px |

---

## BATCH 11: Doom Meter Visuals (6 textures)

**Priority:** MEDIUM - Doom meter enhancement

| Asset Name | Filename | Prompt |
|------------|----------|--------|
| Doom Ring Frame | `doom_meter_frame_256.png` | Circular meter frame, tech interface ring, dark steel with subtle markings, 256x256px |
| Doom Background Safe | `doom_bg_safe_256.png` | Radial gradient background, green safe zone, subtle, 256x256px |
| Doom Background Warning | `doom_bg_warning_256.png` | Radial gradient background, yellow warning zone, subtle, 256x256px |
| Doom Background Danger | `doom_bg_danger_256.png` | Radial gradient background, orange danger zone, subtle, 256x256px |
| Doom Background Critical | `doom_bg_critical_256.png` | Radial gradient background, red critical zone, pulsing glow feel, 256x256px |
| Doom Glow Effect | `doom_glow_effect_128.png` | Soft glow texture for doom meter edge, red/orange gradient, 128x128px |

---

## BATCH 12: Event & Dialog Visuals (8 icons)

**Priority:** LOW - Event system enhancement

| Asset Name | Filename | Prompt |
|------------|----------|--------|
| Event Generic | `event_generic_48.png` | Generic event icon, document with exclamation, neutral, 48x48px |
| Event Opportunity | `event_opportunity_48.png` | Opportunity event icon, rising sun or door opening, positive, 48x48px |
| Event Crisis | `event_crisis_48.png` | Crisis event icon, alarm or emergency bell, urgent red, 48x48px |
| Event Discovery | `event_discovery_48.png` | Discovery event icon, lightbulb or eureka, yellow glow, 48x48px |
| Event Deadline | `event_deadline_48.png` | Deadline event icon, clock with warning, time pressure, 48x48px |
| Event External | `event_external_48.png` | External event icon, globe or outside arrow, world events, 48x48px |
| Choice Positive | `event_choice_positive_32.png` | Positive choice icon, thumbs up or checkmark, green, 32x32px |
| Choice Negative | `event_choice_negative_32.png` | Negative choice icon, thumbs down or warning, red, 32x32px |

---

## BATCH 13: Upgrade Icons (10 icons)

**Priority:** LOW - Upgrade system

| Asset Name | Filename | Prompt |
|------------|----------|--------|
| Cost Reduction | `upgrade_cost_reduction_32.png` | Downward price arrow icon, cost savings, green, 32x32px |
| Speed Increase | `upgrade_speed_increase_32.png` | Speedometer or lightning bolt, faster processing, cyan, 32x32px |
| Quality Boost | `upgrade_quality_boost_32.png` | Star with up arrow, quality improvement, gold, 32x32px |
| Capacity Expand | `upgrade_capacity_expand_32.png` | Expanding box icon, increased capacity, blue, 32x32px |
| Efficiency | `upgrade_efficiency_32.png` | Gear with checkmark, efficiency improvement, green, 32x32px |
| Automation | `upgrade_automation_32.png` | Robot arm or cog chain, automation upgrade, cyan, 32x32px |
| Network | `upgrade_network_32.png` | Connected nodes icon, network upgrade, blue, 32x32px |
| Security | `upgrade_security_32.png` | Shield with lock icon, security upgrade, gold, 32x32px |
| Research Boost | `upgrade_research_32.png` | Beaker with up arrow, research speed, purple, 32x32px |
| Morale Boost | `upgrade_morale_32.png` | Smiley with up arrow, morale improvement, yellow, 32x32px |

---

## BATCH 14: Scrollbar & Slider Components (6 textures)

**Priority:** LOW - UI polish

| Asset Name | Filename | Prompt |
|------------|----------|--------|
| Scrollbar Track V | `ui_scrollbar_track_v_16.png` | Vertical scrollbar track, dark groove, tech style, 16x128px |
| Scrollbar Track H | `ui_scrollbar_track_h_16.png` | Horizontal scrollbar track, dark groove, tech style, 128x16px |
| Scrollbar Thumb V | `ui_scrollbar_thumb_v_16.png` | Vertical scrollbar thumb, cyan accent, draggable feel, 16x32px |
| Scrollbar Thumb H | `ui_scrollbar_thumb_h_16.png` | Horizontal scrollbar thumb, cyan accent, draggable, 32x16px |
| Slider Track | `ui_slider_track_16.png` | Horizontal slider track, groove style, dark with cyan edge, 128x16px |
| Slider Thumb | `ui_slider_thumb_24.png` | Slider thumb/handle, cyan glow knob, draggable, 24x24px |

---

## Summary

### Total by Batch:
1. Missing Action Icons: 8
2. Screen Backgrounds: 6
3. Resource Icons: 10
4. UI Control Icons: 20
5. Status & Alert Icons: 12
6. Settings Section Icons: 8
7. Leaderboard & Rankings: 8
8. Guide & Help Icons: 8
9. Difficulty & Mode Icons: 6
10. Panel Frames & Decorative: 10
11. Doom Meter Visuals: 6
12. Event & Dialog Visuals: 8
13. Upgrade Icons: 10
14. Scrollbar & Slider Components: 6

**TOTAL: 126 new assets**

### Priority Order:
1. **CRITICAL**: Batch 1 (8) - Missing action icons showing placeholder
2. **HIGH**: Batches 2-4 (36) - Backgrounds, resources, controls
3. **MEDIUM**: Batches 5-11 (54) - Status, settings, leaderboard, guides, frames, doom
4. **LOW**: Batches 12-14 (28) - Events, upgrades, scrollbars

### Estimated Generation Time:
- ~3 seconds per icon (API generation)
- ~6-7 minutes for all 126 assets
- Plus selection and promotion time

---

## Usage

```bash
# Generate all assets in batch
cd tools/assets
python generate_images.py --batch ASSET_GENERATION_BATCH.md

# Or generate specific batch
python generate_images.py --batch 1  # Missing actions only
```

---

*Created: 2025-11-18*
*For: P(Doom) Godot Game*
