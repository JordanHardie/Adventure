# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['C:\\Users\\xcool\\Desktop\\Python Projects\\Adventure!\\src\\main.py'],
    pathex=[],
    binaries=[],
    datas=[('C:\\Users\\xcool\\Desktop\\Python Projects\\Adventure!\\src\\config\\biomes.json', 'src/config'), ('C:\\Users\\xcool\\Desktop\\Python Projects\\Adventure!\\src\\config\\descriptions.json', 'src/config'), ('C:\\Users\\xcool\\Desktop\\Python Projects\\Adventure!\\src\\config\\font_support.json', 'src/config'), ('C:\\Users\\xcool\\Desktop\\Python Projects\\Adventure!\\src\\config\\items.json', 'src/config'), ('C:\\Users\\xcool\\Desktop\\Python Projects\\Adventure!\\src\\config\\monsters.json', 'src/config'), ('C:\\Users\\xcool\\Desktop\\Python Projects\\Adventure!\\src\\config\\prefixes.json', 'src/config')],
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
    a.datas,
    [],
    name='Adventure',
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
)
