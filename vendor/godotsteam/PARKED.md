# vendor/godotsteam -- parked Steam integration

Moved out of `godot/` on 2026-10-26 (issue #1071). Anything under `godot/` is
loaded by the engine and packed into every export; nothing here is.

What is here:

- The GodotSteam GDExtension exactly as it sat at `godot/addons/godotsteam/`
  (`godotsteam.gdextension` plus win32/win64/linux32/linux64/osx binaries).
- `steam_manager.gd`, formerly `godot/autoload/steam_manager.gd`. It was never
  registered as an autoload and nothing referenced it.
- `steam_appid.txt`, formerly `godot/steam_appid.txt`. It holds 480, Valve's
  Spacewar TEST app id, not a P(Doom)1 id.

Why it left: no game code called Steam, and the macOS framework broke every
Mac export (`LipO: Can't open file`, `CodeSign: Invalid binary format`). The
frameworks were committed from a Windows checkout, where git cannot store
symlinks, so `Versions/Current` is a plain directory and the binary is not at
the path the generated `Info.plist` names.

To bring Steam back:

1. Get a real Steam app id.
2. Replace the `osx/*.framework` directories with a fresh GodotSteam release
   that has the same Godot compatibility, and confirm the binary sits where
   the framework's `Info.plist` `CFBundleExecutable` says it does -- from a
   Mac or Linux checkout, never Windows.
3. Move this directory back to `godot/addons/godotsteam/` (and the two files
   to their old homes), register the autoload, and restore the expected
   library lists in `scripts/build_all_platforms.py`.
4. Prove a macOS export launches on a real Mac before shipping it.
