# Steam Integration Roadmap - P(Doom)

**Status**: Ready to Implement
**Current Version**: v0.10.5
**Target**: Steam Early Access
**Estimated Timeline**: 2-3 weeks

---

## Executive Summary

**What's stopping us from Steam?**

Nothing critical! The game is **feature-complete** and **technically ready**. What's needed:

1. ✅ **Game**: Complete and polished
2. ✅ **Architecture**: Designed and documented
3. ⏳ **Steamworks Setup**: Developer account + App ID (~1 day)
4. ⏳ **GodotSteam Plugin**: Install & configure (~1 day)
5. ⏳ **Steam Manager**: Basic integration (~2-3 days)
6. ⏳ **Testing**: Steam build validation (~2-3 days)
7. ⏳ **Store Page**: Marketing materials (~1-2 weeks)

**Bottom line**: You could have a Steam build in **1 week** (technical), but should allocate **2-3 weeks** for store page polish.

---

## Current Status

### ✅ What You Already Have

| Component | Status | Notes |
|-----------|--------|-------|
| **Complete Game** | ✅ Ready | v0.10.5 is polished and stable |
| **Windows/Linux/macOS Builds** | ✅ Working | Automated build pipeline |
| **Architecture Docs** | ✅ Complete | Privacy-first Steam design |
| **Achievement System** | ✅ Implemented | Ready for Steam mapping |
| **Leaderboard System** | ✅ Local | Can be extended to Steam |
| **Export Presets** | ✅ Configured | For all platforms |

### ⏳ What's Missing

| Component | Status | Effort | Blocker? |
|-----------|--------|--------|----------|
| **Steamworks Dev Account** | ❌ Not started | 1 day | **YES** |
| **Steam App ID** | ❌ Not started | 1 day | **YES** |
| **GodotSteam Plugin** | ❌ Not installed | 1 day | **YES** |
| **Steam Manager Code** | ❌ Not written | 2-3 days | **YES** |
| **Achievement Integration** | ❌ Not mapped | 1-2 days | No |
| **Store Page** | ❌ Not created | 1-2 weeks | No |
| **Backend API** | 📋 Planned | 3-5 days | No (optional) |

---

## Implementation Plan

### **Phase 1: Steamworks Setup** (1-2 days)

**Goal**: Get developer access and App ID

#### Tasks:
1. **Register Steamworks Developer Account**
   - Go to https://partner.steamgames.com/
   - Pay $100 USD app fee (one-time, per game)
   - Complete tax/banking forms
   - Wait for approval (~1-2 days)

2. **Create App ID**
   - Create new app: "P(Doom): AI Safety Strategy Game"
   - Get App ID (e.g., 123456)
   - Document in `config/steam.json`:
     ```json
     {
       "app_id": "YOUR_APP_ID",
       "depot_ids": {
         "windows": "YOUR_DEPOT_ID_WIN",
         "linux": "YOUR_DEPOT_ID_LINUX",
         "mac": "YOUR_DEPOT_ID_MAC"
       }
     }
     ```

3. **Download Steamworks SDK**
   - Get from https://partner.steamgames.com/
   - Version: Latest (v1.59+)
   - Extract to `steamworks_sdk/`

**Deliverable**: Steamworks developer account + App ID + SDK

---

### **Phase 2: GodotSteam Integration** (2-3 days)

**Goal**: Install plugin and test basic Steam API calls

#### Tasks:

1. **Install GodotSteam GDExtension**
   ```bash
   # Download from: https://github.com/GodotSteam/GodotSteam
   # For Godot 4.5.1, use GodotSteam 4.10+

   # Extract to:
   # godot/addons/godotsteam/
   ```

