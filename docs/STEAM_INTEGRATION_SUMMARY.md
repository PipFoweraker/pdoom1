# Steam Integration - Quick Start Guide

**Status**: Ready to implement - no technical blockers
**Cost**: $100 (one-time Steamworks fee)
**Timeline**: 1 week technical work + 1-2 weeks store page prep

---

## What's Stopping Us? Nothing.

The game is technically ready for Steam. We just need to:
1. Pay the $100 Steamworks fee
2. Install GodotSteam plugin (~2 days)
3. Map existing achievements to Steam (~1 day)
4. Create store page assets (~1-2 weeks)

---

## Implementation Phases

### Phase 1: Steamworks Account Setup (Day 1)
- [ ] Register at https://partner.steamgames.com
- [ ] Pay $100 Steam Direct fee
- [ ] Complete tax/banking forms
- [ ] Reserve app ID
- [ ] Download Steamworks SDK

**Cost**: $100
**Time**: 1-2 hours + approval wait

---

### Phase 2: GodotSteam Integration (Days 2-4)
- [ ] Download GodotSteam 4.11+ from https://github.com/GodotSteam/GodotSteam
- [ ] Install plugin to `godot/addons/godotsteam/`
- [ ] Create `steam_manager.gd` autoload
- [ ] Add `steam_appid.txt` to project root
- [ ] Update export presets for Steam builds

**Key Files to Create**:
```
godot/autoload/steam_manager.gd       # Steam initialization & API wrapper
godot/steam_appid.txt                 # Your Steam app ID
godot/export_presets.cfg              # Steam build configuration
```

**Time**: 2-3 days

---

### Phase 3: Achievement Integration (Days 5-6)
- [ ] Map existing achievements to Steam achievement IDs
- [ ] Update achievement_manager.gd to call Steam API
- [ ] Test achievement unlocking locally
- [ ] Upload achievement definitions to Steamworks

**Existing Achievements Ready**:
- 21 achievements already implemented in-game
- Just need Steam API calls added to `achievement_manager.gd`

**Time**: 1-2 days

---

### Phase 4: Store Page & Launch (Weeks 2-3)
- [ ] Create store page assets (capsule images, screenshots, trailer)
- [ ] Write store description
- [ ] Set pricing
- [ ] Configure release options
- [ ] Submit for review

**Required Assets**:
- Header capsule (460x215)
- Small capsule (231x87)
- Main capsule (616x353)
- Screenshots (1920x1080, at least 5)
- Optional: Trailer video

**Time**: 1-2 weeks (mostly asset creation)

---

## Code Changes Required

### Minimal Implementation (2 files)

**1. Create `godot/autoload/steam_manager.gd`**:
```gdscript
extends Node

var is_steam_enabled: bool = false
var steam_id: int = 0
var player_name: String = ""

func _ready():
    if OS.has_feature("steam"):
        var init_response = Steam.steamInit()
        is_steam_enabled = (init_response['status'] == 1)

        if is_steam_enabled:
            steam_id = Steam.getSteamID()
            player_name = Steam.getPersonaName()
            print("[Steam] Initialized - ID: %d, Name: %s" % [steam_id, player_name])

func unlock_achievement(achievement_id: String):
    if is_steam_enabled:
        Steam.setAchievement(achievement_id)
        Steam.storeStats()

func _process(_delta):
    if is_steam_enabled:
        Steam.run_callbacks()
```

**2. Update `godot/managers/achievement_manager.gd`**:
```gdscript
# Add Steam call to unlock_achievement()
func unlock_achievement(achievement_id: String) -> void:
    # ... existing code ...

    # Add Steam sync
    if get_node_or_null("/root/SteamManager"):
        SteamManager.unlock_achievement(achievement_id)
```

That's it. Two small files.

---

## Testing Plan

### Local Testing (Without Steam)
```bash
# Game runs normally without Steam
godot --headless --quit-after 5
```

### Steam Testing (With GodotSteam)
1. Run game through Steam client
2. Verify Steam overlay works (Shift+Tab)
3. Test achievement unlocking
4. Check Steam profile for unlocked achievements

---

## Revenue Sharing

Steam takes 30% of revenue:
- $10 game = $7 to developer, $3 to Steam
- $15 game = $10.50 to developer, $4.50 to Steam
- $20 game = $14 to developer, $6 to Steam

---

## Next Steps

**If proceeding now**:
1. Register Steamworks account today
2. While waiting for approval, prepare store assets
3. Once approved, install GodotSteam and begin Phase 2

**If waiting**:
- Steam integration can happen anytime
- Game continues to work standalone via itch.io/GitHub
- No deadline or urgency

---

## References

- Full roadmap: [STEAM_INTEGRATION_ROADMAP.md](STEAM_INTEGRATION_ROADMAP.md)
- Steamworks documentation: https://partner.steamgames.com/doc/home
- GodotSteam plugin: https://github.com/GodotSteam/GodotSteam
- GodotSteam docs: https://godotsteam.com/

---

**Bottom Line**: We can ship on Steam in ~2 weeks. The game is ready, we just need to connect the plumbing.
