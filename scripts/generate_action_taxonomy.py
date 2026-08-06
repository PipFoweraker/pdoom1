#!/usr/bin/env python3
"""Generate docs/ACTION_TAXONOMY.md and check the action taxonomy for rot.

Layer: GENERATE

WHY THIS EXISTS. `category` on an action definition is a SORT KEY with no checker,
and an unchecked data field rots. Two measured consequences, not hypotheticals:

  * The `fundraise` door was tagged `category: management` while every item in its
    own submenu was `funding`. Nothing failed. The tile just rendered tenth and fell
    below the fold, and two external playtesters (2026-08-05) could not find
    fundraising at all. Fixed in #1130 by hand -- the DEFECT was invisible because
    the only symptom was a rendering position.
  * `take_loan` is defined TWICE, in `fundraising.json` (category `funding`,
    advertising +$75k / $90k debt) and in `financing.json` (category `financing`,
    advertising +$50k / ~$60k balloon). They live in different domain caches, so
    both are live at once and neither shadows the other loudly.

Same anti-rot pattern as generate_dq_index.py / generate_adr_index.py /
generate_tools_index.py: the index is DERIVED from the JSON, `--check` reports
staleness AND violations, and hand edits are therefore impossible to sustain.

WHAT IT IS NOT. This implements Part D of docs/design/UI_ARCHITECTURE_2026-08-06.md
(keeping the taxonomy honest) and nothing else. Part B (the nine-door sort) and
Part C (the digit grammar) are NOT enforced here -- Part B's Research door is
explicitly gated on a workshop with Pip. The proposed door column in the emitted
table is transcribed from that document and clearly marked PROPOSED; it is
reference material for the phase 1/2 lanes, never a gate.

SEVERITY IS TWO-TIERED, deliberately:
  ERROR   -- a defect: duplicate id, unknown/missing category, a door disagreeing
             with its members over a category that the action bar actually renders,
             an unbuildable submenu, a door nested inside a door.
  WARNING -- a structural observation that is true of the tree TODAY and is a
             phase-1/2 workitem, not a bug: loose top-level actions, and doors whose
             members carry a NAMESPACE category (`travel`, `office`, `scouting`,
             `operations`, `financing`) that the action bar has no group for.
Reporting those as errors would make the check red on arrival, and a check that is
red on arrival gets disabled inside a week (#1117: this repo already ran a Python
lane as `|| echo` and reported green over zero assertions).

WHAT IS AND IS NOT WIRED INTO PRE-COMMIT. `--check-stale` IS (a stale index is a
condition anyone can fix in one command, so gating it costs nothing and is the only
thing keeping the index from rotting the way decisions/README.md did). `--check`,
which additionally fails on the violations, is NOT -- it is red on arrival while
take_loan is duplicated. Flip the hook to `--check` the moment the error list is
empty; that is the phase-2 ratchet in Part E, and there is a test in
tests/test_generate_action_taxonomy.py that fails when the moment arrives.

Usage:
    python scripts/generate_action_taxonomy.py                # (re)write the index
    python scripts/generate_action_taxonomy.py --check        # exit 1 if stale OR violated
    python scripts/generate_action_taxonomy.py --check-stale  # exit 1 only if stale
    python scripts/generate_action_taxonomy.py --report       # print findings, exit 0
"""

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ACTIONS_DIR = ROOT / "godot" / "data" / "actions"
OUT = ROOT / "docs" / "ACTION_TAXONOMY.md"
RENDERER = ROOT / "godot" / "scripts" / "ui" / "action_bar_renderer.gd"
SUBMENU_CONTROLLER = ROOT / "godot" / "scripts" / "ui" / "submenu_controller.gd"
DESIGN_DOC_REL = "docs/design/UI_ARCHITECTURE_2026-08-06.md"

