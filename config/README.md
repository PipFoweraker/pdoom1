# Configuration Files

This directory contains configuration files for the content distribution system.

**DO NOT commit actual credentials to git!** Files in this directory are `.gitignored` except this README.

---

## Reddit Configuration

### Setup Instructions

1. **Create Reddit App**:
   - Go to https://www.reddit.com/prefs/apps
   - Click "create app" or "create another app"
   - Fill in:
     - **name**: PDoom Publisher
     - **app type**: script
     - **description**: Automated content publishing for P(Doom)
     - **about url**: https://github.com/PipFoweraker/pdoom1
     - **redirect uri**: http://localhost:8080 (not used, but required)
   - Click "create app"

2. **Get Credentials**:
   - After creating, you'll see:
     - **client_id**: string under the app name (looks like: `abc123xyz`)
     - **client_secret**: labeled "secret" (longer string)

3. **Create `reddit.json`**:

```json
{
  "client_id": "YOUR_CLIENT_ID_HERE",
  "client_secret": "YOUR_CLIENT_SECRET_HERE",
  "user_agent": "PDoom Publisher v1.0 by /u/YOUR_REDDIT_USERNAME",
  "username": "YOUR_REDDIT_USERNAME",
  "password": "YOUR_REDDIT_PASSWORD"
}
```

4. **Install PRAW**:
```bash
pip install praw
```

5. **Test Connection**:
```bash
python scripts/content_publisher.py test
```

You should see:
```
Checking Python packages:
  praw: [Installed]

Checking configuration:
  reddit.json: [Found]
```

---

## Forum Configuration (Future)

Create `forum.json` for LessWrong/EA Forum posting:

```json
{
  "api_key": "YOUR_API_KEY",
  "base_url": "https://www.lesswrong.com/graphql",
  "author_id": "YOUR_USER_ID"
}
```

---

## Discord Webhooks (Future)

Create `discord.json` for Discord announcements:

```json
{
  "webhooks": {
    "announcements": "https://discord.com/api/webhooks/...",
    "dev_updates": "https://discord.com/api/webhooks/..."
  }
}
```

---

## Security Notes

- **NEVER** commit credentials to git
- Use environment variables in CI/CD:
  - `REDDIT_CLIENT_ID`
  - `REDDIT_CLIENT_SECRET`
  - `REDDIT_PASSWORD`
- Keep `config/` in `.gitignore`
- Rotate credentials if exposed
- Use separate "bot" Reddit account for posting

---

## Troubleshooting

### "invalid_grant" error from Reddit
- Verify username/password are correct
- Check 2FA is disabled on bot account (or use auth tokens)
- Ensure client_id and client_secret match the app

### "403 Forbidden" error
- Verify user_agent string is descriptive
- Check Reddit account has enough karma
- Ensure account age > 30 days (Reddit API restriction)

### Rate limiting
- Reddit: 60 requests per minute
- Content publisher respects rate limits automatically
