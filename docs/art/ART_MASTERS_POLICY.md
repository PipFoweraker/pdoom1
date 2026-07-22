# Art masters policy (RULED 2026-07-22)

Git is 512px/WebP-CANONICAL: the committed assets are what the game ships.
Full-resolution masters (1024+ PNGs, over the 1MB hook cap) are a
convenience cache, NOT the source of truth -- the true source is the
committed YAML prompt manifests (art_prompts/*.yaml), from which any master
is regenerable for cents. Git LFS was considered and REJECTED (quota cost +
per-clone friction to version a cache; two lanes independently declined
raising the 1MB cap -- permanent history bloat).

Masters archive: Pip's own hosting (pdoom infrastructure, a few GB, cheap;
NOT a public web path -- keep outside the docroot or auth-protected).
Interim staging on the dev machine: G:/tmp/pdoom1-art-masters/ -- agents
producing oversized masters copy them there (or note their worktree
location) until Pip syncs the folder to hosting. Migration later is trivial
by design: it is a plain folder of regenerable files.

Agent rule: never commit files over the hook cap, never use --no-verify for
size, never delete masters without them being staged in the archive first.