2. **Create Steam Manager Autoload**

   Create `godot/autoload/steam_manager.gd`:
   ```gdscript
   extends Node

   signal steam_initialized(success: bool)
   signal player_info_loaded(steam_id: int, name: String)

   var is_steam_enabled: bool = false
   var steam_id: int = 0
   var player_name: String = ""
   var app_id: int = 0  # Set from config

   func _ready():
       # Load config
       var config = load_steam_config()
       app_id = config.get("app_id", 0)

       # Initialize Steam
       if OS.has_feature("steam"):
           _initialize_steam()
       else:
           print("[Steam] Not running on Steam - using fallback")
           is_steam_enabled = false
           steam_initialized.emit(false)

   func _initialize_steam():
       # Initialize Steamworks API
       var init_response = Steam.steamInit()

       if init_response['status'] != 1:
           print("[Steam] Failed to initialize: ", init_response)
           is_steam_enabled = false
           steam_initialized.emit(false)
           return

       print("[Steam] Initialized successfully")
       is_steam_enabled = true

       # Get player info
       steam_id = Steam.getSteamID()
       player_name = Steam.getPersonaName()

       print("[Steam] Player: ", player_name, " (", steam_id, ")")

       steam_initialized.emit(true)
       player_info_loaded.emit(steam_id, player_name)

   func _process(_delta):
       if is_steam_enabled:
           Steam.run_callbacks()

   func load_steam_config() -> Dictionary:
       var config_file = "res://config/steam.json"
       if FileAccess.file_exists(config_file):
           var file = FileAccess.open(config_file, FileAccess.READ)
           var json = JSON.parse_string(file.get_as_text())
           file.close()
           return json
       return {}

   func is_steam_build() -> bool:
       return is_steam_enabled

   func get_steam_id() -> int:
       return steam_id if is_steam_enabled else 0

   func get_player_name() -> String:
       return player_name if is_steam_enabled else "Player"
   ```

3. **Register Autoload**

   Add to `godot/project.godot`:
   ```ini
   [autoload]
   SteamManager="*res://autoload/steam_manager.gd"
   ```

4. **Update Export Preset**

   Edit `godot/export_presets.cfg`:
   ```ini
   [preset.0]
   name="Windows Desktop"
   platform="Windows Desktop"
   runnable=true
   advanced_options=true
   custom_features="steam"  # Add this
   export_filter="all_resources"
   include_filter=""
   exclude_filter=""
   export_path="../builds/windows/[version]/PDoom.exe"
   script_export_mode=2

   [preset.0.options]
   custom_template/debug=""
   custom_template/release=""
   debug/export_console_wrapper=1
   binary_format/embed_pck=false
   texture_format/bptc=true
   binary_format/architecture="x86_64"
   codesign/enable=false
   codesign/timestamp=true
   codesign/timestamp_server_url=""
   codesign/digest_algorithm=1
   codesign/description=""
   codesign/custom_options=PackedStringArray()
   application/modify_resources=true
   application/icon="res://icon.svg"
   application/console_wrapper_icon="res://icon.svg"
   application/icon_interpolation=4
   application/file_version=""
   application/product_version=""
   application/company_name="P(Doom)"
   application/product_name="P(Doom)"
   application/file_description=""
   application/copyright=""
   application/trademarks=""
   application/export_angle=0
   application/export_d3d12=0
   application/d3d12_agility_sdk_multiarch=true
   ssh_remote_deploy/enabled=false
   ssh_remote_deploy/host="user@host_ip"
   ssh_remote_deploy/port="22"
   ssh_remote_deploy/extra_args_ssh=""
   ssh_remote_deploy/extra_args_scp=""
   ssh_remote_deploy/run_script="Expand-Archive -LiteralPath '{temp_dir}\\{archive_name}' -DestinationPath '{temp_dir}'
   $action = New-ScheduledTaskAction -Execute '{temp_dir}\\{exe_name}' -Argument '{cmd_args}'
   $trigger = New-ScheduledTaskTrigger -Once -At 00:00
   $settings = New-ScheduledTaskSettingsSet
   $task = New-ScheduledTask -Action $action -Trigger $trigger -Settings $settings
   Register-ScheduledTask godot_remote_debug -InputObject $task -Force:$true
   Start-ScheduledTask -TaskName godot_remote_debug
   while (Get-ScheduledTask -TaskName godot_remote_debug | ? State -eq running) { Start-Sleep -Milliseconds 100 }
   Unregister-ScheduledTask -TaskName godot_remote_debug -Confirm:$false -ErrorAction:SilentlyContinue"
   ssh_remote_deploy/cleanup_script="Stop-ScheduledTask -TaskName godot_remote_debug -ErrorAction:SilentlyContinue
   Unregister-ScheduledTask -TaskName godot_remote_debug -Confirm:$false -ErrorAction:SilentlyContinue
   Remove-Item -Recurse -Force '{temp_dir}'"
   ```

