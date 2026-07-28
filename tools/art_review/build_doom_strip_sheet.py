#!/usr/bin/env python3
"""Generate art_generated/doom_strip_sheet.html -- ADR-0015 doom-strip triage
sheet (issue #949 lane, "Tuesday" S-ticket).

Rapid-fire design-triage sheet over the ~50 INERT literal `doom` fields the
ADR-0015 strip will re-author. Reuses the art_review house style
(review_style.py) for the same rapid yes/no cadence the art sheets give Pip,
but the cells are DATA fields, not images: each cell shows the event id +
option label, the option's player-facing text, the current doom value, the
surrounding effect keys (so Pip can see what else the option already does),
the file:keypath, and the SCOUT'S SUGGESTED disposition as a plain label --
a suggestion to confirm or override, never pre-applied as a tag.

Pip's ruling (2026-07-27): fields get UPLIFTED to systemic streams, not
deleted by default. The verdict chips are therefore stream targets:

    uplift-overhang     -- capability/publishing pressure -> overhang stream
    uplift-alarm        -- public disclosure/awareness -> global_alarm stream
    uplift-political     -- regulation/governance -> political_pressure stream
    uplift-panic         -- acute shock/crisis -> panic stream
    uplift-absorption    -- safety org capacity -> safety_absorption stream
    uplift-rival-delay   -- rival intel/sabotage -> rival frontier delay
    drop                  -- delete outright (no systemic replacement)
    keep                  -- leave as-is (start-config carve-outs etc)
    discuss               -- contradicts the systemic model or is otherwise
                             ambiguous; needs a design call before either
                             uplift or drop

SCOPE (source: scout inventory, ADR0015_STRIP_INVENTORY.md):

  * 46 INERT fields: core_events.json (40) + historical_timeline/2017.json
    option effects (4) + scenarios/crisis.json option effects (2). These are
    the fields whose value flows through Resources.add() -> state.doom, then
    gets CLOBBERED every resolve by state.doom = doom_system.current_doom
    (turn_manager.gd:657) -- re-authoring them is a pure no-op on balance.
  * +1 variable_mapping.json default_effects.legendary.doom.
  * +3 events/overrides/example.json template entries (the explicit
    copy-me file loaded by NOTHING -- the worst ADR-0016 copy-paste trap).
  * +5 2017.json dead `game_effect.doom_increase/doom_decrease` fields (a
    DIFFERENT, entirely-unread key the historical-timeline loader never
    touches -- distinct from the 4 inert `options[].effects.doom` fields
    above, which the engine DOES resolve, just clobbers after).

  Total: 46 + 1 + 3 + 5 = 55 cells.

EXCLUDED ON PURPOSE: the 20 LIVE risk_events.json pool fields. Those flow
through turn_manager.gd:711-719 -> doom_system.add_event_doom(...), are NOT
clobbered, and re-authoring them is a BALANCE CHANGE needing a calibration
pass (the separate M ticket) -- not rapid-fire material.

crisis.json's `starting_resources.doom: 65` is a start-config value, not a
literal doom WRITE; it is out of scope for this sheet entirely (not one of
the 55 cells).

Usage:  python tools/art_review/build_doom_strip_sheet.py
Output: art_generated/doom_strip_sheet.html   (regenerable, gitignored)
"""

import os
import sys

import review_style as rs

_HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(_HERE))
OUT = os.path.join(ROOT, "art_generated", "doom_strip_sheet.html")

# ---------------------------------------------------------------- custom verdict vocabulary
# Pip's ruling: verdict chips are UPLIFT STREAM TARGETS, not a delete-by-default
# taxonomy. page() reads rs.VERDICTS / rs.VERDICT_COLORS as module globals at
# call time (no override parameter exists), so monkeypatch them here rather
# than editing review_style.py's shared 5-tag art vocabulary.
DOOM_VERDICTS = [
    "uplift-overhang",
    "uplift-alarm",
    "uplift-political",
    "uplift-panic",
    "uplift-absorption",
    "uplift-rival-delay",
    "drop",
    "keep",
    "discuss",
]
DOOM_VERDICT_COLORS = {
    "uplift-overhang": "#c98b3f",  # warm amber-brown -- capability stream
    "uplift-alarm": "#e0a34a",  # amber -- public alarm stream
    "uplift-political": "#b57fb0",  # violet -- political pressure stream
    "uplift-panic": "#e64d33",  # hot red-orange -- acute panic stream
    "uplift-absorption": "#6ba3b0",  # teal -- safety org capacity stream
    "uplift-rival-delay": "#8fae6b",  # olive-green -- rival delay stream
    "drop": "#cc5a4a",  # red -- delete
    "keep": "#6fae5a",  # green -- leave as-is
    "discuss": "#e0c34a",  # amber-yellow -- needs a design call
}
rs.VERDICTS = DOOM_VERDICTS
rs.VERDICT_COLORS = DOOM_VERDICT_COLORS

