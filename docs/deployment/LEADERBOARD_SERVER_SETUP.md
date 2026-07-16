# Leaderboard server setup on DreamHost -- step-by-step

> For the P(Doom)1 score endpoint (`server/leaderboard/score_api.php`). Two paths. Read the
> "which path" note first -- for JUST scores you may not need to spin up a server at all.
> DreamCompute KB steps confirmed against DreamHost's current (2026) OpenStack cloud offering.

## Which path?
- **Path A -- existing shared hosting (fastest, ~15 min).** The endpoint is plain PHP, and your
  DreamHost shared hosting already serves PHP (it's where CVTas + pipfoweraker.com live). Just add a
  subdomain and upload one file. No server to spin up. **Best if all you want right now is scores.**
- **Path B -- a DreamCompute cloud VM (a real server, ~45-60 min).** A Linux instance you fully
  control, good if you want a permanent home for pdoom backend services (dashboard, pdoom-data,
  webclient all "keen for game data"). This is the "spin up a server" you asked about.

Recommendation: **Path A today** to get scores flowing before the build cadence, then **Path B**
later as the proper pdoom services box if/when you want it. Both use the same `score_api.php`.

---

## Path A -- shared hosting (PHP, no VM)
1. **DreamHost panel -> Websites -> Manage Domains -> Add Hosting to a Domain / Sub-Domain.**
   Add e.g. `api.pdoom1.com`, hosting type "Web Hosting", pointing at a new dir like
   `/home/USERNAME/api.pdoom1.com`. (PHP is enabled by default; PHP 8.x is fine.)
2. **Upload** `server/leaderboard/score_api.php` into that dir (SFTP or panel file manager).
3. **Data dir OUTSIDE web root** so raw boards aren't fetchable: `mkdir ~/pdoom1-scoredata` and set
   `PDOOM_SCORE_DIR` to it. Easiest: edit the two `getenv(...) ?: 'default'` lines at the top of
   the PHP, or add to the dir's `.htaccess`:
   ```apache
   SetEnv PDOOM_SCORE_TOKEN "a-long-random-string"
   SetEnv PDOOM_SCORE_DIR "/home/USERNAME/pdoom1-scoredata"
   ```
4. **Enable HTTPS**: panel -> Websites -> Secure Certificates -> add free Let's Encrypt for the subdomain.
5. **Test**:
   ```
   curl "https://api.pdoom1.com/score_api.php?seed=default&version=v0.11.0"
   ```
6. Hand Claude the URL + token -> the Godot client gets wired. Done.

(Your website repos read the board JSON directly from `~/pdoom1-scoredata/board_*.json`, or via a
tiny read-only PHP include.)

---

## Path B -- DreamCompute cloud VM (OpenStack)
DreamCompute is DreamHost's OpenStack IaaS. You launch a Linux instance from the dashboard.

### 1. Key pair (so you can SSH in)
- Dashboard -> **Compute -> Key Pairs -> Import Public Key** (paste `~/.ssh/id_ed25519.pub`) or
  **Create Key Pair** (download the private key). Note the key name.

### 2. Open the firewall (security group)
- **Network -> Security Groups -> Manage Rules** on `default` -> **Add Rule** for each:
  SSH (TCP 22), HTTP (TCP 80), HTTPS (TCP 443). CIDR `0.0.0.0/0` for public.

### 3. Launch the instance
- **Compute -> Instances -> Launch Instance**:
  - **Details:** name `pdoom1-api`.
  - **Source:** boot from Image, pick **Ubuntu 24.04 LTS** (or 22.04); volume ~20 GB.
  - **Flavor:** the smallest (e.g. `gp1.subsonic` / lightspeed tier) -- plenty for scores.
  - **Networks:** the default private network (`public` egress is handled by a floating IP).
  - **Security Groups:** attach the one from step 2.
  - **Key Pair:** select your key.
  - **Launch Instance.**

### 4. Public IP
- **Compute -> Instances -> (your instance) dropdown -> Associate Floating IP** (allocate one if
  prompted). That public IP is how the world reaches it.

### 5. SSH in + install a web server
- Default user on Ubuntu DreamCompute images is usually `ubuntu` (some images use `dhc-user` --
  the dashboard shows it):
  ```
  ssh -i ~/.ssh/id_ed25519 ubuntu@<FLOATING_IP>
  sudo apt update && sudo apt install -y nginx php-fpm certbot python3-certbot-nginx
  ```
- Drop `score_api.php` in `/var/www/html/`, set the env in the nginx site or an env file, and add a
  PHP location block to the nginx server (standard `fastcgi_pass unix:/run/php/php-fpm.sock;`).

### 6. DNS + HTTPS
- DreamHost panel -> Manage Domains -> DNS: add an **A record** `api.pdoom1.com -> <FLOATING_IP>`.
- On the box: `sudo certbot --nginx -d api.pdoom1.com` (free cert, auto-renew).

### 7. Test -> hand Claude the URL + token.

### Prefer Python (to match CVTas)?
If you'd rather keep everything Django/Passenger like CVTas, say so and I'll ship a Flask/Django
version of the endpoint instead of PHP -- same API, same store, deployed the CVTas way
(passenger_wsgi.py + .htaccess). PHP is just the zero-dependency default.

---

## Common gotchas (from the CVTas deploy notes)
- DNS propagation is ~10-20 min -- don't panic on first load.
- Make the data dir writable by the web user; keep it out of the web root.
- Save the token in a password manager; the game sends it as `X-PDoom-Token`.

## Sources
- DreamCompute: launch-an-instance dashboard flow + FAQs (DreamHost KB).
- Your own `CVTas/docs/archive/QUICK_START_DEPLOYMENT.md` + `deploy-dreamhost.yml` (the shared-hosting Passenger pattern).
