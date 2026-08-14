#!/usr/bin/env python3
"""Provenance census over the art_night_2026-08-07 sidecars.

READ-ONLY. Walks art_generated/**/*.meta.json plus the run ledger and prints
every number quoted in PROVENANCE_COMPLETENESS.md, tagged with the section it
supports. Run from the repo root:

    python docs/art/audit_2026-08-13/provenance_census.py

Sections can be run individually:

    python docs/art/audit_2026-08-13/provenance_census.py --section 4

Sections: 0 inventory, 1 field coverage, 2 cost, 3 mix, 4 prompt clusters,
5 lineage, 6 pii, 7 publishability, 8 integrity, 9 ledger.
"""

import argparse
import collections
import glob
import hashlib
import json
import os
import re
import subprocess
import sys

SEP = chr(92)  # backslash; sidecars store Windows-style master_path
LEDGER = "art_generated/art_night_2026-08-07/ledger.jsonl"

QUEUE_SPECS = {
    "d4287c06daac339ee98606d27fd3953e01f379bed0bbbf8cff59dae245c38c20": "L0 + L1 wave",
    "a74cfc26733e278ca7a516ef1e35d294167c8f27da0a7af0518ce719efe1a3db": "L2 wave",
    "8c2a2a8d6f72f444283dca4a1a9dc066287f267a1de37a0cd8ff8a431d61d108": "L3 wave",
}

# Tokens that are legitimately expected in this run's prompt corpus and file
# names. Anything alphabetic outside these sets is printed for human review.
FILENAME_TOKEN_ALLOW = {
    "anchors",
    "art",
    "decay",
    "distance",
    "family",
    "grid",
    "hero",
    "json",
    "jsonl",
    "land",
    "ledger",
    "log",
    "meta",
    "night",
    "palette",
    "pitch",
    "png",
    "port",
    "probe",
    "quiet",
    "run",
    "sheets",
    "space",
    "style",
    "title",
    "tween",
    "yaw",
}


def load_metas():
    out = []
    for f in sorted(glob.glob("art_generated/**/*.meta.json", recursive=True)):
        with open(f, "r", encoding="utf-8") as fh:
            out.append((f.replace(os.sep, "/"), json.load(fh)))
    return out


def norm(p):
    return p.replace(SEP, "/").replace(os.sep, "/")


def asset_id(m):
    block_dir = norm(m["master_path"]).split("/")[1]
    return "gen:%s:%s:v%d" % (block_dir, m["cell"], m["variant"])


def section0(metas):
    print("== 0 INVENTORY ==")
    print("sidecars:", len(metas))
    print("run_id values:", dict(collections.Counter(m["run_id"] for _, m in metas)))
    dirs = collections.Counter(os.path.dirname(f) for f, _ in metas)
    for d, c in sorted(dirs.items()):
        print("   %-44s %4d" % (d, c))


def section1(metas):
    n = len(metas)
    print("== 1 FIELD COVERAGE ==")
    present = collections.Counter()
    nulls = collections.Counter()
    for _, m in metas:
        for k, v in m.items():
            present[k] += 1
            if v is None:
                nulls[k] += 1
    for k in sorted(present):
        print(
            "%-24s %4d/%d %6.2f%%  null=%d" % (k, present[k], n, 100.0 * present[k] / n, nulls[k])
        )
    print("-- always-null fields:", sorted(k for k in present if nulls[k] == present[k]))
    nested = collections.Counter()
    for _, m in metas:
        au = m.get("api_usage") or {}
        for k in au:
            nested["api_usage." + k] += 1
        for parent in ("input_tokens_details", "output_tokens_details"):
            for k in au.get(parent) or {}:
                nested["api_usage.%s.%s" % (parent, k)] += 1
    for k in sorted(nested):
        print("%-48s %4d/%d" % (k, nested[k], n))


