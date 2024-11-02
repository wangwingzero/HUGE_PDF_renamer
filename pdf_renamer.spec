# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['pdf_renamer.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=['pdfplumber.utils', 'keyboard', 'pdfminer', 'pdfminer.pdftypes', 'pdfminer.pdfparser'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

b = Analysis(
    ['right_click.py'],
    pathex=[],
    binaries=[],
    datas=[],
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

# 添加安装程序
c = Analysis(
    ['install.py'],  # 我们将创建这个文件
    pathex=[],
    binaries=[],
    datas=[],
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

# 添加卸载程序
d = Analysis(
    ['uninstall.py'],  # 我们将创建这个文件
    pathex=[],
    binaries=[],
    datas=[],
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

MERGE((a, 'pdf_renamer', 'pdf_renamer'), (b, 'right_click', 'right_click'),
      (c, 'install', 'install'), (d, 'uninstall', 'uninstall'))

pyz_a = PYZ(a.pure, a.zipped_data, cipher=block_cipher)
pyz_b = PYZ(b.pure, b.zipped_data, cipher=block_cipher)
pyz_c = PYZ(c.pure, c.zipped_data, cipher=block_cipher)
pyz_d = PYZ(d.pure, d.zipped_data, cipher=block_cipher)

exe_a = EXE(
    pyz_a,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='虎哥PDF重命名工具',
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
    icon='pdf_renamer.ico',
)

exe_b = EXE(
    pyz_b,
    b.scripts,
    b.binaries,
    b.zipfiles,
    b.datas,
    [],
    name='虎哥PDF重命名工具_右键菜单管理',
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
    icon='pdf_renamer.ico',
)

# 安装程序
exe_c = EXE(
    pyz_c,
    c.scripts,
    c.binaries,
    c.zipfiles,
    c.datas,
    [],
    name='安装右键菜单',
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
    icon='pdf_renamer.ico',
)

# 卸载程序
exe_d = EXE(
    pyz_d,
    d.scripts,
    d.binaries,
    d.zipfiles,
    d.datas,
    [],
    name='卸载右键菜单',
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
    icon='pdf_renamer.ico',
) 