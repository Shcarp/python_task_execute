# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(
    ['main.py','globals.py','info_queue.py','register_time.py','run_task.py','server.py','task_queue.py','task.py','wechat.py','module/__init__.py','module/mysql.py','module/register.py','module/task.py','module/wechat.py','service/__init__.py', 'service/oprotocol.py','service/websocket.py'],
    pathex=[],
    binaries=[],
    datas=[('.env','.env')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='chat_message',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon="C:\\Users\\21915\\Desktop\\python_auto_wechat_message\\sourse\\auto.ico",
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='chat_message',
)