# ---------------------------------------------------------------- family order + accents

FAMILY_ORDER = [
    "morale-flavor",
    "publishing-capability",
    "regulation-transparency",
    "security",
    "rival-intel",
    "dead-schema-template",
]
FAMILY_LABEL = {
    "morale-flavor": "morale / flavor doom writes",
    "publishing-capability": "publishing / capability events",
    "regulation-transparency": "regulation / whistleblower / transparency",
    "security": "security & org-capacity",
    "rival-intel": "rival intel / sabotage",
    "dead-schema-template": "dead schema / template files",
}
FAMILY_ACCENT = {
    "morale-flavor": "#cc5a4a",
    "publishing-capability": "#c98b3f",
    "regulation-transparency": "#b57fb0",
    "security": "#6ba3b0",
    "rival-intel": "#8fae6b",
    "dead-schema-template": "#7a7268",
}
FAMILY_NOTE = {
    "morale-flavor": (
        "Precedent actions.gd:508 -- team morale is not a printed doom write. "
        "Scout default: drop. Pip's uplift ruling still applies if any of "
        "these read as disguised systemic effects on review -- flag discuss "
        "rather than silently keeping the drop."
    ),
    "publishing-capability": (
        "Pattern actions.gd:571. Capability breakthroughs / leaked or "
        "published research -> overhang stream (frontier capability outrunning "
        "safety work)."
    ),
    "regulation-transparency": (
        "Patterns actions.gd:533, :552, :840-842. Governance/regulation votes "
        "-> political_pressure; public disclosure/whistleblowing -> "
        "global_alarm; private hiring responses -> safety_absorption (mixed "
        "family, see per-cell suggestion)."
    ),
    "security": (
        "Security audits -> safety_absorption pattern. Also covers hiring/"
        "losing safety researchers, which reads as the same org-capacity "
        "stream even though the scout table filed audits and hiring under "
        "different headings."
    ),
    "rival-intel": (
        "Pattern actions.gd:587. Espionage / rival-breach response -> rival "
        "frontier delay stream, except where the option is really about the "
        "PLAYER's own security posture (flagged per-cell)."
    ),
    "dead-schema-template": (
        "Never read by any loader: overrides/example.json is loaded by "
        "NOTHING (grep-confirmed) and is the explicit copy-me ADR-0016 trap; "
        "2017.json's game_effect.doom_increase/decrease keys are a different, "
        "entirely-unread schema from the options[].effects.doom the engine "
        "does resolve. variable_mapping.json's legendary default is a "
        "fallback default_effects table. All trivial deletes."
    ),
}

# ---------------------------------------------------------------- field inventory
# One dict per literal doom field. `rel` is the export key (file:keypath).

CORE = "godot/data/events/core_events.json"
TIMELINE_2017 = "godot/data/historical_timeline/2017.json"
CRISIS = "godot/data/scenarios/crisis.json"
VARMAP = "godot/data/events/balancing/variable_mapping.json"
EXAMPLE = "godot/data/events/overrides/example.json"

FIELDS = []


def add(
    file,
    family,
    event_id,
    event_name,
    option_id,
    option_text,
    doom_value,
    other_effects,
    message,
    keypath,
    suggested,
    note="",
):
    rel = f"{file}:{keypath}"
    FIELDS.append(
        {
            "file": file,
            "family": family,
            "event_id": event_id,
            "event_name": event_name,
            "option_id": option_id,
            "option_text": option_text,
            "doom_value": doom_value,
            "other_effects": other_effects,
            "message": message,
            "keypath": keypath,
            "rel": rel,
            "suggested": suggested,
            "note": note,
        }
    )


# ---- morale-flavor (13) ---------------------------------------------------

