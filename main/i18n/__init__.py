#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""国际化模块

提供多语言支持，包括语言切换、翻译查找和字符串格式化功能。

Copyright (c) 2024-2026 虎哥
Licensed under the MIT License.

Version: 1.0.0
"""

from __future__ import annotations

from typing import Dict, List, Optional, Tuple

# 可用语言列表：(语言代码, 显示名称)
AVAILABLE_LANGUAGES: List[Tuple[str, str]] = [
    ("zh_CN", "中文"),
    ("en_US", "English"),
]

# 默认语言
DEFAULT_LANGUAGE = "zh_CN"


class I18nManager:
    """国际化管理器。

    单例模式，负责管理语言资源和提供翻译功能。

    Attributes:
        current_language: 当前语言代码 (zh_CN, en_US)
        translations: 当前语言的翻译字典

    Example:
        >>> i18n = I18nManager()
        >>> i18n.get("app.name")
        '虎哥PDF重命名'
        >>> i18n.get("panel.files.count", count=5)
        '5 个文件'
    """

    _instance: Optional["I18nManager"] = None
    _initialized: bool = False

    def __new__(cls) -> "I18nManager":
        """单例模式实现。"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        """初始化，只执行一次。"""
        if I18nManager._initialized:
            return
        I18nManager._initialized = True
        self.current_language = DEFAULT_LANGUAGE
        self.translations: Dict[str, str] = {}
        self._load_language(self.current_language)

    def _load_language(self, lang_code: str) -> bool:
        """加载指定语言的翻译资源。

        Args:
            lang_code: 语言代码 (zh_CN, en_US)

        Returns:
            bool: 加载是否成功
        """
        try:
            if lang_code == "zh_CN":
                from .zh_CN import TRANSLATIONS
            elif lang_code == "en_US":
                from .en_US import TRANSLATIONS
            else:
                # 未知语言，回退到默认语言
                from .zh_CN import TRANSLATIONS
                lang_code = DEFAULT_LANGUAGE

            self.translations = TRANSLATIONS.copy()
            self.current_language = lang_code
            return True
        except ImportError:
            # 语言包不存在，尝试加载默认语言
            if lang_code != DEFAULT_LANGUAGE:
                return self._load_language(DEFAULT_LANGUAGE)
            # 默认语言也加载失败，使用空字典
            self.translations = {}
            return False

    def set_language(self, lang_code: str) -> bool:
        """切换语言。

        Args:
            lang_code: 语言代码 (zh_CN, en_US)

        Returns:
            bool: 切换是否成功
        """
        if lang_code == self.current_language:
            return True
        return self._load_language(lang_code)

    def get(self, key: str, **kwargs) -> str:
        """获取翻译文本。

        Args:
            key: 翻译键
            **kwargs: 格式化参数

        Returns:
            str: 翻译后的文本，如果键不存在则返回键本身
        """
        text = self.translations.get(key, key)
        if kwargs:
            try:
                return text.format(**kwargs)
            except (KeyError, ValueError):
                # 格式化失败，返回原文本
                return text
        return text

    def get_available_languages(self) -> List[Tuple[str, str]]:
        """获取可用语言列表。

        Returns:
            List[Tuple[str, str]]: [(语言代码, 显示名称), ...]
        """
        return AVAILABLE_LANGUAGES.copy()

    def get_language_display_name(self, lang_code: str) -> str:
        """获取语言的显示名称。

        Args:
            lang_code: 语言代码

        Returns:
            str: 显示名称，如果未找到则返回语言代码本身
        """
        for code, name in AVAILABLE_LANGUAGES:
            if code == lang_code:
                return name
        return lang_code

    @classmethod
    def reset(cls) -> None:
        """重置单例实例（仅用于测试）。"""
        cls._instance = None
        cls._initialized = False


# 全局 i18n 实例
i18n = I18nManager()
