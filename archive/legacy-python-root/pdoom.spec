# -*- mode: python ; coding: utf-8 -*-

# P(Doom) PyInstaller Configuration
# Single-file Windows executable for alpha/beta testing

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('assets', 'assets'),  # Include all assets directory
        ('configs/default.template.json', 'configs'),  # Include template config
        ('src', 'src'),  # Include source for dynamic imports
        ('ui.py', '.'),  # Include root-level ui.py
        ('ui_new', 'ui_new'),  # Include ui_new directory
    ],
    hiddenimports=[
        'pygame',
        'numpy',
        'jsonschema',
        'ui',  # Root-level ui module
        'ui_new.facade',
        'src.core.game_state',
        'src.services.config_manager',
        'src.services.sound_manager',
        'src.services.version',
        'src.features.onboarding',
        'src.ui.overlay_manager',
        'src.services.bug_reporter',
        'src.services.lab_name_manager',
        'src.services.resource_manager',
        'src.ui.keybinding_menu',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter',  # Reduce size by excluding unused GUI toolkit
        'matplotlib',  # Not used in P(Doom)
        'PIL',  # Not used currently
    ],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='PDoom-v0.5.0-alpha',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,  # Compress for smaller file size
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # No console window for GUI app
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # TODO: Add game icon if available
)