5. **Test Steam Build Locally**
   ```bash
   # Build Steam version
   python scripts/build_all_platforms.py --version v0.10.5-steam

   # Copy steam_appid.txt to build directory
   echo "YOUR_APP_ID" > builds/windows/v0.10.5-steam/steam_appid.txt

   # Run with Steam client open
   cd builds/windows/v0.10.5-steam/
   ./PDoom.exe
   ```

**Deliverable**: Working Steam integration with player name/ID

---

### **Phase 3: Achievement Integration** (1-2 days)

**Goal**: Map P(Doom) achievements to Steam

#### Tasks:

1. **Define Steam Achievements in Steamworks**

   Go to Steamworks admin → Your App → Stats & Achievements

   Map existing achievements (from `legacy/shared/features/achievements_endgame.py`):

   | P(Doom) Achievement | Steam API Name | Description |
   |---------------------|----------------|-------------|
   | First Victory | `ACHIEVEMENT_FIRST_VICTORY` | Win your first game |
   | Survived 100 Turns | `ACHIEVEMENT_100_TURNS` | Survive 100 turns |
   | Zero Doom | `ACHIEVEMENT_ZERO_DOOM` | Reduce P(Doom) to 0% |
   | Elite Workforce | `ACHIEVEMENT_ELITE_WORKFORCE` | Hire 50+ researchers |
   | Breakthrough | `ACHIEVEMENT_BREAKTHROUGH` | Publish 20+ papers |
   | Financial Mastery | `ACHIEVEMENT_FINANCIAL_MASTERY` | Accumulate $10M+ |
   | Safety Champion | `ACHIEVEMENT_SAFETY_CHAMPION` | Win with 0% doom |
   | Media Darling | `ACHIEVEMENT_MEDIA_DARLING` | Reach 90%+ public opinion |
   | Underdog | `ACHIEVEMENT_UNDERDOG` | Win with <5 researchers |
   | Speedrunner | `ACHIEVEMENT_SPEEDRUNNER` | Win in <50 turns |

2. **Add Achievement Manager**

   Create `godot/autoload/achievement_manager.gd`:
   ```gdscript
   extends Node

   const ACHIEVEMENTS = {
       "first_victory": "ACHIEVEMENT_FIRST_VICTORY",
       "survived_100_turns": "ACHIEVEMENT_100_TURNS",
       "zero_doom": "ACHIEVEMENT_ZERO_DOOM",
       # ... etc
   }

   func unlock_achievement(achievement_id: String):
       if not ACHIEVEMENTS.has(achievement_id):
           print("[Achievements] Unknown achievement: ", achievement_id)
           return

       var steam_api_name = ACHIEVEMENTS[achievement_id]

       # Steam version
       if SteamManager.is_steam_build():
           Steam.setAchievement(steam_api_name)
           Steam.storeStats()
           print("[Achievements] Unlocked (Steam): ", steam_api_name)
       else:
           # Local version - save to file
           _save_local_achievement(achievement_id)
           print("[Achievements] Unlocked (Local): ", achievement_id)

   func _save_local_achievement(achievement_id: String):
       var save_path = "user://achievements.json"
       var achievements_data = {}

       if FileAccess.file_exists(save_path):
           var file = FileAccess.open(save_path, FileAccess.READ)
           achievements_data = JSON.parse_string(file.get_as_text())
           file.close()

       achievements_data[achievement_id] = {
           "unlocked": true,
           "timestamp": Time.get_unix_time_from_system()
       }

       var file = FileAccess.open(save_path, FileAccess.WRITE)
       file.store_string(JSON.stringify(achievements_data, "\t"))
       file.close()
   ```