# The emitted file must be ASCII (enforce-standards + no-emoji hooks). Keys are
# built with chr() DELIBERATELY -- literal characters would make this file
# non-ASCII, and backslash-u escapes get un-escaped back to literals by black on
# the next commit (observed 2026-08-03 on generate_adr_index.py).
ASCII_MAP = {
    chr(0x00B7): "-",  # middle dot
    chr(0x2013): "--",  # en dash
    chr(0x2014): "--",  # em dash
    chr(0x2018): "'",  # left single quote
    chr(0x2019): "'",  # right single quote
    chr(0x201C): '"',  # left double quote
    chr(0x201D): '"',  # right double quote
    chr(0x2026): "...",  # ellipsis
    chr(0x2192): "->",  # right arrow
    chr(0x00A0): " ",  # nbsp
}

# Files under godot/data/actions/ that hold no actions. risk_contributions.json is
# a per-action risk-pool table (top-level keys `_description` + `contributions`).
# Verified by measurement: the commission's "64 actions" count wrongly credited it
# with 2. Listed explicitly so a NEW non-action file has to be declared here rather
# than silently dropping out of the count.
NON_ACTION_FILES = {"risk_contributions.json"}

# door action id -> the domain file holding its members. Mirrors the dispatch in
# GameActions.get_action_by_id / the get_*_options accessors (scripts/core/actions.gd).
DOOR_DOMAIN = {
    "hire_staff": "hiring",
    "fundraise": "fundraising",
    "publicity": "publicity",
    "strategic": "strategic",
    "travel": "travel",
    "operations": "operations",
    "financing": "financing",
    "office": "office",
    "scouting": "scouting",
}

# Domains that are not reached through a door tile. `command` holds `pass`, a
# Plan-screen control rather than a bar tile; `core` is the top level itself.
NON_DOOR_DOMAINS = {"core", "command"}

# Categories the ACTION BAR actually groups by. Read from action_bar_renderer.gd
# at runtime; this is the fallback if the parse fails, kept so a renderer refactor
# degrades to a stale-but-loud check rather than a silent no-op.
FALLBACK_RENDER_CATEGORIES = [
    "funding",
    "hiring",
    "resources",
    "research",
    "management",
    "influence",
    "strategic",
    "other",
]

# Categories that exist ONLY as a submenu namespace: no group in the action bar's
# category_order, so a top-level tile carrying one would fall into "other".
NAMESPACE_CATEGORIES = {
    "travel",
    "office",
    "scouting",
    "operations",
    "financing",
    "command",
}

# Submenu ids SubmenuController.open() handles outside GRID_CONFIG. Documented
# bespoke builders, not a hole -- the hole this pins shut is the `else` branch's
# push_warning("unknown submenu id"), which is a runtime warning nobody sees.
BESPOKE_SUBMENU_IDS = {"financing", "hire_staff", "travel"}

# PROPOSED placement, transcribed from Part B of the architecture doc. REFERENCE
# ONLY -- never checked, never enforced. Part B's Research door is gated on a
# workshop with Pip (Part E phase 3), so encoding it as truth would be a lie.
PROPOSED_DOOR = {
    "Funding": [
        "fundraise_small",
        "fundraise_big",
        "apply_grant",
        "take_loan",
        "funding_strings",
        "desperation_lever",
        "staff_rider",
        "seek_financing",
        "accept_financing_offer",
        "pay_bills",
    ],
    "People": [
        "hire_safety_researcher",
        "hire_capability_researcher",
        "hire_compute_engineer",
        "hire_manager",
        "hire_ethicist",
        "hire_interpretability_researcher",
        "hire_alignment_researcher",
        "advertise",
        "use_connections",
        "interview_next",
        "hire_best",
        "onboard_next",
        "team_building",
    ],
    "Research": [
        "safety_research",
        "capability_research",
        "publish_paper",
        "audit_safety",
    ],
    "Compute": ["buy_compute"],
    "Publicity": [
        "network",
        "media_campaign",
        "lobby_government",
        "release_warning",
        "open_source_release",
    ],
    "Scouting": ["scout_read", "scout_meetups", "scout_shitpost"],
    "Travel": [
        "submit_paper",
        "attend_conference",
        "attend_conference_trip",
        "send_delegation",
    ],
    "Operations": [
        "order_supplies",
        "audit_self_directed",
        "tour_offices",
        "sign_lease_coworking_corner",
        "sign_lease_walkup_office",
        "sign_lease_university_annex",
        "office_maintenance",
    ],
    "Strategic": [
        "acquire_startup",
        "sabotage_competitor",
        "emergency_pivot",
        "grant_proposal",
    ],
    "(command)": ["pass"],
}

