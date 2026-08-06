#!/usr/bin/env python3
"""run_art_night.py -- level-structured, budget-capped, resumable art run.

Layer: GENERATE
Invoked by: human (Pip), once per wave
Spec: tools/assets/manifests/art_night_2026-08-07.json
Plan: docs/design/ART_RUN_2026-08-07.md

Why this exists next to generate_images.py rather than inside it:
generate_images.py expands a FLAT list of assets and has no budget ceiling, no
resume, no quality knob and no provenance capture. This run needs all four, plus
a crossed-axis expansion (subject x rendering x palette x variant) that a flat
list cannot express. generate_images.py stays as-is for manifest batches; this
is the art-night orchestrator. The two share the OpenAI Images request shape and
nothing else -- that duplication is deliberate and is called out in the plan.

Guarantees this script is supposed to give:

  1. --dry-run prints EVERY assembled prompt and the projected cost, and makes
     zero network calls.
  2. A hard USD ceiling (HARD_CEILING_USD below) that no CLI flag can raise.
     Cost is RESERVED before a request is dispatched and refunded on failure,
     so concurrency cannot walk past the ceiling.
  3. Resume: every completed image appends one line to a JSONL ledger, flushed
     and fsynced. Re-running skips job ids already in the ledger. Dying at image
     300 of 600 costs at most one image.
  4. Provenance at the point of generation: a sidecar <stem>.meta.json per
     master plus the ledger line, both carrying the full prompt, its sha256, the
     model, size, quality, timestamp, tariff cost and the sha256 of the taste
     brief that shaped it. See coordination#32 -- pdoom1 cannot yet emit origin
     metadata that survives to a consumer, so this run at least records it in a
     form a later capture mechanism can read.

  ADR-0019: nothing here is promoted. Everything lands under art_generated/
  (gitignored in full) as Generated / Library.

Usage (see the plan for the recommended order):
    python tools/assets/run_art_night.py --wave l0 --dry-run
    python tools/assets/run_art_night.py --wave overnight
    python tools/assets/run_art_night.py --wave l2 --picks <picks.json>
    python tools/assets/run_art_night.py --wave l3 --picks <picks.json>
    python tools/assets/run_art_night.py --wave topup --picks <picks.json>
    python tools/assets/run_art_night.py --status
"""

import argparse
import base64
import concurrent.futures
import hashlib
import json
import os
import random
import re
import sys
import threading
import time
from datetime import datetime, timezone
from io import BytesIO
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
DEFAULT_SPEC = REPO / "tools" / "assets" / "manifests" / "art_night_2026-08-07.json"

# The one number no flag can raise. USD. At USD/AUD 1.4164 (spot 2026-08-05)
# this is AUD 106.94; it only breaches the AUD 110 brief if USD/AUD goes above
# 1.4570. Raising it requires editing this file, which is the intent.
HARD_CEILING_USD = 75.50

DOWNSCALES = {
    "1536x1024": [1536, 1024, 768, 512],
    "1024x1536": [1536, 1024, 768, 512],
    "1024x1024": [1024, 512, 256],
}

MAX_ATTEMPTS = 3
RETRY_BASE_SLEEP_S = 4.0


# --------------------------------------------------------------------------
# small helpers
# --------------------------------------------------------------------------