add(
    CORE,
    "morale-flavor",
    "employee_burnout",
    "Employee Burnout Crisis",
    "emergency_intervention",
    "Emergency Intervention",
    -5,
    {"reputation": 8},
    "Personal intervention prevented resignations! (+8 reputation, -5 doom)",
    "events[employee_burnout].options[emergency_intervention].effects.doom",
    "drop",
)
add(
    CORE,
    "morale-flavor",
    "employee_burnout",
    "Employee Burnout Crisis",
    "team_retreat",
    "Organize Team Retreat",
    -2,
    {"reputation": 5},
    "Team retreat restored morale (+5 reputation, -2 doom)",
    "events[employee_burnout].options[team_retreat].effects.doom",
    "drop",
)
add(
    CORE,
    "morale-flavor",
    "employee_burnout",
    "Employee Burnout Crisis",
    "ignore_burnout",
    "Push Through (costs trust)",
    3,
    {"loyalty_hit": 15},
    "Nobody quit, but pushing through cost trust (+3 doom)",
    "events[employee_burnout].options[ignore_burnout].effects.doom",
    "drop",
)
add(
    CORE,
    "morale-flavor",
    "stray_cat",
    "A Stray Cat Appears!",
    "adopt_cat",
    "Adopt the Cat",
    -1,
    {"has_cat": 1},
    "Cat adopted! Your researchers' morale improves slightly. (-1 doom)",
    "events[stray_cat].options[adopt_cat].effects.doom",
    "drop",
)
add(
    CORE,
    "morale-flavor",
    "stray_cat",
    "A Stray Cat Appears!",
    "shoo_away",
    "Shoo It Away",
    1,
    {},
    "The cat leaves, disappointed. (+1 doom for being heartless)",
    "events[stray_cat].options[shoo_away].effects.doom",
    "drop",
)
add(
    CORE,
    "morale-flavor",
    "workplace_conflict",
    "Interpersonal Conflict",
    "mediate_personally",
    "Mediate Personally",
    -1,
    {"reputation": 3},
    "Successful mediation! Team cohesion improved (-1 doom)",
    "events[workplace_conflict].options[mediate_personally].effects.doom",
    "drop",
)
add(
    CORE,
    "morale-flavor",
    "workplace_conflict",
    "Interpersonal Conflict",
    "ignore_conflict",
    "Let Them Work It Out",
    2,
    {"reputation": -3},
    "Conflict festered and spread (+2 doom)",
    "events[workplace_conflict].options[ignore_conflict].effects.doom",
    "drop",
)
add(
    CORE,
    "morale-flavor",
    "harassment_complaint",
    "Workplace Complaint Filed",
    "minimize_issue",
    "Minimize the Issue",
    3,
    {"reputation": -10},
    "Poor handling damaged lab culture (+3 doom)",
    "events[harassment_complaint].options[minimize_issue].effects.doom",
    "drop",
)
add(
    CORE,
    "morale-flavor",
    "salary_dispute",
    "Pay Equity Concerns",
    "salary_audit",
    "Conduct Salary Audit & Adjust",
    -2,
    {"reputation": 10},
    "Salary audit complete, adjustments made (-2 doom)",
    "events[salary_dispute].options[salary_audit].effects.doom",
    "drop",
)
add(
    CORE,
    "morale-flavor",
    "salary_dispute",
    "Pay Equity Concerns",
    "ignore_concerns",
    "Dismiss Concerns",
    1,
    {"reputation": -5},
    "Ignored concerns bred resentment (+1 doom)",
    "events[salary_dispute].options[ignore_concerns].effects.doom",
    "drop",
)
add(
    CORE,
    "morale-flavor",
    "mental_health_crisis",
    "Employee Mental Health Crisis",
    "full_support",
    "Full Support + Paid Leave",
    -3,
    {"reputation": 8},
    "Provided full support. Team sees you care (-3 doom)",
    "events[mental_health_crisis].options[full_support].effects.doom",
    "drop",
)
add(
    CORE,
    "morale-flavor",
    "mental_health_crisis",
    "Employee Mental Health Crisis",
    "deny_leave",
    "Deny Request (Too Busy)",
    5,
    {"reputation": -8},
    "Denial caused serious damage to culture (+5 doom)",
    "events[mental_health_crisis].options[deny_leave].effects.doom",
    "drop",
)
add(
    CORE,
    "morale-flavor",
    "policy_violation",
    "Policy Violation Discovered",
    "sweep_under_rug",
    "Ignore It (They're Valuable)",
    2,
    {"reputation": -6},
    "Favoritism damaged morale (+2 doom)",
    "events[policy_violation].options[sweep_under_rug].effects.doom",
    "drop",
)

# ---- publishing-capability (7) --------------------------------------------

