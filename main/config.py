#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""配置管理模块

使用 dataclass 定义配置结构，JSON 文件持久化。提供配置的加载、
保存和更新功能。

Copyright (c) 2024-2026 虎哥
Licensed under the MIT License.

Version: 1.0.0
"""

from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Set

# 配置文件名
CONFIG_FILENAME = "config.json"


# 支持的语言列表
SUPPORTED_LANGUAGES = ["zh_CN", "en_US"]
DEFAULT_LANGUAGE = "zh_CN"


@dataclass
class RenameConfig:
    """重命名配置数据类。

    存储 PDF 重命名相关的所有配置选项，支持序列化到 JSON 文件。

    Attributes:
        max_filename_length: 最大文件名长度，范围 10-255，默认 120
        add_timestamp: 是否添加时间戳后缀，默认 False
        auto_backup: 是否自动备份原文件，默认 False
        parallel_processing: 是否启用并行处理，默认 True
        max_workers: 最大并行工作线程数，范围 1-16，默认 4
        language: 界面语言，默认 zh_CN（简体中文）
    """

    max_filename_length: int = 120
    add_timestamp: bool = False
    auto_backup: bool = False
    parallel_processing: bool = True
    max_workers: int = 4
    language: str = DEFAULT_LANGUAGE

    def __post_init__(self) -> None:
        """验证并修正配置值。

        确保所有配置值在有效范围内，超出范围的值会被自动修正。
        """
        if self.max_filename_length < 10:
            self.max_filename_length = 10
        if self.max_filename_length > 255:
            self.max_filename_length = 255
        if self.max_workers < 1:
            self.max_workers = 1
        if self.max_workers > 16:
            self.max_workers = 16
        # 验证语言设置
        if self.language not in SUPPORTED_LANGUAGES:
            self.language = DEFAULT_LANGUAGE


class ConfigManager:
    """配置管理器。

    单例模式，负责配置的加载、保存和更新。配置文件存储在项目根目录。

    Attributes:
        config_file: 配置文件路径
        config: 当前配置实例

    Example:
        >>> manager = ConfigManager()
        >>> manager.update_config(max_filename_length=100)
        True
    """

    def __init__(self) -> None:
        """初始化配置管理器，加载配置文件。"""
        base_dir = Path(__file__).resolve().parent.parent
        self.config_file = base_dir / CONFIG_FILENAME
        self.config = self._load_config()

    def _load_config(self) -> RenameConfig:
        """从文件加载配置。

        如果配置文件不存在或格式错误，返回默认配置。

        Returns:
            RenameConfig: 加载的配置实例
        """
        if not self.config_file.exists():
            return RenameConfig()

        try:
            with open(self.config_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            # 只使用已知字段，忽略未知字段
            known_fields: Set[str] = {
                f.name for f in RenameConfig.__dataclass_fields__.values()
            }
            filtered_data = {k: v for k, v in data.items() if k in known_fields}
            return RenameConfig(**filtered_data)
        except (json.JSONDecodeError, TypeError, ValueError):
            return RenameConfig()

    def save_config(self) -> bool:
        """保存配置到文件。

        Returns:
            bool: 保存是否成功
        """
        try:
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(asdict(self.config), f, ensure_ascii=False, indent=2)
            return True
        except OSError:
            return False

    def update_config(self, **kwargs: Any) -> bool:
        """更新配置并保存。

        Args:
            **kwargs: 要更新的配置项，键名必须是 RenameConfig 的属性名

        Returns:
            bool: 保存是否成功

        Example:
            >>> manager.update_config(max_filename_length=100, auto_backup=True)
            True
        """
        for key, value in kwargs.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)
        # 重新验证
        self.config.__post_init__()
        return self.save_config()


# 全局配置管理器实例
config_manager = ConfigManager()
