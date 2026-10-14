# -*- mode: python ; coding: utf-8 -*-

from pathlib import Path

project_root = Path(SPECPATH)
asset_directory = project_root / "assets"
bundled_assets = [
    (str(path), path.parent.relative_to(project_root).as_posix())
    for path in asset_directory.rglob("*")
    if path.is_file()
]

a = Analysis(
    [str(project_root / "main.py")],
    pathex=[str(project_root)],
    binaries=[],
    datas=bundled_assets,
    hiddenimports=[
        "pygame",
        "pygame.base",
        "pygame.constants",
        "PySide6.QtSvg",
        "PySide6.QtCore",
        "PySide6.QtGui",
        "PySide6.QtWidgets",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["tkinter"],
    noarchive=False,
    optimize=1,
)
pyz = PYZ(a.pure)
# Keep binaries and data inside this EXE; do not add a COLLECT step that creates
# a folder-based distribution.
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="SnakeForest",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(asset_directory / "images" / "app_icon.ico"),
)