add(
    CORE,
    "publishing-capability",
    "ai_breakthrough",
    "AI Breakthrough!",
    "publish_open",
    "Publish Openly",
    5,
    {"reputation": 10, "research": 20},
    "Published breakthrough! (+5 doom, +10 reputation, +20 research)",
    "events[ai_breakthrough].options[publish_open].effects.doom",
    "uplift-overhang",
)
add(
    CORE,
    "publishing-capability",
    "ai_breakthrough",
    "AI Breakthrough!",
    "keep_proprietary",
    "Keep Proprietary",
    2,
    {"research": 30},
    "Kept research proprietary (+2 doom, +30 research)",
    "events[ai_breakthrough].options[keep_proprietary].effects.doom",
    "uplift-overhang",
)
add(
    CORE,
    "publishing-capability",
    "ai_breakthrough",
    "AI Breakthrough!",
    "safety_review",
    "Conduct Safety Review First",
    1,
    {"research": 15, "reputation": 5},
    "Safety review complete (+1 doom, +15 research, +5 reputation)",
    "events[ai_breakthrough].options[safety_review].effects.doom",
    "discuss",
    note=(
        "CONTRADICTS the systemic model: a safety review INCREASING doom is "
        "backwards. Scout flags this as likely drop -- design call needed."
    ),
)
add(
    CORE,
    "publishing-capability",
    "research_leak",
    "Research Leaked!",
    "investigate_leak",
    "Full Investigation",
    3,
    {"reputation": 5},
    "Found and addressed the leak, but damage done (+3 doom, +5 reputation)",
    "events[research_leak].options[investigate_leak].effects.doom",
    "uplift-overhang",
)
add(
    CORE,
    "publishing-capability",
    "research_leak",
    "Research Leaked!",
    "publish_immediately",
    "Publish Research Publicly",
    5,
    {"papers": 1, "reputation": 8},
    "Published to get credit, but all labs benefit (+1 paper, +8 rep, +5 doom)",
    "events[research_leak].options[publish_immediately].effects.doom",
    "uplift-overhang",
)
add(
    CORE,
    "publishing-capability",
    "research_leak",
    "Research Leaked!",
    "accept_leak",
    "Accept the Loss",
    8,
    {"reputation": -3},
    "Competitor gained significant advantage (+8 doom, -3 reputation)",
    "events[research_leak].options[accept_leak].effects.doom",
    "uplift-overhang",
)
add(
    CRISIS,
    "publishing-capability",
    "funding_pressure",
    "Investor Pressure",
    "compromise",
    "Accept Faster Timelines",
    3,
    {"money": 50000},
    "Additional funding secured, but at what cost?",
    "events[funding_pressure].options[compromise].effects.doom",
    "uplift-overhang",
    note="Race-dynamics pressure (accepting faster capability timelines).",
)

# ---- regulation-transparency (13) -----------------------------------------