# Where each of today's DOORS lands under the same proposed sort. `financing` folds
# into Funding and `office` into Operations (Part E phase 2), which is why two of
# today's nine doors map onto a door that is not their own name.
PROPOSED_DOOR_FOR_DOOR = {
    "hire_staff": "People",
    "fundraise": "Funding",
    "financing": "Funding (merged)",
    "publicity": "Publicity",
    "strategic": "Strategic",
    "travel": "Travel",
    "operations": "Operations",
    "office": "Operations (merged)",
    "scouting": "Scouting",
}

# Pip's cap (#1132): "no more than 10 buttons along the top ... including how many
# buttons we want to have unlocked in total". Enforced against DOORS, which is the
# quantity the architecture rule produces. Ratchets down per Part E; asserted at the
# value the tree actually meets, never at an aspiration.
MAX_DOORS = 10


def to_ascii(text: str) -> str:
    for src, dst in ASCII_MAP.items():
        text = text.replace(src, dst)
    return "".join(c if ord(c) < 128 else "?" for c in text)


# --- source-of-truth readers --------------------------------------------------


def read_render_categories(text: str) -> list:
    """Pull category_order out of action_bar_renderer.gd.

    A DERIVED read, not a copy: the whole point of this checker is that placement
    currently lives in four places that can drift (the category field, this
    category_order, GRID_CONFIG's keys, and which file an action sits in). Copying
    one of them into this script would add a fifth.
    """
    m = re.search(r"var\s+category_order\s*=\s*\[(.*?)\]", text, re.S)
    if not m:
        return list(FALLBACK_RENDER_CATEGORIES)
    return re.findall(r'"([^"]+)"', m.group(1))


def read_hidden_ids(text: str) -> list:
    m = re.search(r"HIDDEN_FROM_ACTION_BAR_IDS\s*:?=\s*\[(.*?)\]", text, re.S)
    if not m:
        return []
    return re.findall(r'"([^"]+)"', m.group(1))


def read_grid_config_ids(text: str) -> list:
    """Top-level keys of SubmenuController.GRID_CONFIG.

    Matched at exactly one level of indentation (one tab) so nested dict keys
    inside an entry ("panel_size", "summary", ...) cannot be mistaken for panels.
    """
    m = re.search(r"const\s+GRID_CONFIG\s*:?=\s*\{(.*?)\n\}", text, re.S)
    if not m:
        return []
    return re.findall(r'^\t"([^"]+)"\s*:\s*\{', m.group(1), re.M)


