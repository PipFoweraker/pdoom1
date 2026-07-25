# Art masters policy (RULED 2026-07-22)

Git is 512px/WebP-CANONICAL: the committed assets are what the game ships.
Full-resolution masters (1024+ PNGs, over the 1MB hook cap) are a
convenience cache, NOT the source of truth -- the true source is the
committed YAML prompt manifests (art_prompts/*.yaml), from which any master
is regenerable for cents. Git LFS was considered and REJECTED (quota cost +
per-clone friction to version a cache; two lanes independently declined
raising the 1MB cap -- permanent history bloat).

Masters archive: **DreamObjects** (DreamHost's S3-compatible object storage;
RULED 2026-07-25). Chosen over MinIO-on-instance / external R2/B2 because it
consolidates billing on existing hosting, is S3-compatible (rclone/boto),
decoupled from the compute instance's lifecycle, and ~$1/mo at this scale
(2.5c/GB, upload free; DreamCompute also includes 100GB Ceph if a self-host
path is ever preferred). Keep the bucket NON-public (auth-only, not a web
path). Sync with `python tools/archive_masters.py --push` (rclone remote
'dreamobjects'; see that script's header for one-time setup).

Interim staging on the dev machine: G:/tmp/pdoom1-art-masters/ -- agents
producing oversized masters copy them there (or note their worktree location)
until synced. Durability note: DreamObjects is one provider/one copy; for a
true 3-2-1 posture add a second off-site copy (R2/B2) once masters warrant it.
Migration stays trivial by design: a plain folder of regenerable files.

Agent rule: never commit files over the hook cap, never use --no-verify for
size, never delete masters without them being staged in the archive first.