3. **Trigger Achievements in Game**

   In `godot/scripts/game_controller.gd`:
   ```gdscript
   func handle_game_over():
       # Existing code...

       # Check achievements
       if game_won:
           AchievementManager.unlock_achievement("first_victory")

           if game_state["turn"] >= 100:
               AchievementManager.unlock_achievement("survived_100_turns")

           if game_state["doom"] <= 0:
               AchievementManager.unlock_achievement("zero_doom")

           # ... etc
   ```

**Deliverable**: Steam achievements working

---

### **Phase 4: Store Page & Marketing** (1-2 weeks)

**Goal**: Create compelling Steam store presence

#### Tasks:

1. **Store Page Assets**
   - ✅ Screenshots (you have these)
   - ⏳ Capsule image (460x215)
   - ⏳ Header image (460x215)
   - ⏳ Hero image (optional, 1920x622)
   - ⏳ Trailer video (30-90 seconds)

2. **Store Page Copy**
   ```markdown
   # Short Description (300 chars)
   Manage an underfunded AI safety lab racing to solve alignment before it's too late. Make strategic decisions about hiring, research, and resources. Your choices determine whether P(Doom) reaches 0% or humanity faces extinction.

   # About This Game
   You run an underfunded AI safety research lab racing against well-funded competitors to solve the alignment problem. Make strategic decisions about:

   - Hiring researchers from a candidate pool (Safety, Capabilities, Interpretability, Alignment)
   - Managing teams and balancing researcher traits (team_player, media_savvy, leak_prone)
   - Handling burnout, poaching events, and doom from reckless research
   - Responding to rival lab actions and random events
   - Surviving 100 turns with P(Doom) at 0%

   # Key Features
   - Turn-based strategy gameplay inspired by XCOM and FTL
   - Individual researcher management with unique traits
   - Dynamic event system with meaningful choices
   - Compete on seed-specific leaderboards
   - Historical AI safety timeline (2017-2025)
   - Retro-futuristic UI aesthetic

   # Early Access
   P(Doom) is in Early Access. Current features are complete and polished, with planned additions including:
   - Enhanced scoring system
   - More events and scenarios
   - Additional researcher specializations
   - Steam achievements and leaderboards
   ```

3. **Pricing Strategy**
   - Recommended: $9.99 USD (Early Access)
   - Post-1.0: $14.99 USD
   - Launch discount: 20% off ($7.99)

4. **Release Timeline**
   - **Week 1**: Technical implementation (Phases 1-3)
   - **Week 2**: Store page creation + assets
   - **Week 3**: Playtesting + polish
   - **Week 4**: Soft launch (invite-only)
   - **Week 5**: Public Early Access launch

**Deliverable**: Live Steam Early Access page

---

### **Phase 5: Optional Enhancements** (Future)

These can wait until after launch:

1. **Steam Leaderboards** (3-5 days)
   - Sync local leaderboards to Steam
   - Fetch Steam leaderboards for display
   - Requires backend API (Phase 2 from architecture docs)

2. **Steam Cloud Saves** (1-2 days)
   - Sync `user://` directory to Steam Cloud
   - Cross-platform save compatibility

3. **Steam Trading Cards** (1 week)
   - Design card artwork
   - Create badge designs
   - Set up in Steamworks

4. **Steam Workshop** (2-3 weeks)
   - Mod support infrastructure
   - Custom scenario sharing
   - Texture/UI mods

---

## Technical Requirements

### Minimum Steamworks Requirements

- ✅ **Godot 4.5.1** (you have this)
- ⏳ **GodotSteam 4.10+** (need to install)
- ⏳ **Steamworks SDK v1.59+** (need to download)
- ✅ **Windows/Linux/macOS builds** (you have these)
- ⏳ **Steam App ID** (need to register)

### Build Pipeline Changes

Current:
```bash
python scripts/build_all_platforms.py --version v0.10.5
# Creates: PDoom.exe + PDoom.pck
```

