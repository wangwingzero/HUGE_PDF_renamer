#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""I18nManager 测试模块

包含单元测试和属性测试，验证国际化功能的正确性。

Feature: internationalization
"""

import pytest
from hypothesis import given, strategies as st, settings

import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from main.i18n import I18nManager, AVAILABLE_LANGUAGES, DEFAULT_LANGUAGE


class TestI18nManagerBasic:
    """I18nManager 基础单元测试"""

    def setup_method(self):
        """每个测试前重置单例"""
        I18nManager.reset()

    def test_singleton_pattern(self):
        """测试单例模式"""
        i18n1 = I18nManager()
        i18n2 = I18nManager()
        assert i18n1 is i18n2

    def test_default_language(self):
        """测试默认语言为中文"""
        i18n = I18nManager()
        assert i18n.current_language == DEFAULT_LANGUAGE
        assert i18n.current_language == "zh_CN"

    def test_get_existing_key(self):
        """测试获取存在的翻译键"""
        i18n = I18nManager()
        result = i18n.get("app.name")
        assert result == "虎哥PDF重命名"

    def test_set_language_english(self):
        """测试切换到英文"""
        i18n = I18nManager()
        success = i18n.set_language("en_US")
        assert success is True
        assert i18n.current_language == "en_US"
        assert i18n.get("app.name") == "Tiger PDF Renamer"

    def test_set_language_same(self):
        """测试切换到相同语言"""
        i18n = I18nManager()
        success = i18n.set_language("zh_CN")
        assert success is True

    def test_get_available_languages(self):
        """测试获取可用语言列表"""
        i18n = I18nManager()
        languages = i18n.get_available_languages()
        assert len(languages) >= 2
        assert ("zh_CN", "中文") in languages
        assert ("en_US", "English") in languages

    def test_get_language_display_name(self):
        """测试获取语言显示名称"""
        i18n = I18nManager()
        assert i18n.get_language_display_name("zh_CN") == "中文"
        assert i18n.get_language_display_name("en_US") == "English"
        assert i18n.get_language_display_name("unknown") == "unknown"


class TestI18nManagerFormatting:
    """I18nManager 字符串格式化测试"""

    def setup_method(self):
        """每个测试前重置单例"""
        I18nManager.reset()

    def test_format_with_count(self):
        """测试带 count 参数的格式化"""
        i18n = I18nManager()
        result = i18n.get("panel.files.count", count=5)
        assert result == "5 个文件"

    def test_format_with_multiple_params(self):
        """测试带多个参数的格式化"""
        i18n = I18nManager()
        result = i18n.get("status.done", emoji="🎉", success=8, total=10, time="2.5")
        assert "8" in result
        assert "10" in result
        assert "2.5" in result

    def test_format_missing_param(self):
        """测试缺少格式化参数时返回原文本"""
        i18n = I18nManager()
        # 缺少参数时应返回原模板文本
        result = i18n.get("panel.files.count")
        assert "{count}" in result


class TestI18nManagerPropertyTests:
    """I18nManager 属性测试
    
    Feature: internationalization, Property 1: Translation Lookup with Fallback
    Validates: Requirements 1.1, 1.3
    """

    def setup_method(self):
        """每个测试前重置单例"""
        I18nManager.reset()

    @given(st.text(min_size=1, max_size=100))
    @settings(max_examples=100)
    def test_fallback_returns_key_for_nonexistent(self, key: str):
        """Property 1: 不存在的键应返回键本身
        
        Feature: internationalization, Property 1: Translation Lookup with Fallback
        Validates: Requirements 1.1, 1.3
        
        For any translation key that does not exist in the current language pack,
        the I18nManager SHALL return the key itself as fallback.
        """
        i18n = I18nManager()
        # 使用一个肯定不存在的前缀
        fake_key = f"__nonexistent_prefix__.{key}"
        result = i18n.get(fake_key)
        assert result == fake_key

    @given(st.sampled_from(["zh_CN", "en_US"]))
    @settings(max_examples=100)
    def test_existing_keys_return_translation(self, lang_code: str):
        """Property 1: 存在的键应返回对应翻译
        
        Feature: internationalization, Property 1: Translation Lookup with Fallback
        Validates: Requirements 1.1, 1.3
        
        For any translation key that exists in the current language pack,
        the I18nManager SHALL return the corresponding translation.
        """
        I18nManager.reset()
        i18n = I18nManager()
        i18n.set_language(lang_code)
        
        # 测试一些已知存在的键
        known_keys = ["app.name", "btn.start", "settings.title"]
        for key in known_keys:
            result = i18n.get(key)
            # 结果不应该等于键本身（因为键存在）
            assert result != key
            # 结果应该是非空字符串
            assert len(result) > 0


class TestI18nManagerFormattingProperty:
    """字符串格式化属性测试
    
    Feature: internationalization, Property 4: String Formatting with Placeholders
    Validates: Requirements 6.1, 6.4
    """

    def setup_method(self):
        """每个测试前重置单例"""
        I18nManager.reset()

    @given(st.integers(min_value=0, max_value=10000))
    @settings(max_examples=100)
    def test_count_formatting(self, count: int):
        """Property 4: 带占位符的字符串应正确格式化
        
        Feature: internationalization, Property 4: String Formatting with Placeholders
        Validates: Requirements 6.1, 6.4
        
        For any translation string containing placeholders, calling get(key, **kwargs)
        with the appropriate keyword arguments SHALL return a properly formatted string.
        """
        i18n = I18nManager()
        result = i18n.get("panel.files.count", count=count)
        assert str(count) in result
        assert "{count}" not in result

    @given(
        st.integers(min_value=0, max_value=1000),
        st.integers(min_value=0, max_value=1000),
        st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False)
    )
    @settings(max_examples=100)
    def test_multiple_placeholder_formatting(self, success: int, total: int, time: float):
        """Property 4: 多占位符字符串应正确格式化
        
        Feature: internationalization, Property 4: String Formatting with Placeholders
        Validates: Requirements 6.1, 6.4
        """
        i18n = I18nManager()
        time_str = f"{time:.1f}"
        result = i18n.get("status.done", emoji="✅", success=success, total=total, time=time_str)
        assert str(success) in result
        assert str(total) in result
        assert "{success}" not in result
        assert "{total}" not in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