def section2(metas):
    print("== 2 COST (tariff estimate; cost_is_billed_truth is false everywhere) ==")
    print(
        "cost_is_billed_truth values:",
        dict(collections.Counter(str(m["cost_is_billed_truth"]) for _, m in metas)),
    )
    print("TOTAL cost_usd_tariff: %.4f USD" % sum(m["cost_usd_tariff"] for _, m in metas))
    print(
        "distinct unit tariffs:", dict(collections.Counter(m["cost_usd_tariff"] for _, m in metas))
    )
    for field in ("level", "block"):
        agg = collections.defaultdict(lambda: [0, 0.0])
        for _, m in metas:
            agg[m[field]][0] += 1
            agg[m[field]][1] += m["cost_usd_tariff"]
        print("-- per %s --" % field)
        for k in sorted(agg):
            n, c = agg[k]
            print("   %-24s n=%4d  %8.4f USD  unit=%.4f" % (k, n, c, c / n))
    # tariff/model consistency: cost_source names gpt-image-1.5 only
    off = [(f, m["model"]) for f, m in metas if m["model"] != "gpt-image-1.5"]
    print("sidecars whose model is NOT the model named in cost_source:", len(off))
    for f, mod in off:
        print("   %s  model=%s" % (f, mod))


def section3(metas):
    n = len(metas)
    print("== 3 MODEL / SIZE / QUALITY / BACKGROUND ==")
    for field in (
        "backend",
        "model",
        "size",
        "quality",
        "background",
        "origin",
        "variant",
        "promotion_state",
        "taste_profile_source",
        "tool",
    ):
        print("-- %s" % field)
        for v, c in collections.Counter(str(m[field]) for _, m in metas).most_common():
            print("   %-32s %4d %6.2f%%" % (v, c, 100.0 * c / n))
    print("-- model x size x quality x background")
    combo = collections.Counter(
        (m["model"], m["size"], m["quality"], m["background"]) for _, m in metas
    )
    for k, c in combo.most_common():
        print("   %-14s %-10s %-7s %-8s %4d" % (k[0], k[1], k[2], k[3], c))


def section4(metas):
    n = len(metas)
    print("== 4 PROMPT CLUSTERING ==")
    hashes = collections.Counter(m["prompt_sha256"] for _, m in metas)
    print("images:", n)
    print("distinct prompt_sha256:", len(hashes))
    print("mean images per distinct prompt: %.4f" % (float(n) / len(hashes)))
    hist = collections.Counter(hashes.values())
    for size in sorted(hist):
        print(
            "   cluster size %d -> %d prompts -> %d images" % (size, hist[size], size * hist[size])
        )
    print("largest cluster size:", max(hashes.values()))
    for h, c in hashes.most_common(5):
        ex = next(f for f, m in metas if m["prompt_sha256"] == h)
        print("   %s x%d  e.g. %s" % (h[:16], c, ex))
    mism = sum(
        1
        for _, m in metas
        if hashlib.sha256(m["prompt"].encode("utf-8")).hexdigest() != m["prompt_sha256"]
    )
    print("prompt_sha256 that do NOT equal sha256(utf8(prompt)):", mism)
    # A distinct prompt_sha256 is NOT a distinct brief. Every prompt in this run
    # is <shared style preamble> + "SUBJECT:" + <brief>. Split on that marker to
    # separate "how many briefs" from "how many style variations of a brief".
    subj_img = collections.Counter()
    subj_prompt = collections.Counter()
    pre_prompt = collections.Counter()
    nosub = 0
    for _, m in metas:
        p = m["prompt"]
        subj_img[
            p.split("SUBJECT:", 1)[1].strip() if "SUBJECT:" in p else "<no SUBJECT clause>"
        ] += 1
    for p in set(m["prompt"] for _, m in metas):
        if "SUBJECT:" not in p:
            nosub += 1
            continue
        a, b = p.split("SUBJECT:", 1)
        pre_prompt[a.strip()] += 1
        subj_prompt[b.strip()] += 1
    print("-- brief vs variation --")
    print("   distinct prompts with no SUBJECT: marker:", nosub)
    print("   distinct SUBJECT clauses across all images:", len(subj_img))
    print("   distinct SUBJECT clauses among prompts that have one:", len(subj_prompt))
    print("   distinct pre-SUBJECT style preambles:", len(pre_prompt))
    print("   largest SUBJECT cluster (images):", max(subj_img.values()))
    print("   SUBJECT cluster sizes (images):", sorted(subj_img.values(), reverse=True))
    print("-- distinct prompts per block --")
    per = collections.defaultdict(set)
    tot = collections.Counter()
    for _, m in metas:
        per[m["block"]].add(m["prompt_sha256"])
        tot[m["block"]] += 1
    for b in sorted(per):
        print(
            "   %-24s images=%4d distinct=%4d ratio=%.2f"
            % (b, tot[b], len(per[b]), float(tot[b]) / len(per[b]))
        )


