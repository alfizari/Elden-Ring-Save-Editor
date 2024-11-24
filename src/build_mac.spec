# -*- mode: python ; coding: utf-8 -*-
import os
from glob import glob

a = Analysis(
    ['Final.py'],
    pathex=[os.getcwd()],
    binaries=[],
    datas=[
        (os.path.join(os.getcwd(), 'src', 'Resources'), 'Resources'),
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

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='Dark_Souls_3_Save_Editor',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    windowed=True,
)
