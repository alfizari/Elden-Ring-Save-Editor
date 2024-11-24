# -*- mode: python ; coding: utf-8 -*-
import os
from glob import glob

a = Analysis(
    ['Final.py'],
    pathex=[os.getcwd()],
    binaries=[],
    datas=[
        (os.path.join(os.getcwd(), 'Resources'), 'Resources'),
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

exe_windows = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='Dark_Souls_3_Save_Editor',
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
    onefile=True,
    windowed=True
)