add(
    CORE,
    "regulation-transparency",
    "government_regulation",
    "New AI Regulation Proposed",
    "support_regulation",
    "Publicly Support",
    -10,
    {"reputation": 15},
    "Regulation passed! Global safety improved (-10 doom, +15 reputation)",
    "events[government_regulation].options[support_regulation].effects.doom",
    "uplift-political",
)
add(
    CORE,
    "regulation-transparency",
    "government_regulation",
    "New AI Regulation Proposed",
    "oppose_regulation",
    "Oppose (Stay Competitive)",
    5,
    {"reputation": -5},
    "Regulation weakened (+5 doom, -5 reputation)",
    "events[government_regulation].options[oppose_regulation].effects.doom",
    "uplift-political",
)
add(
    CORE,
    "regulation-transparency",
    "government_regulation",
    "New AI Regulation Proposed",
    "stay_neutral",
    "Remain Neutral",
    2,
    {},
    "Stayed neutral as doom increased (+2 doom)",
    "events[government_regulation].options[stay_neutral].effects.doom",
    "uplift-political",
)
add(
    CORE,
    "regulation-transparency",
    "whistleblower_approach",
    "Whistleblower Approaches",
    "full_support",
    "Fully Support & Publicize",
    -15,
    {"reputation": 20},
    "Major expose! Industry-wide safety improvements (-15 doom, +20 reputation)",
    "events[whistleblower_approach].options[full_support].effects.doom",
    "uplift-alarm",
)
add(
    CORE,
    "regulation-transparency",
    "whistleblower_approach",
    "Whistleblower Approaches",
    "anonymous_support",
    "Anonymous Support",
    -8,
    {"reputation": 5},
    "Quietly helped expose dangers (-8 doom, +5 reputation)",
    "events[whistleblower_approach].options[anonymous_support].effects.doom",
    "uplift-alarm",
)
add(
    CORE,
    "regulation-transparency",
    "whistleblower_approach",
    "Whistleblower Approaches",
    "hire_whistleblower",
    "Hire Them Instead",
    -3,
    {"safety_researchers": 1},
    "Hired the concerned researcher (+1 safety researcher, -3 doom)",
    "events[whistleblower_approach].options[hire_whistleblower].effects.doom",
    "uplift-absorption",
    note="Private hire, not public disclosure -- reads closer to org capacity than alarm.",
)
add(
    CORE,
    "regulation-transparency",
    "employee_whistleblower",
    "Internal Concerns Raised",
    "address_concerns",
    "Open Forum Discussion",
    -2,
    {"reputation": 8},
    "Transparent discussion improved practices (-2 doom)",
    "events[employee_whistleblower].options[address_concerns].effects.doom",
    "uplift-alarm",
)
add(
    CORE,
    "regulation-transparency",
    "employee_whistleblower",
    "Internal Concerns Raised",
    "suppress_concerns",
    "Suppress the Issue",
    5,
    {"reputation": -15},
    "Suppression backfired badly (+5 doom)",
    "events[employee_whistleblower].options[suppress_concerns].effects.doom",
    "uplift-alarm",
)
add(
    TIMELINE_2017,
    "regulation-transparency",
    "concrete_problems_ai_safety_impact",
    "AI Safety Community Discusses 'Concrete Problems'",
    "study_paper",
    "Assign researchers to study concrete safety problems",
    -1.0,
    {"research": 10, "reputation": 2},
    "(inert; option effect)",
    "default_timeline_events[concrete_problems_ai_safety_impact].options[study_paper].effects.doom",
    "uplift-absorption",
)
add(
    TIMELINE_2017,
    "regulation-transparency",
    "concrete_problems_ai_safety_impact",
    "AI Safety Community Discusses 'Concrete Problems'",
    "organize_reading_group",
    "Organize safety reading group (2 AP)",
    -2.0,
    {"research": 20, "reputation": 5},
    "(inert; option effect)",
    "default_timeline_events[concrete_problems_ai_safety_impact].options[organize_reading_group].effects.doom",
    "uplift-absorption",
)
add(
    TIMELINE_2017,
    "regulation-transparency",
    "fli_asilomar_principles",
    "Asilomar AI Principles Published",
    "endorse_principles",
    "Publicly Endorse Asilomar Principles",
    -0.5,
    {"reputation": 8},
    "(inert; option effect)",
    "default_timeline_events[fli_asilomar_principles].options[endorse_principles].effects.doom",
    "uplift-political",
)
add(
    TIMELINE_2017,
    "regulation-transparency",
    "fli_asilomar_principles",
    "Asilomar AI Principles Published",
    "integrate_principles",
    "Integrate Principles Into Lab Policy (2 AP, $10k)",
    -2.0,
    {"reputation": 15},
    "(inert; option effect)",
    "default_timeline_events[fli_asilomar_principles].options[integrate_principles].effects.doom",
    "uplift-political",
)
add(
    CRISIS,
    "regulation-transparency",
    "crisis_warning",
    "Urgent Warning",
    "issue_statement",
    "Issue a Supporting Statement",
    -2,
    {"reputation": 10},
    "Your public support helps legitimize safety concerns.",
    "events[crisis_warning].options[issue_statement].effects.doom",
    "uplift-political",
)

# ---- security (6) -----------------------------------------------------

add(
    CORE,
    "security",
    "talent_recruitment",
    "Talent Opportunity",
    "hire_immediately",
    "Fast-Track Hiring",
    -3,
    {"safety_researchers": 1},
    "Fast-tracked hiring process! (+1 safety researcher, -3 doom)",
    "events[talent_recruitment].options[hire_immediately].effects.doom",
    "uplift-absorption",
)
add(
    CORE,
    "security",
    "talent_recruitment",
    "Talent Opportunity",
    "hire_discounted",
    "Standard Hiring",
    -2,
    {"safety_researchers": 1},
    "Hired talented researcher at discount! (+1 safety researcher, -2 doom)",
    "events[talent_recruitment].options[hire_discounted].effects.doom",
    "uplift-absorption",
)
add(
    CORE,
    "security",
    "your_security_audit",
    "Security Vulnerability Found",
    "full_security_overhaul",
    "Full Security Overhaul",
    -5,
    {"reputation": 8},
    "Comprehensive security upgrade complete (-5 doom)",
    "events[your_security_audit].options[full_security_overhaul].effects.doom",
    "uplift-absorption",
)
add(
    CORE,
    "security",
    "your_security_audit",
    "Security Vulnerability Found",
    "patch_critical",
    "Patch Critical Issues",
    -2,
    {"reputation": 3},
    "Critical vulnerabilities patched (-2 doom)",
    "events[your_security_audit].options[patch_critical].effects.doom",
    "uplift-absorption",
)
add(
    CORE,
    "security",
    "your_security_audit",
    "Security Vulnerability Found",
    "defer_security",
    "Defer (We're Too Busy)",
    5,
    {},
    "Security risks remain (+5 doom)",
    "events[your_security_audit].options[defer_security].effects.doom",
    "uplift-absorption",
    note="Deferring your own audit -- negative delta on the same absorption stream.",
)
add(
    CORE,
    "security",
    "researcher_poached",
    "Competitor Poaching Attempt",
    "let_them_go",
    "Let Them Leave",
    3,
    {"lose_researcher": 1},
    "Researcher departed for competitor (+3 doom, lost valuable team member)",
    "events[researcher_poached].options[let_them_go].effects.doom",
    "uplift-absorption",
    note="Losing a researcher -- absorption capacity going DOWN.",
)

