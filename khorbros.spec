# PyInstaller spec for KhorBrosMenu (one-file, console).
# Build:  pyinstaller khorbros.spec

a = Analysis(
    ["generate_menu.py"],
    pathex=[],
    binaries=[],
    datas=[
        ("images/DE.RM.VCVO2025.jpg", "images"),
        ("twist_combinations.md", "."),
        ("fonts", "fonts"),
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="KhorBrosMenu",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
