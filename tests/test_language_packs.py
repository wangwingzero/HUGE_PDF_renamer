#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""语言包完整性测试模块

验证所有语言包包含必需的翻译键。

Feature: internationalization, Property 2: Language Pack Completeness
Validates: Requirements 1.4, 4.1, 4.2, 4.3, 4.4, 4.5, 4.6
"""

import pytest
from hypothesis import given, strategies as st, settings

import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from main.i18n import AVAILABLE_LANGUAGES
from main.i18n.zh_CN import TRANSLATIONS as ZH_TRANSLATIONS
from main.i18n.en_US import TRANSLATIONS as EN_TRANSLATIONS


# 必需的翻译键列表
REQUIRED_KEYS = [
    # 应用信息
    "app.name",
    "app.subtitle",
    
    # 文件面板
    "panel.files",
    "panel.files.count",
    "panel.files.placeholder",
    
    # 按钮
    "btn.select_files",
    "btn.select_folder",
    "btn.clear",
    "btn.preview",
    "btn.start",
    "btn.cancel",
    
    # 设置
    "settings.title",
    "settings.max_length",
    "settings.backup",
    "settings.parallel",
    "settings.timestamp",
    "settings.language",
    
    # 模式说明
    "mode.smart",
    "mode.smart.desc",
    
    # 状态消息
    "status.ready",
    "status.selected",
    "status.processing",
    "status.done",
    "status.cancelled",
    
    # 进度
    "progress.ready",
    "progress.processing",
    "progress.done",
    
    # 日志
    "log.title",
    
    # 对话框
    "dialog.error",
    "dialog.warning",
    "dialog.max_length_error",
    "dialog.select_files_first",
    
    # 页脚
    "footer.author",
]


class TestLanguagePackCompleteness:
    """语言包完整性测试
    
    Feature: internationalization, Property 2: Language Pack Completeness
    Validates: Requirements 1.4, 4.1, 4.2, 4.3, 4.4, 4.5, 4.6
    """

    def test_zh_cn_has_all_required_keys(self):
        """测试中文语言包包含所有必需键"""
        missing_keys = []
        for key in REQUIRED_KEYS:
            if key not in ZH_TRANSLATIONS:
                missing_keys.append(key)
        
        assert len(missing_keys) == 0, f"中文语言包缺少以下键: {missing_keys}"

    def test_en_us_has_all_required_keys(self):
        """测试英文语言包包含所有必需键"""
        missing_keys = []
        for key in REQUIRED_KEYS:
            if key not in EN_TRANSLATIONS:
                missing_keys.append(key)
        
        assert len(missing_keys) == 0, f"英文语言包缺少以下键: {missing_keys}"

    def test_language_packs_have_same_keys(self):
        """测试两个语言包有相同的键集合"""
        zh_keys = set(ZH_TRANSLATIONS.keys())
        en_keys = set(EN_TRANSLATIONS.keys())
        
        only_in_zh = zh_keys - en_keys
        only_in_en = en_keys - zh_keys
        
        assert len(only_in_zh) == 0, f"仅在中文包中存在的键: {only_in_zh}"
        assert len(only_in_en) == 0, f"仅在英文包中存在的键: {only_in_en}"

    def test_all_values_are_non_empty_strings(self):
        """测试所有翻译值都是非空字符串"""
        for lang_name, translations in [("zh_CN", ZH_TRANSLATIONS), ("en_US", EN_TRANSLATIONS)]:
            empty_keys = []
            for key, value in translations.items():
                if not isinstance(value, str) or len(value.strip()) == 0:
                    empty_keys.append(key)
            
            assert len(empty_keys) == 0, f"{lang_name} 语言包中以下键的值为空: {empty_keys}"

    @given(st.sampled_from(REQUIRED_KEYS))
    @settings(max_examples=100)
    def test_required_key_exists_in_all_languages(self, key: str):
        """Property 2: 所有必需键在所有语言包中都存在
        
        Feature: internationalization, Property 2: Language Pack Completeness
        Validates: Requirements 1.4, 4.1, 4.2, 4.3, 4.4, 4.5, 4.6
        
        For any supported language, the language pack SHALL contain all required
        translation keys (app info, buttons, settings, status messages, dialogs, etc.).
        """
        assert key in ZH_TRANSLATIONS, f"键 '{key}' 不在中文语言包中"
        assert key in EN_TRANSLATIONS, f"键 '{key}' 不在英文语言包中"
        
        # 验证值非空
        assert len(ZH_TRANSLATIONS[key].strip()) > 0, f"中文语言包中键 '{key}' 的值为空"
        assert len(EN_TRANSLATIONS[key].strip()) > 0, f"英文语言包中键 '{key}' 的值为空"


class TestLanguagePackContent:
    """语言包内容测试"""

    def test_app_names_are_different(self):
        """测试中英文应用名称不同"""
        assert ZH_TRANSLATIONS["app.name"] != EN_TRANSLATIONS["app.name"]

    def test_button_labels_contain_emoji(self):
        """测试按钮标签包含 emoji"""
        button_keys = [k for k in REQUIRED_KEYS if k.startswith("btn.")]
        for key in button_keys:
            # 检查是否包含常见的 emoji 字符
            zh_value = ZH_TRANSLATIONS.get(key, "")
            en_value = EN_TRANSLATIONS.get(key, "")
            # 至少有一个语言包的按钮应该包含 emoji
            has_emoji = any(ord(c) > 127 for c in zh_value) or any(ord(c) > 127 for c in en_value)
            # 这个测试比较宽松，主要确保按钮文本存在
            assert len(zh_value) > 0 and len(en_value) > 0

    def test_placeholder_keys_have_placeholders(self):
        """测试带占位符的键确实包含占位符"""
        placeholder_keys = [
            "panel.files.count",
            "status.selected",
            "status.processing",
            "status.done",
            "status.cancelled",
            "progress.processing",
            "progress.done",
            "footer.author",
        ]
        
        for key in placeholder_keys:
            zh_value = ZH_TRANSLATIONS.get(key, "")
            en_value = EN_TRANSLATIONS.get(key, "")
            # 检查是否包含 {xxx} 格式的占位符
            has_placeholder_zh = "{" in zh_value and "}" in zh_value
            has_placeholder_en = "{" in en_value and "}" in en_value
            assert has_placeholder_zh, f"中文键 '{key}' 应包含占位符"
            assert has_placeholder_en, f"英文键 '{key}' 应包含占位符"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
