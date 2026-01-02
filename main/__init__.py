#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""虎哥PDF重命名工具

智能识别 PDF 标题，批量重命名文件。支持从 PDF 元数据或首页内容
自动提取标题，实现一键批量重命名。

Copyright (c) 2024-2026 虎哥
Licensed under the MIT License.

模块结构:
    - pdf_renamer: GUI 主界面
    - config: 配置管理
    - file_processor: 文件处理核心
    - smart_text_extractor: PDF 标题提取
    - utils: 通用工具
"""

from __future__ import annotations

# 版本信息
__version__ = "1.0.0"
__author__ = "虎哥"
__app_name__ = "虎哥PDF重命名"
__app_name_en__ = "Tiger PDF Renamer"
__license__ = "MIT"

# 导出模块
from .config import RenameConfig, ConfigManager, config_manager
from .file_processor import FileProcessor, RenameResult, ProcessStats
from .smart_text_extractor import SmartTextExtractor, ExtractedText
from .utils import setup_logging
from .pdf_renamer import MainApp, main

__all__ = [
    # 版本信息
    "__version__",
    "__author__",
    "__app_name__",
    "__app_name_en__",
    # 配置
    "RenameConfig",
    "ConfigManager",
    "config_manager",
    # 文件处理
    "FileProcessor",
    "RenameResult",
    "ProcessStats",
    # 文本提取
    "SmartTextExtractor",
    "ExtractedText",
    # 工具
    "setup_logging",
    # GUI
    "MainApp",
    "main",
]