def load_actions() -> tuple:
    """Return (records, notes). One record per action ENTRY, duplicates included.

    Duplicates are deliberately NOT collapsed here: the whole take_loan finding is
    that two entries share an id, and a dict keyed by id would eat the evidence --
    which is precisely how the defect survived this long.
    """
    if not ACTIONS_DIR.is_dir():
        raise SystemExit("ERROR: %s does not exist" % ACTIONS_DIR)

    records = []
    notes = []
    for path in sorted(ACTIONS_DIR.glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        if path.name in NON_ACTION_FILES:
            if data.get("actions"):
                raise SystemExit(
                    "ERROR: %s is declared a non-action file (NON_ACTION_FILES) but "
                    "now carries an 'actions' array. Remove it from that set." % path.name
                )
            notes.append(
                "`%s` carries ZERO actions and is excluded from the count "
                "(it is a lookup table, not an action list). The commission's "
                "earlier inventory credited it with 2." % path.name
            )
            continue
        actions = data.get("actions")
        if not isinstance(actions, list):
            raise SystemExit(
                "ERROR: %s has no 'actions' array. Every file in godot/data/actions/ "
                "is either an action list or declared in NON_ACTION_FILES." % path.name
            )
        for index, action in enumerate(actions):
            if not isinstance(action, dict):
                raise SystemExit("ERROR: %s entry %d is not an object" % (path.name, index))
            action_id = action.get("id")
            if not action_id:
                raise SystemExit(
                    "ERROR: %s entry %d has no 'id'. A blank id is worse than a wrong "
                    "one -- it cannot be queued, iconed, or replayed." % (path.name, index)
                )
            records.append(
                {
                    "id": action_id,
                    "name": to_ascii(action.get("name", "")),
                    "domain": path.stem,
                    "file": path.name,
                    "category": action.get("category"),
                    "is_submenu": bool(action.get("is_submenu", False)),
                    "index": index,
                    "raw": action,
                }
            )
    if not records:
        raise SystemExit("ERROR: no actions found in %s" % ACTIONS_DIR)
    return records, notes


# --- the checks ---------------------------------------------------------------


def describe_divergence(group) -> str:
    """Name the fields on which duplicate definitions of one id disagree.

    Reported because "duplicate" understates it. The two `take_loan` records do not
    merely coexist -- they promise the player different money. Whoever dedups needs
    to see that before choosing, or the dedup silently ships one of two prices.
    """
    keys = sorted({k for g in group for k in g["raw"] if not k.startswith("_")})
    parts = []
    for key in keys:
        values = [json.dumps(g["raw"].get(key), sort_keys=True) for g in group]
        if len(set(values)) == 1:
            continue
        rendered = " vs ".join(
            "%s=%s" % (g["file"], (v if len(v) <= 90 else v[:87] + "..."))
            for g, v in zip(group, values)
        )
        parts.append("%s (%s)" % (key, rendered))
    return "; ".join(parts) if parts else "nothing (the records are identical)"


def analyse(records, render_categories, hidden_ids, grid_ids) -> dict:
    errors = []
    warnings = []

    known_categories = set(render_categories) | NAMESPACE_CATEGORIES
    doors = [r for r in records if r["is_submenu"]]
    by_domain = {}
    for r in records:
        by_domain.setdefault(r["domain"], []).append(r)

    # 1. duplicate ids across files -- the take_loan case.
    seen = {}
    for r in records:
        seen.setdefault(r["id"], []).append(r)
    for action_id, group in sorted(seen.items()):
        if len(group) > 1:
            where = ", ".join("%s (category %s)" % (g["file"], g["category"]) for g in group)
            errors.append(
                "DUPLICATE ID '%s' defined in %d files: %s. The domain caches are "
                "separate, so BOTH are live at once and neither shadows the other "
                "loudly; which one a lookup returns depends on accessor order in "
                "GameActions.get_action_by_id. They DISAGREE on: %s. Deduping is "
                "therefore not a merge -- pick the record that matches what "
                "execute_action actually does, and say so."
                % (action_id, len(group), where, describe_divergence(group))
            )

    # 2. missing or unknown category.
    for r in records:
        if not r["category"]:
            errors.append("MISSING CATEGORY on '%s' (%s)" % (r["id"], r["file"]))
        elif r["category"] not in known_categories:
            errors.append(
                "UNKNOWN CATEGORY '%s' on '%s' (%s). Known: %s."
                % (
                    r["category"],
                    r["id"],
                    r["file"],
                    ", ".join(sorted(known_categories)),
                )
            )

    # 3. category disagreement between a door and its own members.
    #    ERROR when the members' category is one the action bar RENDERS -- that is
    #    exactly the fundraise defect (door said `management`, members said
    #    `funding`, tile sorted tenth and fell below the fold).
    #    WARNING when the members' category is a namespace with no render group:
    #    the door CANNOT carry it without falling into "other". That is the
    #    two-meanings-of-`category` rot, a phase-2 workitem, not a live defect.
    for door in doors:
        domain = DOOR_DOMAIN.get(door["id"])
        if domain is None:
            errors.append(
                "UNMAPPED DOOR '%s' (%s) is is_submenu but no domain file is mapped "
                "to it in DOOR_DOMAIN." % (door["id"], door["file"])
            )
            continue
        member_cats = sorted({m["category"] for m in by_domain.get(domain, []) if m["category"]})
        if not member_cats:
            errors.append("EMPTY DOOR '%s' -> %s.json has no members" % (door["id"], domain))
            continue
        if door["category"] in member_cats:
            continue
        detail = "door '%s' is category '%s'; its %s.json members are %s" % (
            door["id"],
            door["category"],
            domain,
            "/".join(member_cats),
        )
        if any(c in render_categories for c in member_cats):
            errors.append(
                "CATEGORY DISAGREEMENT -- %s. The members' category is one the action "
                "bar groups by, so the door sorts into a group unrelated to what it "
                "opens (the #1130 fundraise defect)." % detail
            )
        else:
            warnings.append(
                "NAMESPACE CATEGORY -- %s, which the action bar has no group for. The "
                "door has to borrow a render category, so `category` means two "
                "different things at the two levels. Phase 2 workitem." % detail
            )

    # 4. placement: door, member of exactly one door, hidden, command, or loose.
    placement = {}
    for r in records:
        if r["is_submenu"]:
            placement[r["id"]] = "door"
        elif r["domain"] in NON_DOOR_DOMAINS:
            placement.setdefault(r["id"], "top-level")
        else:
            placement[r["id"]] = "member"
    door_domains = set(DOOR_DOMAIN.values())
    for domain in sorted(by_domain):
        if domain in NON_DOOR_DOMAINS or domain in door_domains:
            continue
        errors.append(
            "ORPHAN DOMAIN '%s.json' -- %d actions with no door mapped to it; nothing "
            "in the UI can reach them." % (domain, len(by_domain[domain]))
        )
    for door_id, domain in sorted(DOOR_DOMAIN.items()):
        if domain not in by_domain:
            errors.append("DOOR '%s' maps to missing domain file %s.json" % (door_id, domain))

    # 5. depth invariant: no door inside a door.
    for door in doors:
        domain = DOOR_DOMAIN.get(door["id"])
        for member in by_domain.get(domain, []):
            if member["is_submenu"]:
                errors.append(
                    "DEPTH VIOLATION -- '%s' is a door nested inside door '%s'. Two "
                    "menus then at most one picker; a third menu of verbs is out."
                    % (member["id"], door["id"])
                )

    # 6. every door has a builder (GRID_CONFIG entry or documented bespoke). This
    #    pins shut SubmenuController.open()'s push_warning("unknown submenu id"),
    #    which is a runtime warning in a headless-quiet log -- i.e. invisible.
    buildable = set(grid_ids) | BESPOKE_SUBMENU_IDS
    for door in doors:
        if door["id"] not in buildable:
            errors.append(
                "NO BUILDER for door '%s' -- not in SubmenuController.GRID_CONFIG %s "
                "and not a documented bespoke builder %s. Opening it would only "
                "push_warning." % (door["id"], sorted(grid_ids), sorted(BESPOKE_SUBMENU_IDS))
            )
    for grid_id in sorted(grid_ids):
        if grid_id not in {d["id"] for d in doors}:
            warnings.append(
                "ORPHAN BUILDER -- GRID_CONFIG has a panel '%s' with no is_submenu "
                "action of that id." % grid_id
            )

    # 7. the cap, executable (#1132).
    if len(doors) > MAX_DOORS:
        errors.append(
            "DOOR CAP -- %d doors exceeds the cap of %d. An 11th door means the game "
            "grew an 11th steerable system; interrogate that, not the pixel width."
            % (len(doors), MAX_DOORS)
        )

    # 8. loose top-level actions -- true today, folded by phase 1/2. WARNING.
    loose = [
        r
        for r in records
        if r["domain"] == "core" and not r["is_submenu"] and r["id"] not in hidden_ids
    ]
    if loose:
        warnings.append(
            "LOOSE TOP-LEVEL ACTIONS -- %d actions render as bare tiles alongside the "
            "%d doors (%s). Under the Part A rule each competes only with its door's "
            "siblings; phase 1/2 of %s folds them."
            % (
                len(loose),
                len(doors),
                ", ".join(sorted(r["id"] for r in loose)),
                DESIGN_DOC_REL,
            )
        )

    # 9. hidden ids must actually exist.
    all_ids = {r["id"] for r in records}
    for hidden in hidden_ids:
        if hidden not in all_ids:
            errors.append(
                "STALE HIDE -- HIDDEN_FROM_ACTION_BAR_IDS names '%s', which no action "
                "defines." % hidden
            )

    return {
        "errors": errors,
        "warnings": warnings,
        "doors": doors,
        "placement": placement,
        "loose": loose,
        "unique_ids": len(all_ids),
    }


def proposed_door_for(action_id: str) -> str:
    if action_id in PROPOSED_DOOR_FOR_DOOR:
        return PROPOSED_DOOR_FOR_DOOR[action_id]
    for door, members in PROPOSED_DOOR.items():
        if action_id in members:
            return door
    return "--"


def today_door_for(record: dict, doors) -> str:
    if record["is_submenu"]:
        return "(is a door)"
    if record["domain"] in NON_DOOR_DOMAINS:
        return "(top level)"
    for door in doors:
        if DOOR_DOMAIN.get(door["id"]) == record["domain"]:
            return door["id"]
    return "(unreachable)"


# --- rendering ----------------------------------------------------------------


def render() -> str:
    records, notes = load_actions()
    renderer_text = RENDERER.read_text(encoding="utf-8")
    render_categories = read_render_categories(renderer_text)
    hidden_ids = read_hidden_ids(renderer_text)
    grid_ids = read_grid_config_ids(SUBMENU_CONTROLLER.read_text(encoding="utf-8"))
    result = analyse(records, render_categories, hidden_ids, grid_ids)
    doors = result["doors"]

    lines = [
        "# Action taxonomy (GENERATED -- do not hand-edit)",
        "",
        "> Derived from `godot/data/actions/*.json`, `action_bar_renderer.gd`",
        "> (`category_order`, `HIDDEN_FROM_ACTION_BAR_IDS`) and",
        "> `submenu_controller.gd` (`GRID_CONFIG`) by",
        "> `scripts/generate_action_taxonomy.py`. Regenerate with:",
        "> `python scripts/generate_action_taxonomy.py`.",
        ">",
        "> Implements Part D of `%s`." % DESIGN_DOC_REL,
        "> The rule it serves: **an action is top-level iff it is the single door to a",
        "> system the player steers when composing an ordinary month's plan.**",
        ">",
        "> **The violation gate is REPORT-ONLY.** Pre-commit runs `--check-stale`, which",
        "> fails only if THIS FILE is out of date. `--check` additionally exits nonzero on",
        "> the errors below and is deliberately NOT wired while a known violation is live:",
        "> a gate that is red on arrival gets disabled within a week (#1117). Flip the hook",
        "> to `--check` when the error list is empty.",
        "",
        "## Counts",
        "",
        "| Measure | Value |",
        "|---|---|",
        "| Action entries | %d |" % len(records),
        "| Distinct action ids | %d |" % result["unique_ids"],
        "| Files scanned | %d |" % len(list(ACTIONS_DIR.glob("*.json"))),
        "| Files carrying actions | %d |"
        % len([p for p in ACTIONS_DIR.glob("*.json") if p.name not in NON_ACTION_FILES]),
        "| Doors (`is_submenu`) | %d (cap %d) |" % (len(doors), MAX_DOORS),
        "| Loose top-level tiles | %d |" % len(result["loose"]),
        "| Hidden from the bar | %d |" % len(hidden_ids),
        "| Errors | %d |" % len(result["errors"]),
        "| Warnings | %d |" % len(result["warnings"]),
        "",
    ]
    for note in notes:
        lines.append("- %s" % note)
    if notes:
        lines.append("")

    lines += [
        "## Findings",
        "",
    ]
    if result["errors"]:
        lines.append("### Errors (`--check` exits 1)")
        lines.append("")
        for e in result["errors"]:
            lines.append("- %s" % to_ascii(e))
        lines.append("")
    else:
        lines += ["### Errors (`--check` exits 1)", "", "None.", ""]
    if result["warnings"]:
        lines.append("### Warnings (reported, never fatal)")
        lines.append("")
        for w in result["warnings"]:
            lines.append("- %s" % to_ascii(w))
        lines.append("")

    lines += [
        "## Every action",
        "",
        "`Door (today)` is measured from the data: which submenu file the action lives",
        "in, and which `is_submenu` action opens that file. `Door (proposed)` is",
        "transcribed from Part B of the architecture doc and is **reference only** --",
        "nothing here checks it, and the Research door is gated on a workshop.",
        "",
        "| # | id | Name | File | Category | Placement | Door (today) | Door (proposed) |",
        "|---|---|---|---|---|---|---|---|",
    ]
    ordered = sorted(records, key=lambda r: (r["file"], r["index"]))
    for n, r in enumerate(ordered, 1):
        placement = "door" if r["is_submenu"] else result["placement"].get(r["id"], "member")
        if r["id"] in hidden_ids:
            placement += " (hidden)"
        lines.append(
            "| %d | `%s` | %s | `%s` | `%s` | %s | %s | %s |"
            % (
                n,
                r["id"],
                r["name"],
                r["file"],
                r["category"],
                placement,
                today_door_for(r, doors),
                proposed_door_for(r["id"]),
            )
        )
    lines.append("")

    lines += [
        "## Doors today",
        "",
        "| Door id | Door category | Members file | Members | Member categories | Builder |",
        "|---|---|---|---|---|---|",
    ]
    by_domain = {}
    for r in records:
        by_domain.setdefault(r["domain"], []).append(r)
    for door in sorted(doors, key=lambda d: d["index"]):
        domain = DOOR_DOMAIN.get(door["id"], "")
        members = by_domain.get(domain, [])
        member_cats = sorted({m["category"] for m in members if m["category"]})
        builder = "GRID_CONFIG" if door["id"] in grid_ids else "bespoke"
        lines.append(
            "| `%s` | `%s` | `%s.json` | %d | %s | %s |"
            % (
                door["id"],
                door["category"],
                domain,
                len(members),
                ", ".join("`%s`" % c for c in member_cats),
                builder,
            )
        )
    lines.append("")
    lines.append(
        "Action bar `category_order` (the render groups): %s."
        % ", ".join("`%s`" % c for c in render_categories)
    )
    lines.append("")
    return "\n".join(lines)


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    content = render()

    records, _ = load_actions()
    renderer_text = RENDERER.read_text(encoding="utf-8")
    result = analyse(
        records,
        read_render_categories(renderer_text),
        read_hidden_ids(renderer_text),
        read_grid_config_ids(SUBMENU_CONTROLLER.read_text(encoding="utf-8")),
    )

    check = "--check" in argv
    check_stale = "--check-stale" in argv
    stale = not OUT.exists() or OUT.read_text(encoding="utf-8") != content

    if "--report" in argv or check:
        for e in result["errors"]:
            print("ERROR: %s" % e)
        for w in result["warnings"]:
            print("WARN:  %s" % w)
        print(
            "%d entries, %d distinct ids, %d errors, %d warnings."
            % (len(records), result["unique_ids"], len(result["errors"]), len(result["warnings"]))
        )

    if check or check_stale:
        if stale:
            print("ACTION_TAXONOMY.md is stale. Run: python scripts/generate_action_taxonomy.py")
        if check_stale and result["errors"]:
            # Deliberately not fatal here: this mode gates the INDEX, not the tree.
            print(
                "(%d taxonomy error(s) reported in %s -- not gated. See the script "
                "docstring for why.)" % (len(result["errors"]), OUT.relative_to(ROOT))
            )
        return 1 if (stale or (check and result["errors"])) else 0

    if "--report" in argv:
        return 0

    OUT.write_text(content, encoding="utf-8", newline="\n")
    print("Wrote %s" % OUT.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
