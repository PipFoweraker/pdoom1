# v0.10.1 Release - Quick Reference

## 🚀 One-Command Release

```bash
bash release_v0.10.1.sh
```

This runs everything in order. Or run manually:

---

## 📋 Manual Release Steps

### 1. Test Everything (YOU DO THIS)
```bash
# In Godot: Press F5, test game
# Verify:
- Queue actions work
- C clears queue
- Remove buttons work
- Space commits turn
- No errors in console
```

### 2. Export from Godot (YOU DO THIS)
```
Project → Export → Windows Desktop → Export Project
Save to: builds/windows/v0.10.1/PDoom.exe
```

### 3. Commit All Changes
```bash
bash commit_ap_tracking_fix.sh
bash commit_gdscript_warnings.sh
bash commit_tier2_features.sh
git add CHANGELOG.md
git commit -m "docs: Update CHANGELOG for v0.10.1"
git push origin main
```

### 4. Package Release
```bash
bash package_release.sh
# Creates: PDoom-v0.10.1-Windows.zip (~110MB)
```

### 5. Test Package
```bash
# Extract zip to temp folder
# Run PDoom.exe
# Verify it works
```

### 6. Create GitHub Release
```bash
bash create_github_release.sh
# Or manually:
gh release create v0.10.1 \
  --title "v0.10.1 - UX Improvements & First Public Release" \
  --notes-file RELEASE_NOTES_v0.10.1.md \
  PDoom-v0.10.1-Windows.zip
```

### 7. Update README
```bash
# Edit README.md
# Change "Windows builds coming soon" to:
**Download:** [v0.10.1 for Windows](https://github.com/PipFoweraker/pdoom1/releases/tag/v0.10.1)

git add README.md
git commit -m "docs: Add v0.10.1 download link to README"
git push
```

### 8. Close Issues
```bash
gh issue close 435 -c "Fixed in v0.10.1 - Zero GDScript warnings"
gh issue close 431 -c "Fixed in v0.10.1 - Strategic simulation description"
gh issue close 389 -c "Resolved by design - Submenu actions intentionally cost 0 AP"
```

---

## 📦 Release Contents

```
PDoom-v0.10.1-Windows.zip
├── PDoom.exe           (91MB - main game)
├── PDoom.pck           (19MB - game data)
├── README.txt          (quick start guide)
└── CHANGELOG.txt       (what's new)
```

---

## ✅ Verification Checklist

Before release:
- [ ] Game exports without errors
- [ ] Package created successfully
- [ ] Test extraction and running
- [ ] All commits pushed
- [ ] CHANGELOG updated

After release:
- [ ] Download link works
- [ ] Release notes visible
- [ ] README updated
- [ ] Issues closed

---

## 🆘 Troubleshooting

**Package script fails:**
- Check builds/windows/v0.10.1/PDoom.exe exists
- Re-export from Godot

**GitHub release fails:**
- Check `gh auth status`
- Check package exists
- Check release notes file exists

**Game doesn't run:**
- Test on clean Windows 10/11 machine
- Check antivirus didn't quarantine
- Verify all files extracted

---

## 📊 Time Estimates

| Task | Time |
|------|------|
| Testing | 15min |
| Export | 5min |
| Commit & Push | 5min |
| Package | 5min |
| Test Package | 10min |
| GitHub Release | 5min |
| README Update | 5min |
| **Total** | **50min** |

---

## 🎯 Success Criteria

**Minimum:**
- Game downloads and runs
- Basic gameplay works
- No critical bugs

**Target:**
- All features working
- Professional presentation
- Zero known issues

---

## 🔗 Important Links

- **Release URL:** https://github.com/PipFoweraker/pdoom1/releases/tag/v0.10.1
- **Issues:** https://github.com/PipFoweraker/pdoom1/issues
- **Website:** https://pdoom1.com
- **Full Checklist:** RELEASE_v0.10.1_CHECKLIST.md
- **Release Notes:** RELEASE_NOTES_v0.10.1.md