def section5(metas):
    print("== 5 BRIEF LINEAGE ==")
    for field in ("taste_profile_path", "taste_profile_sha256", "queue_spec_sha256"):
        c = collections.Counter(m[field] for _, m in metas)
        print("-- %s distinct=%d" % (field, len(c)))
        for v, k in c.most_common():
            print("   %-66s %4d  %s" % (v, k, QUEUE_SPECS.get(v, "")))
    tp = "docs/design/TASTE_PROFILE_2026-08-06.md"
    if os.path.exists(tp):
        h = hashlib.sha256(open(tp, "rb").read()).hexdigest()
        print("on-disk sha256(%s) = %s" % (tp, h))
        print("matches taste_profile_sha256:", h == metas[0][1]["taste_profile_sha256"])
    else:
        print("taste profile MISSING on disk:", tp)
    print("-- block -> queue_spec --")
    bl = collections.defaultdict(set)
    for _, m in metas:
        bl[m["block"]].add(m["queue_spec_sha256"][:12])
    for b in sorted(bl):
        print("   %-24s %s" % (b, sorted(bl[b])))
    print("-- where each queue_spec_sha256 can be recovered --")
    try:
        objs = subprocess.check_output(
            ["git", "rev-list", "--all", "--objects", "--", "tools/assets/manifests"], text=True
        ).splitlines()
    except Exception as e:
        print("   git lookup failed:", e)
        return
    found = collections.defaultdict(list)
    seen = set()
    for line in objs:
        parts = line.split(" ", 1)
        if len(parts) != 2 or parts[0] in seen:
            continue
        seen.add(parts[0])
        try:
            blob = subprocess.check_output(["git", "cat-file", "-p", parts[0]])
        except Exception:
            continue
        h = hashlib.sha256(blob).hexdigest()
        if h in QUEUE_SPECS:
            found[h].append("git blob %s (%s)" % (parts[0][:12], parts[1]))
    for h, label in QUEUE_SPECS.items():
        print("   %-16s %-12s %s" % (h[:16], label, found.get(h, ["NOT FOUND"])))