With Steam:
```bash
python scripts/build_all_platforms.py --version v0.10.5 --steam
# Creates: PDoom.exe + PDoom.pck + steam_appid.txt + steam_api64.dll
```

Add to `scripts/build_all_platforms.py`:
```python
def build_steam_version(self, version: str):
    """Build Steam-specific version"""
    # Copy Steamworks DLLs
    steam_dlls = [
        'steam_api64.dll',  # Windows
        'libsteam_api.so',  # Linux
        'libsteam_api.dylib'  # macOS
    ]

    for platform in ['windows', 'linux', 'mac']:
        build_dir = self.repo_root / 'builds' / platform / version
        # Copy appropriate DLL from steamworks_sdk/
        # Create steam_appid.txt with App ID
```

---

## Cost Breakdown

| Item | Cost | Notes |
|------|------|-------|
| **Steamworks Developer Fee** | $100 USD | One-time, per game |
| **GodotSteam Plugin** | Free | Open source |
| **Steamworks SDK** | Free | From Valve |
| **Total** | **$100** | |

No recurring fees until you make $1M+ revenue (then Valve takes 30% cut).

---

## Risk Assessment

### Low Risk
- ✅ Game is stable and complete
- ✅ Builds work on all platforms
- ✅ Architecture designed for Steam

### Medium Risk
- ⏳ Store page creation (marketing)
- ⏳ GodotSteam plugin learning curve
- ⏳ Testing Steam features

### High Risk
- ❌ **None identified**

---

## Decision Points

### Option A: Minimal Steam Launch (1 week)
- ✅ Just get it on Steam
- Basic Steam integration (name, ID)
- No achievements
- No leaderboards
- Launch ASAP

**Best for**: Testing the waters, getting feedback fast

### Option B: Full Steam Launch (2-3 weeks)
- ✅ Complete Steam integration
- All achievements working
- Leaderboards (optional)
- Polished store page
- Launch with confidence

**Best for**: Professional launch, maximize impact

### Option C: Early Access Soft Launch (4 weeks)
- ✅ Full integration
- Beta testing period
- Community feedback
- Polish based on testing
- Public launch after refinement

**Best for**: Building community, iterating based on feedback

---

## Recommendation

**Go with Option B: Full Steam Launch (2-3 weeks)**

Why:
1. Game is already polished - no major bugs
2. Achievements are ready to map
3. Store page effort is worth it for visibility
4. You'll only get one first impression
5. Extra 1-2 weeks is worth the quality

**Timeline**:
- **Week 1**: Steamworks setup + GodotSteam integration
- **Week 2**: Achievements + store page assets
- **Week 3**: Testing + marketing prep
- **Launch**: Week 4

---

## Next Actions (This Week)

### Day 1: Steamworks Setup
1. Register Steamworks developer account
2. Pay $100 app fee
3. Create app + get App ID
4. Download Steamworks SDK

### Day 2-3: GodotSteam Installation
1. Download GodotSteam 4.10+
2. Install to `godot/addons/`
3. Create SteamManager autoload
4. Test basic Steam API calls

### Day 4-5: Testing & Debugging
1. Build Steam version
2. Test Steam initialization
3. Verify player name/ID display
4. Fix any integration issues

### Weekend: Store Page Planning
1. Draft store page copy
2. Design capsule/header images
3. Plan trailer video
4. Gather screenshots

---

## Success Criteria

✅ Steam build launches with Steam client
✅ Player name displays from Steam account
✅ Steam overlay works (Shift+Tab)
✅ Achievements unlock properly
✅ Store page looks professional
✅ No game-breaking bugs

---

## Resources

- **GodotSteam**: https://github.com/GodotSteam/GodotSteam
- **Steamworks Docs**: https://partner.steamgames.com/doc/home
- **Steam Store Guidelines**: https://partner.steamgames.com/doc/store/assets
- **Your Architecture Docs**: `docs/LEADERBOARD_BACKEND_ARCHITECTURE.md`

---

**Status**: Ready to Begin
**Priority**: High
**Blockers**: None (just need to start!)

**Estimated Launch**: 2-3 weeks from today