# ---- rival-intel (7) -----------------------------------------------------

add(
    CORE,
    "rival-intel",
    "competitor_intel",
    "Competitor Intelligence",
    "use_intel",
    "Use the Information",
    -5,
    {"reputation": -8},
    "Used intel to counter their work (-5 doom, -8 reputation for ethics)",
    "events[competitor_intel].options[use_intel].effects.doom",
    "uplift-rival-delay",
)
add(
    CORE,
    "rival-intel",
    "competitor_intel",
    "Competitor Intelligence",
    "report_intel",
    "Report to Authorities",
    -3,
    {"reputation": 10},
    "Reported concerns, triggering investigation (+10 reputation, -3 doom)",
    "events[competitor_intel].options[report_intel].effects.doom",
    "uplift-rival-delay",
)
add(
    CORE,
    "rival-intel",
    "plant_source_opportunity",
    "Intelligence Opportunity",
    "plant_source",
    "Plant a Source",
    -10,
    {"reputation": -15},
    "Source planted, early warnings enabled (-10 doom, -15 reputation)",
    "events[plant_source_opportunity].options[plant_source].effects.doom",
    "uplift-rival-delay",
)
add(
    CORE,
    "rival-intel",
    "plant_source_opportunity",
    "Intelligence Opportunity",
    "legitimate_partnership",
    "Propose Legitimate Partnership",
    -5,
    {"reputation": 8},
    "Established safety information sharing (-5 doom, +8 reputation)",
    "events[plant_source_opportunity].options[legitimate_partnership].effects.doom",
    "uplift-rival-delay",
)
add(
    CORE,
    "rival-intel",
    "competitor_password_breach",
    "Competitor Security Breach",
    "public_security_audit",
    "Announce Public Security Audit",
    -3,
    {"reputation": 15},
    "Proactive security audit boosted confidence (+15 reputation, -3 doom)",
    "events[competitor_password_breach].options[public_security_audit].effects.doom",
    "discuss",
    note="This is the PLAYER's own audit response, not rival delay -- may belong in security instead.",
)
add(
    CORE,
    "rival-intel",
    "competitor_password_breach",
    "Competitor Security Breach",
    "stay_silent",
    "Stay Silent",
    2,
    {"reputation": -5},
    "Silence perceived as indifference (-5 reputation, +2 doom)",
    "events[competitor_password_breach].options[stay_silent].effects.doom",
    "uplift-alarm",
    note="Public non-response reads as an alarm-stream effect, not rival delay.",
)
add(
    CORE,
    "rival-intel",
    "competitor_password_breach",
    "Competitor Security Breach",
    "exploit_weakness",
    "Exploit Their Weakness (Poach Clients)",
    3,
    {"money": 50000, "reputation": -10},
    "Gained clients but damaged reputation (+$50k, -10 rep, +3 doom)",
    "events[competitor_password_breach].options[exploit_weakness].effects.doom",
    "discuss",
    note="Poaching clients doesn't clearly delay the rival's frontier -- doesn't map cleanly to any stream.",
)

# ---- dead-schema-template (9) ---------------------------------------------

