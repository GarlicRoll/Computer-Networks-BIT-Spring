# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['server.py'],
    pathex=[],
    binaries=[],
    datas=[('webroot/404.html', 'webroot'), ('webroot/calculator_form.html', 'webroot'), ('webroot/data_query_form.html', 'webroot'), ('webroot/index.html', 'webroot'), ('webroot/cgi-bin/calculator.py', 'webroot/cgi-bin'), ('webroot/cgi-bin/data_query.py', 'webroot/cgi-bin')],
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
    name='server',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