def section6(metas):
    print("== 6 PII / THIRD-PARTY SCAN ==")
    prompts = {m["prompt_sha256"]: m["prompt"] for _, m in metas}
    blob = "\n".join(prompts.values())
    print("distinct prompts scanned:", len(prompts))
    print("total prompt characters:", len(blob))
    checks = [
        ("email", r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"),
        ("url", r"(?:https?://|www\.)\S+"),
        ("bare domain", r"\b[a-z0-9-]+\.(?:com|org|net|io|ai|co|uk|gov|edu)\b"),
        ("honorific + name", r"\b(?:Mr|Mrs|Ms|Dr|Prof|Sir|Lady)\.?\s+[A-Z][a-z]+"),
        ("two capitalised words in a row", r"\b[A-Z][a-z]{2,}\s+[A-Z][a-z]{2,}\b"),
        ("non-ascii codepoint", r"[^\x00-\x7f]"),
    ]
    for name, pat in checks:
        hits = sorted(set(re.findall(pat, blob)))
        print("   %-32s hits=%d %s" % (name, len(hits), hits[:20]))
    caps = collections.Counter(re.findall(r"(?<![.!?]\s)(?<!^)\b[A-Z][a-z]{2,}\b", blob, re.M))
    print("   distinct mid-sentence Capitalised tokens: %d -> %s" % (len(caps), sorted(caps)))
    allcaps = sorted(set(re.findall(r"\b[A-Z]{2,}\b", blob)))
    print("   distinct ALLCAPS tokens: %d -> %s" % (len(allcaps), allcaps))
    brands = [
        "openai",
        "anthropic",
        "deepmind",
        "google",
        "microsoft",
        "nvidia",
        "intel",
        "cisco",
        "oracle",
        "amazon",
        "tesla",
        "sony",
        "samsung",
        "xerox",
        "sharpie",
        "post-it",
        "thinkpad",
        "macbook",
        "iphone",
        "beacon",
        "certes",
        "pdoom",
        "godot",
        "github",
        "pip",
    ]
    for b in brands:
        n = len(re.findall(r"\b" + re.escape(b) + r"\b", blob, re.I))
        if n:
            print("   word-boundary brand/identity token %-12s count=%d" % (b, n))
            ctx = sorted(set(re.findall(r".{40}\b" + re.escape(b) + r"\b.{40}", blob, re.I)))
            for c in ctx[:3]:
                print("      context: ..." + c.replace("\n", " ") + "...")
            print("      distinct surrounding contexts:", len(ctx))
    # filenames
    names = set()
    for pat in ("art_generated/an0807_*/**", "art_generated/art_night_2026-08-07/**"):
        for p in glob.glob(pat, recursive=True):
            if os.path.isfile(p):
                names.add(os.path.basename(p))
    for p in glob.glob("art_generated/an0807_*") + glob.glob("art_generated/art_night_2026-08-07"):
        names.add(os.path.basename(p))
    toks = collections.Counter()
    for nm in names:
        for t in re.findall(r"[A-Za-z]{3,}", nm):
            toks[t.lower()] += 1
    print("   filenames+dirnames scanned:", len(names))
    print("   distinct alphabetic tokens (len>=3) across all of them: %d" % len(toks))
    print("   tokens:", sorted(toks))
    print("   tokens OUTSIDE the pipeline vocabulary:", sorted(set(toks) - FILENAME_TOKEN_ALLOW))
    absolute = [
        f
        for f, m in metas
        if re.match(r"^[A-Za-z]:", m["master_path"]) or m["master_path"].startswith("/")
    ]
    print("   master_path values that are absolute (would leak a local user dir):", len(absolute))
    print(
        "   master_path values containing 'Users':",
        sum(1 for _, m in metas if "Users" in m["master_path"]),
    )


def section7(metas):
    print("== 7 PUBLISHABILITY ==")
    n = len(metas)
    for f in (
        "prompt",
        "prompt_sha256",
        "tool",
        "backend",
        "model",
        "size",
        "quality",
        "background",
        "seed",
        "review_state",
        "verdict",
        "reviewed_at",
        "where_used",
        "used_in",
        "consumers",
        "slot",
        "license",
        "usage_rights",
        "promotion_state",
    ):
        print("   %-16s present in %4d/%d sidecars" % (f, sum(1 for _, m in metas if f in m), n))
    ids = {asset_id(m): (f, m) for f, m in metas}
    try:
        rs = json.load(open("tools/art_review/review_state.json", encoding="utf-8"))
    except Exception as e:
        print("   review_state.json unreadable:", e)
        rs = {}
    run_rs = {k: v for k, v in rs.items() if k in ids}
    print("   review_state.json total entries:", len(rs))
    print(
        "   entries that resolve to a run asset: %d (%.2f%% of %d)"
        % (len(run_rs), 100.0 * len(run_rs) / n, n)
    )
    print("   verdict mix:", dict(collections.Counter(v.get("verdict") for v in run_rs.values())))
    per = collections.Counter(ids[k][1]["block"] for k in run_rs)
    tot = collections.Counter(m["block"] for _, m in metas)
    for b in sorted(tot):
        print("      %-24s reviewed %4d/%4d" % (b, per[b], tot[b]))
    try:
        sp = json.load(open("tools/assets/demand/slot_picks.json", encoding="utf-8"))
        print(
            "   demand/slot_picks.json slots=%d frame_roles=%d"
            % (len(sp.get("slots", {})), len(sp.get("frame_roles", {})))
        )
    except Exception as e:
        print("   slot_picks.json unreadable:", e)
    try:
        share = open("docs/copy/art_share_set.json", encoding="utf-8").read()
        mp = set(norm(m["master_path"]) for _, m in metas)
        print(
            "   docs/copy/art_share_set.json names %d of %d run masters"
            % (sum(1 for x in mp if x in share), n)
        )
    except Exception as e:
        print("   art_share_set.json unreadable:", e)


def section8(metas):
    print("== 8 INTEGRITY ==")
    missing = 0
    mismatch = 0
    total = 0
    for _, m in metas:
        p = norm(m["master_path"])
        total += m["master_bytes"]
        if not os.path.exists(p):
            missing += 1
        elif os.path.getsize(p) != m["master_bytes"]:
            mismatch += 1
    print("masters referenced by a sidecar but absent from disk:", missing)
    print("masters whose on-disk size differs from master_bytes:", mismatch)
    print("sum(master_bytes): %d bytes (%.2f GiB)" % (total, total / 1024.0**3))
    print("sum(api_usage.input_tokens): ", sum(m["api_usage"]["input_tokens"] for _, m in metas))
    print("sum(api_usage.output_tokens):", sum(m["api_usage"]["output_tokens"] for _, m in metas))
    print("sum(api_usage.total_tokens): ", sum(m["api_usage"]["total_tokens"] for _, m in metas))
    print(
        "generated_at_utc range:",
        min(m["generated_at_utc"] for _, m in metas),
        "->",
        max(m["generated_at_utc"] for _, m in metas),
    )


def section9(metas):
    print("== 9 LEDGER RECONCILIATION ==")
    if not os.path.exists(LEDGER):
        print("ledger missing:", LEDGER)
        return
    recs = [json.loads(ln) for ln in open(LEDGER, encoding="utf-8") if ln.strip()]
    print("ledger records:", len(recs))
    print("status mix:", dict(collections.Counter(r["status"] for r in recs)))
    ok = [r for r in recs if r["status"] == "ok"]
    bad = [r for r in recs if r["status"] != "ok"]
    print(
        "ledger cost_usd total: %.4f  (ok %.4f, failed %.4f)"
        % (
            sum(r["cost_usd"] for r in recs),
            sum(r["cost_usd"] for r in ok),
            sum(r["cost_usd"] for r in bad),
        )
    )
    print("sidecar cost_usd_tariff total: %.4f" % sum(m["cost_usd_tariff"] for _, m in metas))
    by_job = {m["job_id"]: m for _, m in metas}
    okj = set(r["job_id"] for r in ok)
    print("ok ledger rows with no sidecar:", len(okj - set(by_job)))
    print("sidecars with no ok ledger row:", len(set(by_job) - okj))
    dis = sum(
        1
        for r in ok
        if r["job_id"] in by_job
        and abs(by_job[r["job_id"]]["cost_usd_tariff"] - r["cost_usd"]) > 1e-9
    )
    print("cost disagreements sidecar vs ledger:", dis)
    dis = sum(
        1
        for r in ok
        if r["job_id"] in by_job and by_job[r["job_id"]]["prompt_sha256"] != r["prompt_sha256"]
    )
    print("prompt_sha256 disagreements sidecar vs ledger:", dis)
    print(
        "failed rows by block:", dict(collections.Counter(r["job_id"].split("|")[1] for r in bad))
    )
    print("failed rows cost values:", dict(collections.Counter(r["cost_usd"] for r in bad)))
    print("failed rows attempts:", dict(collections.Counter(r.get("attempts") for r in bad)))
    for e, c in collections.Counter(r["error"][:120] for r in bad).most_common():
        print("   x%-4d %s" % (c, e))


SECTIONS = {
    "0": section0,
    "1": section1,
    "2": section2,
    "3": section3,
    "4": section4,
    "5": section5,
    "6": section6,
    "7": section7,
    "8": section8,
    "9": section9,
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--section", action="append", choices=sorted(SECTIONS))
    args = ap.parse_args()
    if not os.path.isdir("art_generated"):
        sys.exit("run this from the repo root (art_generated/ not found)")
    metas = load_metas()
    for key in args.section or sorted(SECTIONS):
        SECTIONS[key](metas)
        print()


if __name__ == "__main__":
    main()