add(
    VARMAP,
    "dead-schema-template",
    "-",
    "variable_mapping.json",
    "-",
    "default_effects.legendary fallback (no impacts[] array provided)",
    5,
    {"research": 20, "reputation": 10},
    "Default effect bundle applied when a pdoom-data event has no impacts[].",
    "default_effects.legendary.doom",
    "drop",
)
add(
    EXAMPLE,
    "dead-schema-template",
    "ftx_future_fund_collapse_2022",
    "FTX Future Fund Collapse (example override)",
    "-",
    "impacts[].variable=doom change + top-level pdoom_impact (2 fields, same event)",
    15,
    {"money": -80, "pdoom_impact": 15},
    "Example override showing the impacts[]/pdoom_impact override schema.",
    "ftx_future_fund_collapse_2022.impacts[variable=doom].change (+pdoom_impact)",
    "drop",
    note="File loaded by NOTHING (grep-confirmed) -- explicit copy-me template, worst ADR-0016 copy-paste trap.",
)
add(
    EXAMPLE,
    "dead-schema-template",
    "openai_founded",
    "Founding of OpenAI (example override)",
    "-",
    "impacts[].variable=doom change",
    5,
    {"reputation": 10},
    "Example override showing the impacts[] schema.",
    "openai_founded.impacts[variable=doom].change",
    "drop",
    note="File loaded by NOTHING -- same copy-me trap.",
)
add(
    EXAMPLE,
    "dead-schema-template",
    "chatgpt_released",
    "ChatGPT Released (example override)",
    "-",
    "impacts[].variable=doom change",
    10,
    {"reputation": 5},
    "Example override showing the impacts[] schema.",
    "chatgpt_released.impacts[variable=doom].change",
    "drop",
    note="File loaded by NOTHING -- same copy-me trap.",
)
add(
    TIMELINE_2017,
    "dead-schema-template",
    "openai_dota2_announcement",
    "OpenAI Dota 2 Bot Announced",
    "-",
    "game_effect.doom_increase (dead key, never read)",
    2.0,
    {"capability_research_boost": 5, "reputation_change": -1},
    "game_effect is a DIFFERENT schema from options[].effects -- read nowhere.",
    "default_timeline_events[openai_dota2_announcement].game_effect.doom_increase",
    "drop",
)
add(
    TIMELINE_2017,
    "dead-schema-template",
    "deepmind_alphago_zero",
    "AlphaGo Zero Announced",
    "-",
    "game_effect.doom_increase (dead key, never read)",
    3.0,
    {"capability_research_boost": 10},
    "game_effect is a DIFFERENT schema from options[].effects -- read nowhere.",
    "default_timeline_events[deepmind_alphago_zero].game_effect.doom_increase",
    "drop",
)
add(
    TIMELINE_2017,
    "dead-schema-template",
    "attention_is_all_you_need",
    "'Attention Is All You Need' Published",
    "-",
    "game_effect.doom_increase (dead key, never read)",
    1.0,
    {"capability_research_boost": 15},
    "game_effect is a DIFFERENT schema from options[].effects -- read nowhere.",
    "default_timeline_events[attention_is_all_you_need].game_effect.doom_increase",
    "drop",
)
add(
    TIMELINE_2017,
    "dead-schema-template",
    "concrete_problems_ai_safety_impact",
    "AI Safety Community Discusses 'Concrete Problems'",
    "-",
    "game_effect.doom_decrease (dead key, never read)",
    -0.5,
    {"reputation_boost": 3},
    "game_effect is a DIFFERENT schema from options[].effects -- read nowhere.",
    "default_timeline_events[concrete_problems_ai_safety_impact].game_effect.doom_decrease",
    "drop",
)
add(
    TIMELINE_2017,
    "dead-schema-template",
    "fli_asilomar_principles",
    "Asilomar AI Principles Published",
    "-",
    "game_effect.doom_decrease (dead key, never read)",
    -1.0,
    {"reputation_boost": 5, "governance_boost": 10},
    "game_effect is a DIFFERENT schema from options[].effects -- read nowhere.",
    "default_timeline_events[fli_asilomar_principles].game_effect.doom_decrease",
    "drop",
)


# ---------------------------------------------------------------- rendering


def fmt_effects(d):
    if not d:
        return "(no other effects)"
    return ", ".join(f"{k}: {v}" for k, v in d.items())