def sha256_text(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_file(path):
    p = Path(path)
    if not p.exists():
        return None
    return hashlib.sha256(p.read_bytes()).hexdigest()


def utcnow():
    return datetime.now(timezone.utc).isoformat()


def load_spec(path):
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def tariff_usd(spec, model, size, quality):
    table = spec["tariff_usd"].get(model)
    if table is None:
        raise SystemExit(
            f"[ABORT] no tariff recorded for model '{model}'. Add one to the spec "
            "before generating -- an unpriced call cannot be budget-capped."
        )
    by_size = table.get(size)
    if by_size is None:
        raise SystemExit(f"[ABORT] no tariff for {model} at size {size}.")
    price = by_size.get(quality)
    if price is None:
        raise SystemExit(f"[ABORT] no tariff for {model} {size} quality={quality}.")
    return float(price)


# --------------------------------------------------------------------------
# taste brief
# --------------------------------------------------------------------------

ARTBRIEF_KEYS = ("HOLD", "AVOID", "PALETTE", "RENDERING_FAVOURED", "SUBJECT_BOOST", "NOTE")


def load_taste_brief(spec):
    """Read the parallel lane's taste profile if it exists.

    Contract (documented in the plan so the taste lane can target it):
      preferred -- a fenced block tagged 'artbrief' holding KEY: value lines;
      fallback  -- the body under the LAST heading matching /brief/i, appended
                   verbatim as a style clause;
      absent    -- house clauses only, with a loud warning.

    Returns a dict: {present, path, sha256, hold, avoid, palettes, renderings,
    subject_boost, note, raw_clause, source}.
    """
    cfg = spec.get("taste_profile", {})
    rel = cfg.get("path")
    max_chars = int(cfg.get("taste_clause_max_chars", 1400))
    out = {
        "present": False,
        "path": rel,
        "sha256": None,
        "hold": "",
        "avoid": "",
        "palettes": None,
        "renderings": None,
        "subject_boost": None,
        "note": "",
        "raw_clause": "",
        "source": "absent",
    }
    if not rel:
        return out
    path = REPO / rel
    if not path.exists():
        return out

    text = path.read_text(encoding="utf-8", errors="replace")
    out["present"] = True
    out["sha256"] = sha256_file(path)

    fenced = re.search(r"```artbrief\s*\n(.*?)\n```", text, re.DOTALL | re.IGNORECASE)
    if fenced:
        out["source"] = "artbrief-block"
        for line in fenced.group(1).splitlines():
            if ":" not in line:
                continue
            key, _, value = line.partition(":")
            key = key.strip().upper()
            value = value.strip()
            if key not in ARTBRIEF_KEYS or not value:
                continue
            if key == "HOLD":
                out["hold"] = value[:max_chars]
            elif key == "AVOID":
                out["avoid"] = value[:max_chars]
            elif key == "NOTE":
                out["note"] = value
            elif key == "PALETTE":
                out["palettes"] = [v.strip() for v in value.replace(",", " ").split() if v.strip()]
            elif key == "RENDERING_FAVOURED":
                out["renderings"] = [
                    v.strip() for v in value.replace(",", " ").split() if v.strip()
                ]
            elif key == "SUBJECT_BOOST":
                out["subject_boost"] = [
                    v.strip() for v in value.replace(",", " ").split() if v.strip()
                ]
        return out

    headings = [m for m in re.finditer(r"^#{1,6}\s+(.*)$", text, re.MULTILINE)]
    brief_heads = [m for m in headings if re.search(r"brief", m.group(1), re.IGNORECASE)]
    if brief_heads:
        head = brief_heads[-1]
        nxt = next((m for m in headings if m.start() > head.start()), None)
        body = text[head.end() : (nxt.start() if nxt else len(text))].strip()
        body = re.sub(r"\s+", " ", body)[:max_chars]
        out["raw_clause"] = body
        out["hold"] = body
        out["source"] = "brief-heading"
    return out


# --------------------------------------------------------------------------
# expansion
# --------------------------------------------------------------------------


def _resolve_axis(spec, brief, axis, value):
    """Resolve a cross value: '*', '@alias', or an explicit list of ids."""
    if isinstance(value, list):
        return list(value)
    if value == "*":
        if axis == "subject":
            return [s["id"] for s in spec["subjects"]]
        if axis == "palette":
            return [p["id"] for p in spec["palettes"]]
        if axis == "rendering":
            return [r["id"] for r in spec["renderings"]]
        raise SystemExit(f"[ABORT] '*' is not defined for axis '{axis}'.")
    if isinstance(value, str) and value.startswith("@"):
        alias = value[1:]
        if alias == "swatch_anchors":
            return list(spec["swatch_anchors"])
        if alias == "palette_block_subjects":
            return list(spec["palette_block_subjects"])
        if alias == "depth_renderings":
            return list(brief["renderings"] or spec["depth_renderings_default"])
        if alias == "palette_block_palettes":
            return list(brief["palettes"] or spec["palette_block_palettes_default"])
        raise SystemExit(f"[ABORT] unknown alias '@{alias}' on axis '{axis}'.")
    return [value]


def _house_default_palette(spec, brief):
    """The single palette L1's scene blocks hold constant.

    Deliberate design fact, stated in the plan: L1 does NOT wait on L0's palette
    verdict, because both run in the same unattended wave. L1 holds one palette
    constant (the brief's first pick, else the first house palette) and treats
    palette as a separate block instead. L0's verdict constrains L2 and L3.
    """
    if brief["palettes"]:
        return brief["palettes"][0]
    for p in spec["palettes"]:
        if p.get("house"):
            return p["id"]
    return spec["palettes"][0]["id"]


def _by_id(items, key):
    return {item["id"]: item for item in items}


def assemble_scene_prompt(spec, brief, subject_id, rendering_id, palette_id, composition_id, extra):
    subjects = _by_id(spec["subjects"], "id")
    renderings = _by_id(spec["renderings"], "id")
    palettes = _by_id(spec["palettes"], "id")
    base = spec["base_clauses"]
    comp = spec["composition_clauses"]

    parts = [
        base["poster_base"],
        base["poster_lighting"],
        base["poster_people"],
        base["poster_props"],
        base["poster_safety"],
        base["poster_tone"],
    ]
    if rendering_id:
        parts.append(renderings[rendering_id]["clause"])
    if palette_id:
        parts.append(palettes[palette_id]["clause"])
    if brief["hold"]:
        parts.append("HOUSE TASTE (measured from prior verdicts): " + brief["hold"])
    if brief["avoid"]:
        parts.append("AVOID: " + brief["avoid"])
    parts.append(comp.get(composition_id or "c_default", comp["c_default"]))
    for clause in extra or []:
        parts.append(clause)
    parts.append("SUBJECT: " + subjects[subject_id]["clause"])
    return ", ".join(p.strip().rstrip(",") for p in parts if p)


def assemble_swatch_prompt(spec, brief, palette_id):
    palettes = _by_id(spec["palettes"], "id")
    sw = spec["swatch_clauses"]
    parts = [sw["sheet_base"], sw["sheet_structure"], palettes[palette_id]["clause"]]
    if brief["hold"]:
        parts.append("HOUSE TASTE (measured from prior verdicts): " + brief["hold"])
    return ", ".join(parts)


def make_job(spec, level, block_id, cell_key, prompt, size, quality, model, variant):
    out_dir = REPO / "art_generated" / f"{spec.get('output_prefix', 'an0807_')}{block_id}" / "v1"
    base_name = f"{cell_key}_v{variant}"
    return {
        "job_id": f"{level}|{block_id}|{cell_key}|v{variant}",
        "level": level,
        "block": block_id,
        "cell": cell_key,
        "variant": variant,
        "prompt": prompt,
        "prompt_sha256": sha256_text(prompt),
        "size": size,
        "quality": quality,
        "model": model,
        "background": spec.get("background", "opaque"),
        "out_dir": str(out_dir),
        "base_name": base_name,
        "master_path": str(out_dir / f"{base_name}_{size.split('x')[0]}.png"),
        "cost_usd": tariff_usd(spec, model, size, quality),
    }


def expand_level_l0_l1(spec, brief, level_key):
    level = spec["levels"][level_key]
    size = level["size"]
    quality = level["quality"]
    default_model = spec["model"]
    house_palette = _house_default_palette(spec, brief)
    jobs = []

    for block in level["blocks"]:
        model = block.get("model", default_model)
        cross = block.get("cross", {})
        subj_ids = (
            _resolve_axis(spec, brief, "subject", cross["subject"])
            if "subject" in cross
            else [None]
        )
        pal_ids = (
            _resolve_axis(spec, brief, "palette", cross["palette"])
            if "palette" in cross
            else [None]
        )
        rend_ids = (
            _resolve_axis(spec, brief, "rendering", cross["rendering"])
            if "rendering" in cross
            else [None]
        )

        if pal_ids == [None]:
            fixed = block.get("palette")
            pal_ids = [house_palette if fixed == "@house_default" else fixed]
        if rend_ids == [None]:
            rend_ids = [block.get("rendering")]

        variants = int(block.get("variants", 1))
        # variant_offset lets a depth block continue the numbering of the grid
        # block instead of re-rolling identical prompts under a colliding name.
        # l1_depth starts at v2 so l1_grid's v1 IS the first roll of that cell.
        offset = int(block.get("variant_offset", 0))
        composition = block.get("composition", "c_default")

        for s in subj_ids:
            for r in rend_ids:
                for p in pal_ids:
                    for v in range(1 + offset, variants + 1 + offset):
                        if block["kind"] == "swatch_sheet":
                            prompt = assemble_swatch_prompt(spec, brief, p)
                            cell = f"{p}"
                        else:
                            prompt = assemble_scene_prompt(spec, brief, s, r, p, composition, None)
                            cell = "_".join(x for x in (s, r, p) if x)
                        jobs.append(
                            make_job(
                                spec, level_key, block["id"], cell, prompt, size, quality, model, v
                            )
                        )
    return jobs


def expand_level_l2(spec, brief, picks):
    """picks: list of {subject, rendering, palette} dicts parsed from L1 ids."""
    level = spec["levels"]["L2"]
    size, quality = level["size"], level["quality"]
    model = spec["model"]
    axes = level["axes"]
    steps_per_pick = int(level["steps_per_pick"])
    jobs = []

    for i, pick in enumerate(picks):
        axis = axes[i % len(axes)]
        steps = axis["steps"][:steps_per_pick]
        for j, step in enumerate(steps, 1):
            composition = pick.get("composition", "c_default")
            extra = []
            if step.startswith("@composition:"):
                composition = step.split(":", 1)[1]
            else:
                extra.append(step)
            prompt = assemble_scene_prompt(
                spec,
                brief,
                pick["subject"],
                pick["rendering"],
                pick["palette"],
                composition,
                extra,
            )
            cell = f"{pick['subject']}_{pick['rendering']}_{pick['palette']}_{axis['id']}_s{j}"
            jobs.append(
                make_job(spec, "L2", f"l2_{axis['id']}", cell, prompt, size, quality, model, 1)
            )
    return jobs


def expand_level_l3(spec, brief, picks):
    level = spec["levels"]["L3"]
    quality = level["quality"]
    model = spec["model"]
    land, port = level["size"], level["portrait_size"]
    n_land = int(level["landscape_per_pick"])
    n_port = int(level["portrait_per_pick"])
    jobs = []
    for pick in picks:
        cell = f"{pick['subject']}_{pick['rendering']}_{pick['palette']}"
        for v in range(1, n_land + 1):
            prompt = assemble_scene_prompt(
                spec,
                brief,
                pick["subject"],
                pick["rendering"],
                pick["palette"],
                pick.get("composition", "c_default"),
                None,
            )
            jobs.append(make_job(spec, "L3", "l3_hero_land", cell, prompt, land, quality, model, v))
        for v in range(1, n_port + 1):
            prompt = assemble_scene_prompt(
                spec, brief, pick["subject"], pick["rendering"], pick["palette"], "c_portrait", None
            )
            jobs.append(make_job(spec, "L3", "l3_hero_port", cell, prompt, port, quality, model, v))
    return jobs


def expand_topup(spec, brief, picks, budget_usd):
    """Anti-underspend wave: extra variants of winning L1 cells until the money
    is gone. Variant numbers start at 100 so they never collide with L1 ids."""
    level = spec["levels"]["L1"]
    size, quality, model = level["size"], level["quality"], spec["model"]
    unit = tariff_usd(spec, model, size, quality)
    if unit <= 0:
        return []
    n = int(budget_usd // unit)
    jobs = []
    if not picks:
        return jobs
    v = 100
    while len(jobs) < n:
        for pick in picks:
            if len(jobs) >= n:
                break
            prompt = assemble_scene_prompt(
                spec,
                brief,
                pick["subject"],
                pick["rendering"],
                pick["palette"],
                pick.get("composition", "c_default"),
                None,
            )
            cell = f"{pick['subject']}_{pick['rendering']}_{pick['palette']}"
            jobs.append(make_job(spec, "TOPUP", "topup_l1", cell, prompt, size, quality, model, v))
        v += 1
    return jobs


# --------------------------------------------------------------------------
# picks
# --------------------------------------------------------------------------

FAVOURABLE_TAGS = {"love", "like", "promote", "favour", "favor", "hero", "yes", "keep"}
CELL_RE = re.compile(r"^(s\d{2})_(r\d{2})_(p\d{2})")


def load_picks(path, spec, limit=None):
    """Accept either a flat list of ids or the review tools' {rel: [tags]} map.

    Ids are the cell keys this script writes (s07_r03_p01), or full gallery ids
    (gen:an0807_l1_grid:s07_r03_p01:2), or master filenames. Anything that does
    not parse is reported rather than silently dropped -- a silently dropped
    pick is exactly the class of wrongness this repo keeps being caught by.
    """
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    if isinstance(raw, dict):
        candidates = [
            k for k, tags in raw.items() if set(t.lower() for t in tags) & FAVOURABLE_TAGS
        ]
    elif isinstance(raw, list):
        candidates = [c if isinstance(c, str) else c.get("id", "") for c in raw]
    else:
        raise SystemExit("[ABORT] picks file must be a list or an object of {id: [tags]}.")

    subj_ok = {s["id"] for s in spec["subjects"]}
    rend_ok = {r["id"] for r in spec["renderings"]}
    pal_ok = {p["id"] for p in spec["palettes"]}

    picks, unparsed, seen = [], [], set()
    for cand in candidates:
        tail = cand.split(":")[-2] if cand.startswith("gen:") else Path(cand).name
        m = CELL_RE.match(tail)
        if not m:
            unparsed.append(cand)
            continue
        s, r, p = m.groups()
        if s not in subj_ok or r not in rend_ok or p not in pal_ok:
            unparsed.append(cand)
            continue
        key = (s, r, p)
        if key in seen:
            continue
        seen.add(key)
        picks.append({"subject": s, "rendering": r, "palette": p})

    if unparsed:
        print(f"[!] {len(unparsed)} pick entries did not parse as an art-night cell:")
        for u in unparsed[:10]:
            print(f"      {u}")
        if len(unparsed) > 10:
            print(f"      ... and {len(unparsed) - 10} more")
    if limit:
        picks = picks[:limit]
    return picks


# --------------------------------------------------------------------------
# ledger + budget
# --------------------------------------------------------------------------


class Ledger:
    def __init__(self, path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        self.done = {}
        self.spent = 0.0
        if self.path.exists():
            for line in self.path.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if not line:
                    continue
                try:
                    rec = json.loads(line)
                except ValueError:
                    continue
                if rec.get("status") == "ok":
                    self.done[rec["job_id"]] = rec
                    self.spent += float(rec.get("cost_usd", 0.0))

    def append(self, record):
        with self._lock:
            with open(self.path, "a", encoding="utf-8") as fh:
                fh.write(json.dumps(record, ensure_ascii=True) + "\n")
                fh.flush()
                os.fsync(fh.fileno())
            if record.get("status") == "ok":
                self.done[record["job_id"]] = record


class Budget:
    """Reserve-before-dispatch so N concurrent workers cannot overshoot."""

    def __init__(self, ceiling_usd, already_spent_usd):
        self.ceiling = float(ceiling_usd)
        self.committed = float(already_spent_usd)
        self._lock = threading.Lock()
        self.stopped = False

    def reserve(self, amount):
        with self._lock:
            if self.stopped:
                return False
            if self.committed + amount > self.ceiling + 1e-9:
                self.stopped = True
                return False
            self.committed += amount
            return True

    def refund(self, amount):
        with self._lock:
            self.committed -= amount

    @property
    def remaining(self):
        with self._lock:
            return self.ceiling - self.committed


# --------------------------------------------------------------------------
# generation
# --------------------------------------------------------------------------

_client = None
_client_lock = threading.Lock()


def get_client():
    global _client
    with _client_lock:
        if _client is None:
            from openai import OpenAI

            _client = OpenAI()
        return _client


def call_images_api(job):
    """One Images API request. Returns (bytes, api_meta)."""
    kwargs = {
        "model": job["model"],
        "prompt": job["prompt"],
        "size": job["size"],
        "quality": job["quality"],
        "background": job["background"],
    }
    result = get_client().images.generate(**kwargs)
    datum = result.data[0]
    meta = {
        "api_created": getattr(result, "created", None),
        "api_usage": None,
        "revised_prompt": getattr(datum, "revised_prompt", None),
    }
    usage = getattr(result, "usage", None)
    if usage is not None:
        try:
            meta["api_usage"] = usage.model_dump()
        except AttributeError:
            meta["api_usage"] = str(usage)
    return base64.b64decode(datum.b64_json), meta


def write_outputs(job, img_bytes, api_meta, run_meta, staging_dir=None):
    from PIL import Image

    out_dir = Path(job["out_dir"])
    out_dir.mkdir(parents=True, exist_ok=True)
    master = Path(job["master_path"])
    img = Image.open(BytesIO(img_bytes)).convert("RGBA")
    img.save(master)

    master_w, master_h = (int(x) for x in job["size"].split("x"))
    for width in DOWNSCALES.get(job["size"], []):
        if width >= master_w:
            continue
        height = max(1, round(master_h * width / master_w))
        img.resize((width, height), Image.LANCZOS).save(out_dir / f"{job['base_name']}_{width}.png")

    sidecar = {
        "origin": "generated",
        "run_id": run_meta["run_id"],
        "job_id": job["job_id"],
        "level": job["level"],
        "block": job["block"],
        "cell": job["cell"],
        "variant": job["variant"],
        "prompt": job["prompt"],
        "prompt_sha256": job["prompt_sha256"],
        "revised_prompt": api_meta.get("revised_prompt"),
        "backend": run_meta["backend"],
        "model": job["model"],
        "size": job["size"],
        "quality": job["quality"],
        "background": job["background"],
        "seed": None,
        "seed_note": "The OpenAI Images API exposes no seed parameter, so this "
        "image is not reproducible from its record. Recorded as null rather "
        "than omitted so a consumer can tell the difference.",
        "generated_at_utc": utcnow(),
        "cost_usd_tariff": job["cost_usd"],
        "cost_source": run_meta["cost_source"],
        "cost_is_billed_truth": False,
        "api_created": api_meta.get("api_created"),
        "api_usage": api_meta.get("api_usage"),
        "taste_profile_path": run_meta["taste_profile_path"],
        "taste_profile_sha256": run_meta["taste_profile_sha256"],
        "taste_profile_source": run_meta["taste_profile_source"],
        "queue_spec_sha256": run_meta["queue_spec_sha256"],
        "tool": "tools/assets/run_art_night.py",
        "master_path": str(master.relative_to(REPO)),
        "master_bytes": master.stat().st_size,
        "promotion_state": "library",
        "promotion_note": "ADR-0019: no promotion without a mechanically "
        "verified demand entry. This file is Generated / Library.",
    }
    with open(master.with_suffix(".meta.json"), "w", encoding="utf-8") as fh:
        json.dump(sidecar, fh, ensure_ascii=True, indent=2)

    if staging_dir:
        import shutil

        stage = Path(staging_dir)
        stage.mkdir(parents=True, exist_ok=True)
        shutil.copy2(master, stage / master.name)
        shutil.copy2(master.with_suffix(".meta.json"), stage / (master.stem + ".meta.json"))

    return sidecar


def run_job(job, ledger, budget, run_meta, staging_dir):
    if not budget.reserve(job["cost_usd"]):
        return "ceiling"
    last_err = None
    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            img_bytes, api_meta = call_images_api(job)
            sidecar = write_outputs(job, img_bytes, api_meta, run_meta, staging_dir)
            ledger.append(
                {
                    "status": "ok",
                    "job_id": job["job_id"],
                    "cost_usd": job["cost_usd"],
                    "attempt": attempt,
                    "recorded_at_utc": utcnow(),
                    "master_path": sidecar["master_path"],
                    "prompt_sha256": job["prompt_sha256"],
                    "model": job["model"],
                    "size": job["size"],
                    "quality": job["quality"],
                }
            )
            return "ok"
        except Exception as exc:  # noqa: BLE001 -- an overnight run must not die on one image
            last_err = f"{type(exc).__name__}: {exc}"
            if attempt < MAX_ATTEMPTS:
                time.sleep(RETRY_BASE_SLEEP_S * (2 ** (attempt - 1)) + random.uniform(0, 1.5))
    budget.refund(job["cost_usd"])
    ledger.append(
        {
            "status": "failed",
            "job_id": job["job_id"],
            "cost_usd": 0.0,
            "attempts": MAX_ATTEMPTS,
            "recorded_at_utc": utcnow(),
            "error": last_err,
            "model": job["model"],
        }
    )
    return "failed"


# --------------------------------------------------------------------------
# reporting
# --------------------------------------------------------------------------


def summarise(jobs):
    by_block = {}
    for j in jobs:
        rec = by_block.setdefault(
            j["block"],
            {"n": 0, "usd": 0.0, "size": j["size"], "q": j["quality"], "model": j["model"]},
        )
        rec["n"] += 1
        rec["usd"] += j["cost_usd"]
    return by_block


def print_projection(jobs, brief, fx, title):
    by_block = summarise(jobs)
    total_usd = sum(j["cost_usd"] for j in jobs)
    print("")
    print("=" * 78)
    print(f"PROJECTION -- {title}")
    print("=" * 78)
    print(f"{'block':<20} {'model':<14} {'size':<11} {'qual':<7} {'n':>5} {'USD':>9}")
    print("-" * 78)
    for block, rec in by_block.items():
        print(
            f"{block:<20} {rec['model']:<14} {rec['size']:<11} {rec['q']:<7} "
            f"{rec['n']:>5} {rec['usd']:>9.2f}"
        )
    print("-" * 78)
    print(f"{'TOTAL':<20} {'':<14} {'':<11} {'':<7} {len(jobs):>5} {total_usd:>9.2f}")
    print(
        f"{'':<20} {'':<14} {'':<11} {'':<7} {'AUD':>5} {total_usd * fx:>9.2f}  (at {fx} AUD/USD)"
    )
    print("")
    print(
        f"taste brief: {brief['source']}"
        + (f"  sha256={brief['sha256'][:12]}" if brief["sha256"] else "")
    )
    if not brief["present"]:
        print(
            "[!] WARNING: the taste profile was NOT found. Prompts fall back to the\n"
            "    in-repo house clauses. That is a legitimate run, but it is a BLIND\n"
            "    run -- Pip's 151 picks are not shaping anything. Check the path in\n"
            "    the spec before committing money to it."
        )
    return total_usd


# --------------------------------------------------------------------------
# main
# --------------------------------------------------------------------------

WAVES = {
    "l0": ["L0"],
    "l1": ["L1"],
    "overnight": ["L0", "L1"],
    "l2": ["L2"],
    "l3": ["L3"],
    "topup": ["TOPUP"],
}


def build_jobs(spec, brief, wave, args):
    jobs = []
    for level_key in WAVES[wave]:
        if level_key in ("L0", "L1"):
            jobs.extend(expand_level_l0_l1(spec, brief, level_key))
        elif level_key == "L2":
            picks = load_picks(args.picks, spec, spec["levels"]["L2"]["picks_target"])
            if not picks:
                raise SystemExit("[ABORT] L2 needs picks and none parsed. Nothing generated.")
            print(f"[*] L2 driving from {len(picks)} picks.")
            jobs.extend(expand_level_l2(spec, brief, picks))
        elif level_key == "L3":
            picks = load_picks(args.picks, spec, spec["levels"]["L3"]["picks_target"])
            if not picks:
                raise SystemExit("[ABORT] L3 needs picks and none parsed. Nothing generated.")
            print(f"[*] L3 driving from {len(picks)} picks.")
            jobs.extend(expand_level_l3(spec, brief, picks))
        elif level_key == "TOPUP":
            picks = load_picks(args.picks, spec)
            budget_left = args.topup_usd
            print(f"[*] topup driving from {len(picks)} picks, budget USD {budget_left:.2f}.")
            jobs.extend(expand_topup(spec, brief, picks, budget_left))
    return jobs


def main():
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("--spec", default=str(DEFAULT_SPEC))
    ap.add_argument("--wave", choices=sorted(WAVES), help="which level(s) to run")
    ap.add_argument("--picks", help="picks JSON for L2 / L3 / topup")
    ap.add_argument(
        "--dry-run",
        action="store_true",
        help="print every prompt and the projected cost; no network calls, no spend",
    )
    ap.add_argument(
        "--show-prompts",
        action="store_true",
        help="with --dry-run, print the FULL prompt text for every job (very long)",
    )
    ap.add_argument(
        "--prompt-sample",
        type=int,
        default=6,
        help="how many full prompts to print in a dry run (default 6)",
    )
    ap.add_argument(
        "--ceiling-usd",
        type=float,
        default=None,
        help=f"lower the ceiling for this invocation. Cannot exceed the hard ceiling of {HARD_CEILING_USD}",
    )
    ap.add_argument("--topup-usd", type=float, default=0.0, help="budget for the topup wave")
    ap.add_argument("--concurrency", type=int, default=4)
    ap.add_argument("--limit", type=int, help="cap the number of jobs (testing)")
    ap.add_argument(
        "--allow-partial",
        action="store_true",
        help="if the projection exceeds the remaining ceiling, run what fits instead of aborting",
    )
    ap.add_argument(
        "--force", action="store_true", help="regenerate jobs already recorded done in the ledger"
    )
    ap.add_argument("--status", action="store_true", help="print ledger status and exit")
    ap.add_argument("--yes", "-y", action="store_true", help="skip the confirmation prompt")
    args = ap.parse_args()

    spec = load_spec(args.spec)
    spec_sha = sha256_file(args.spec)
    fx = float(spec["budget"]["fx_aud_per_usd"])
    ledger_path = REPO / spec["output_root"] / "ledger.jsonl"
    ledger = Ledger(ledger_path)

    if args.status or not args.wave:
        print(f"run_id       : {spec['run_id']}")
        print(f"ledger       : {ledger_path}")
        print(f"images done  : {len(ledger.done)}")
        print(f"spent (tariff): USD {ledger.spent:.2f}  /  AUD {ledger.spent * fx:.2f}")
        print(f"hard ceiling : USD {HARD_CEILING_USD:.2f}  /  AUD {HARD_CEILING_USD * fx:.2f}")
        print(f"remaining    : USD {HARD_CEILING_USD - ledger.spent:.2f}")
        print(
            f"underspend floor: USD {spec['budget']['underspend_floor_usd']:.2f} "
            "(below this after L3, run --wave topup)"
        )
        if not args.wave:
            return 0

    brief = load_taste_brief(spec)
    jobs = build_jobs(spec, brief, args.wave, args)

    if not args.force:
        jobs = [j for j in jobs if j["job_id"] not in ledger.done]
    if args.limit:
        jobs = jobs[: args.limit]

    if not jobs:
        print("[*] nothing to do -- every job in this wave is already in the ledger.")
        return 0

    projected = print_projection(jobs, brief, fx, f"wave={args.wave}")
    print(f"already spent this run (tariff): USD {ledger.spent:.2f}")
    print(f"hard ceiling                   : USD {HARD_CEILING_USD:.2f}")

    ceiling = HARD_CEILING_USD
    if args.ceiling_usd is not None:
        if args.ceiling_usd > HARD_CEILING_USD:
            print(
                f"[!] --ceiling-usd {args.ceiling_usd} is above the hard ceiling; clamping to {HARD_CEILING_USD}."
            )
        ceiling = min(args.ceiling_usd, HARD_CEILING_USD)

    if ledger.spent + projected > ceiling + 1e-9:
        over = ledger.spent + projected - ceiling
        msg = (
            f"[ABORT] this wave would take the run to USD {ledger.spent + projected:.2f}, "
            f"which is USD {over:.2f} over the ceiling of USD {ceiling:.2f} "
            f"(AUD {ceiling * fx:.2f})."
        )
        if not args.allow_partial:
            print(msg)
            print(
                "        Nothing was generated. Re-run with --allow-partial to fill the "
                "remaining headroom, or trim the wave."
            )
            return 2
        print(msg.replace("[ABORT]", "[!]"))
        print("        --allow-partial: generating until the ceiling is reached.")

    if args.dry_run:
        n = len(jobs) if args.show_prompts else min(args.prompt_sample, len(jobs))
        print(
            f"--- DRY RUN: {n} of {len(jobs)} full prompts "
            f"({'all' if args.show_prompts else 'use --show-prompts for all'}) ---\n"
        )
        step = max(1, len(jobs) // n) if n else 1
        for j in jobs[::step][:n] if not args.show_prompts else jobs:
            print(
                f"[{j['job_id']}]  {j['size']} {j['quality']} {j['model']}  USD {j['cost_usd']:.3f}"
            )
            print(f"  -> {j['master_path']}")
            print(f"  prompt sha256 {j['prompt_sha256'][:16]}")
            print(f"  {j['prompt']}")
            print("")
        print(
            f"[DRY RUN] {len(jobs)} images, USD {projected:.2f} / AUD {projected * fx:.2f}. "
            "Zero API calls were made and zero dollars were spent."
        )
        return 0

    if not args.yes:
        answer = input(
            f"Generate {len(jobs)} images for about USD {projected:.2f} "
            f"(AUD {projected * fx:.2f})? [y/N]: "
        )
        if answer.strip().lower() != "y":
            print("Cancelled. Nothing generated.")
            return 0

    run_meta = {
        "run_id": spec["run_id"],
        "backend": spec.get("backend", "openai"),
        "cost_source": spec["_meta"]["cost_source"],
        "taste_profile_path": brief["path"],
        "taste_profile_sha256": brief["sha256"],
        "taste_profile_source": brief["source"],
        "queue_spec_sha256": spec_sha,
    }
    staging = None
    if args.wave == "l3":
        staging = spec.get("masters_staging")

    budget = Budget(ceiling, ledger.spent)
    counts = {"ok": 0, "failed": 0, "ceiling": 0}
    started = time.time()

    with concurrent.futures.ThreadPoolExecutor(max_workers=max(1, args.concurrency)) as pool:
        futures = {pool.submit(run_job, j, ledger, budget, run_meta, staging): j for j in jobs}
        for i, fut in enumerate(concurrent.futures.as_completed(futures), 1):
            outcome = fut.result()
            counts[outcome] += 1
            if i % 10 == 0 or outcome != "ok":
                elapsed = time.time() - started
                rate = i / elapsed if elapsed else 0
                left = (len(jobs) - i) / rate / 60 if rate else 0
                print(
                    f"[{i}/{len(jobs)}] ok={counts['ok']} failed={counts['failed']} "
                    f"stopped={counts['ceiling']} | USD {budget.committed:.2f} "
                    f"| ~{left:.0f} min left"
                )

    print("")
    print("=" * 78)
    print(
        f"wave {args.wave} complete: ok={counts['ok']} failed={counts['failed']} "
        f"not-started-at-ceiling={counts['ceiling']}"
    )
    print(f"run total (tariff): USD {ledger.spent:.2f} / AUD {ledger.spent * fx:.2f}")
    print(f"ledger            : {ledger_path}")
    print("gallery           : python tools/art_review/build_full_gallery.py --open")
    if counts["ceiling"]:
        print("[!] the ceiling stopped this wave. Nothing overran; some jobs were skipped.")
    print(
        "Tariff dollars are the PUBLISHED price, not billed truth. Reconcile "
        "against the OpenAI billing dashboard before quoting a spend."
    )
    print("=" * 78)
    return 0


if __name__ == "__main__":
    sys.exit(main())
