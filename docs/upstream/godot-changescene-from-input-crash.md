# Upstream candidate (Godot): change_scene_to_file() from _input() -> release-only segfault

> Draft for filing at https://github.com/godotengine/godot/issues after we build a
> clean minimal reproduction project. Captured from the P(Doom)1 v0.11.0 hunt
> (docs/LEADERBOARD_CRASH_DIAGNOSIS.md).

## Summary

Calling `SceneTree.change_scene_to_file()` (or `change_scene_to_packed()`) **from inside an
`_input()` handler** causes a hard, deterministic segfault (`EXCEPTION_ACCESS_VIOLATION`,
`0xc0000005`) while the target scene is loading, **before its `_ready` runs** -- but ONLY in
**release** exports. Debug builds and the editor do not crash. No engine crash backtrace is
printed (the access violation outruns the crash handler / logger).

## Environment

- Godot 4.5.1-stable, Windows 10 (x86_64), Forward+ (Vulkan) AND Compatibility (OpenGL3) --
  crash is renderer-independent.
- Reproduces in `--export-release` builds. Does NOT reproduce in `--export-debug` or in the
  editor.

## Windows Error Reporting signature (consistent across independent builds)

```
Faulting module name: <game>.exe   (the engine template binary)
Exception code:       0xc0000005   (access violation)
Fault offset:         <constant across builds>   (deterministic native deref inside the engine)
```

## Steps to reproduce (to be packaged as a minimal project)

1. Scene A (any Control) with an `_input()` that, on `KEY_ENTER`, calls
   `get_tree().change_scene_to_file("res://scene_b.tscn")` directly (inline, not deferred).
2. Scene B: any trivial Control scene (a `ColorRect` + `Label` + `Button` is enough -- the
   crash is content-independent).
3. Export RELEASE for Windows. Run, press ENTER in Scene A.
4. Result: access violation before Scene B's `_ready`. Last `--verbose` line is
   `Loading resource: res://scene_b.tscn` (+ its `.gdc`), then the process dies.

Control: triggering the SAME `change_scene_to_file(scene_b)` from a Button `pressed` signal
(mouse) instead of `_input()` does NOT crash. Deferring the call
(`call_deferred("change_scene_...")`) does NOT crash. So the trigger is specifically the
synchronous scene load/instantiate executed **within input dispatch**.

## Expected

Either the engine safely defers structural scene changes requested during input
propagation, or the API documents that `change_scene_to_*` must not be called from
`_input`/`_gui_input` and (ideally) pushes an error instead of dereferencing freed/invalid
state.

## Notes for the minimal repro

- Confirmed content-independent: a bare stub Scene B crashes identically.
- Confirmed release-only: the debug template masks it (different heap/timing).
- Our workaround: `call_deferred` the navigation out of the input callstack. Solid, but the
  engine crashing (vs erroring) on a plausible-looking API call from `_input` is the bug.

## TODO before filing

- [ ] Build the standalone minimal-repro project (no P(Doom) deps) and confirm it crashes.
- [ ] Symbolize the faulting offset against the official 4.5.1 release template if symbols
      are obtainable, to name the exact engine frame (we could not, locally).
- [ ] Check the Godot issue tracker for existing reports of change_scene-from-input crashes.
