# -*- mode: python ; coding: utf-8 -*-
"""
虎哥PDF重命名工具 - PyInstaller 打包配置
生成单文件便携版 exe，无需安装 Python，开箱即用
"""

import sys
from pathlib import Path

block_cipher = None

# 项目根目录
ROOT = Path(SPECPATH)

a = Analysis(
    ['run_huge_pdf_renamer.py'],
    pathex=[str(ROOT)],
    binaries=[],
    datas=[
        # 资源文件
        ('resources/huge_icon.ico', 'resources'),
        ('resources/huge_icon.png', 'resources'),
        # 配置文件（如果存在）
        ('config.json', '.') if Path('config.json').exists() else (None, None),
    ],
    hiddenimports=[
        # customtkinter 相关
        'customtkinter',
        'darkdetect',
        'PIL',
        'PIL._tkinter_finder',
        # PDF 处理
        'pypdf',
        'pdfplumber',
        'pdfminer',
        'pdfminer.six',
        'pdfminer.pdfparser',
        'pdfminer.pdfdocument',
        'pdfminer.pdfpage',
        'pdfminer.pdfinterp',
        'pdfminer.converter',
        'pdfminer.layout',
        # 其他依赖
        'keyboard',
        'tqdm',
        'sv_ttk',
        # 项目模块
        'main',
        'main.pdf_renamer',
        'main.config',
        'main.file_processor',
        'main.smart_text_extractor',
        'main.utils',
        'main.i18n',
        'main.i18n.zh_CN',
        'main.i18n.en_US',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # 排除不需要的模块以减小体积
        'pytest',
        'hypothesis',
        'unittest',
        'test',
        'tests',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# 过滤掉 None 的 datas
a.datas = [(d, s, t) for d, s, t in a.datas if d is not None]

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='HugePDFRenamer',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,  # 使用 UPX 压缩减小体积
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # 无控制台窗口
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='resources/huge_icon.ico',  # 应用图标
    version_info=None,
)