def field_cell(f):
    """Text-only cell in the review_style vocabulary (no image, no rs.image_cell
    since that's image-specific): rs-cell chrome, label/sub/blurb, a suggested-
    disposition badge, and the verdict-chip slot review_style's VERDICT_JS
    populates automatically for any [data-rel] cell."""
    label = f"{f['event_id']} :: {f['option_id']}" if f["option_id"] != "-" else f["event_id"]
    sub = f["rel"]
    blurb_lines = [
        (
            f"doom {f['doom_value']:+g}"
            if isinstance(f["doom_value"], (int, float))
            else f"doom {f['doom_value']}"
        ),
        f"text: {f['option_text']}",
        f"other effects: {fmt_effects(f['other_effects'])}",
        f"message: {f['message']}",
    ]
    if f["note"]:
        blurb_lines.append(f"note: {f['note']}")
    blurb = "\n".join(blurb_lines)
    accent = FAMILY_ACCENT[f["family"]]
    sugg_color = DOOM_VERDICT_COLORS.get(f["suggested"], rs.PALETTE["dim"])
    parts = [
        f'<div class="rs-cell" style="--accent:{accent};width:260px" data-rel="{rs.esc(f["rel"])}">',
        f'<div class="rs-label">{rs.esc(label)}</div>',
        f'<code class="rs-sub">{rs.esc(sub)}</code>',
        (
            '<div class="rs-blurb" style="white-space:pre-line;text-align:left">'
            f"{rs.esc(blurb)}</div>"
        ),
        (
            '<div style="margin-top:6px;font-family:monospace;font-size:9px;'
            f"color:{sugg_color};border:1px solid {sugg_color};border-radius:5px;"
            'padding:2px 6px;display:inline-block">'
            f"scout suggests: {rs.esc(f['suggested'])}</div>"
        ),
        '<div class="rs-vtags"></div>',
        rs.NOTE_HTML,
        "</div>",
    ]
    return "".join(parts)


def main():
    sections = []
    total = 0
    by_family = {fam: [] for fam in FAMILY_ORDER}
    for f in FIELDS:
        by_family[f["family"]].append(f)

    for fam in FAMILY_ORDER:
        items = by_family[fam]
        if not items:
            continue
        total += len(items)
        cells = "".join(field_cell(f) for f in items)
        head_extra = f' <span class="count-tag">{rs.esc(FAMILY_NOTE[fam])}</span>'
        sections.append(
            rs.section(
                FAMILY_LABEL[fam],
                f'<div class="rs-grid">{cells}</div>',
                count=len(items),
                accent=FAMILY_ACCENT[fam],
                head_extra=head_extra,
            )
        )

    intro = (
        "ADR-0015 doom-strip triage (S ticket, precedes the 0016 pack schema). "
        "55 cells: 46 INERT fields (core_events.json 40 + 2017.json option "
        "effects 4 + crisis.json option effects 2 -- all clobbered every "
        "resolve by turn_manager.gd:657, so re-authoring is a pure no-op on "
        "balance) + 1 variable_mapping.json legendary default + 3 "
        "overrides/example.json template entries + 5 2017.json dead "
        "game_effect keys. EXCLUDED ON PURPOSE: the 20 LIVE risk_events.json "
        "pool fields (turn_manager.gd:711-719 -> doom_system.add_event_doom, "
        "NOT clobbered) -- re-authoring those is a balance change needing a "
        "calibration pass and ships as a separate M ticket. Also excluded: "
        "crisis.json starting_resources.doom (start-config, not a doom WRITE). "
        "<br><br>Pip's ruling: fields get UPLIFTED to systemic streams, not "
        "deleted by default -- the verdict chips below are stream targets "
        "(uplift-overhang / uplift-alarm / uplift-political / uplift-panic / "
        "uplift-absorption / uplift-rival-delay), plus drop / keep / discuss "
        "for the genuine no-systemic-replacement cases. Every cell's \"scout "
        'suggests" label is a suggestion to confirm or override with a chip '
        "-- nothing is pre-applied."
    )

    html_text = rs.page(
        tool_name="doom strip triage sheet",
        subtitle="ADR-0015 uplift dispositions -- issue #949",
        body_html="".join(sections),
        badges=[("fields", str(total)), ("families", str(len(FAMILY_ORDER)))],
        intro_html=intro,
        verdict_key="doomstrip:verdicts",
        export_name="doom_strip_verdicts.json",
        footer_note=(
            "Export JSON and save the download over "
            "docs/game-design/doom_strip_verdicts.json (a design-decision "
            "artifact -- tracked once the lane that acts on it commits it; "
            "this sheet itself stays local/regenerable, NOT art_source)."
        ),
    )

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    rs.write_ascii(OUT, html_text)
    print(
        f"wrote {OUT} ({os.path.getsize(OUT) // 1024} KB, {total} fields, {len(FAMILY_ORDER)} families)"
    )
    assert total == 55, f"expected 55 fields, got {total}"
    return 0


if __name__ == "__main__":
    sys.exit(main())
