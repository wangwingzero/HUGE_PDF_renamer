#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""配置管理测试模块

包含配置持久化的单元测试和属性测试。

Feature: internationalization, Property 3: Configuration Round-Trip
Validates: Requirements 2.1, 2.2, 2.4
"""

import json
import pytest
import tempfile
from pathlib import Path
from hypothesis import given, strategies as st, settings

import sys

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from main.config import RenameConfig, ConfigManager, SUPPORTED_LANGUAGES, DEFAULT_LANGUAGE


class TestRenameConfig:
    """RenameConfig 数据类测试"""

    def test_default_values(self):
        """测试默认配置值"""
        config = RenameConfig()
        assert config.max_filename_length == 120
        assert config.add_timestamp is False
        assert config.auto_backup is False
        assert config.parallel_processing is True
        assert config.max_workers == 4
        assert config.language == DEFAULT_LANGUAGE

    def test_language_default_is_zh_cn(self):
        """测试默认语言为中文"""
        config = RenameConfig()
        assert config.language == "zh_CN"

    def test_invalid_language_corrected(self):
        """测试无效语言被修正为默认值"""
        config = RenameConfig(language="invalid_lang")
        assert config.language == DEFAULT_LANGUAGE

    def test_valid_languages_accepted(self):
        """测试有效语言被接受"""
        for lang in SUPPORTED_LANGUAGES:
            config = RenameConfig(language=lang)
            assert config.language == lang

    def test_value_validation(self):
        """测试配置值验证"""
        config = RenameConfig(max_filename_length=5, max_workers=100)
        assert config.max_filename_length == 10  # 最小值
        assert config.max_workers == 16  # 最大值


class TestConfigManagerLanguage:
    """ConfigManager 语言设置测试"""

    def test_save_and_load_language(self):
        """测试保存和加载语言设置"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / "config.json"
            
            # 创建配置管理器并设置语言
            manager = ConfigManager.__new__(ConfigManager)
            manager.config_file = config_file
            manager.config = RenameConfig(language="en_US")
            manager.save_config()
            
            # 验证文件内容
            with open(config_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            assert data["language"] == "en_US"
            
            # 重新加载
            manager2 = ConfigManager.__new__(ConfigManager)
            manager2.config_file = config_file
            manager2.config = manager2._load_config()
            assert manager2.config.language == "en_US"

    def test_update_language(self):
        """测试更新语言设置"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / "config.json"
            
            manager = ConfigManager.__new__(ConfigManager)
            manager.config_file = config_file
            manager.config = RenameConfig()
            
            # 更新语言
            success = manager.update_config(language="en_US")
            assert success is True
            assert manager.config.language == "en_US"
            
            # 验证文件已更新
            with open(config_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            assert data["language"] == "en_US"

    def test_missing_language_uses_default(self):
        """测试缺少语言字段时使用默认值"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / "config.json"
            
            # 创建不包含 language 字段的配置文件（模拟旧版本配置）
            old_config = {
                "max_filename_length": 100,
                "add_timestamp": True
            }
            with open(config_file, "w", encoding="utf-8") as f:
                json.dump(old_config, f)
            
            # 加载配置
            manager = ConfigManager.__new__(ConfigManager)
            manager.config_file = config_file
            manager.config = manager._load_config()
            
            # 应该使用默认语言
            assert manager.config.language == DEFAULT_LANGUAGE


class TestConfigRoundTrip:
    """配置持久化 Round-Trip 属性测试
    
    Feature: internationalization, Property 3: Configuration Round-Trip
    Validates: Requirements 2.1, 2.2, 2.4
    """

    @given(st.sampled_from(SUPPORTED_LANGUAGES))
    @settings(max_examples=100)
    def test_language_round_trip(self, lang_code: str):
        """Property 3: 语言设置的 Round-Trip 测试
        
        Feature: internationalization, Property 3: Configuration Round-Trip
        Validates: Requirements 2.1, 2.2, 2.4
        
        For any valid language code, saving it to the configuration and then
        loading a new ConfigManager instance SHALL return the same language code.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / "config.json"
            
            # 保存配置
            manager1 = ConfigManager.__new__(ConfigManager)
            manager1.config_file = config_file
            manager1.config = RenameConfig(language=lang_code)
            manager1.save_config()
            
            # 加载配置
            manager2 = ConfigManager.__new__(ConfigManager)
            manager2.config_file = config_file
            manager2.config = manager2._load_config()
            
            # 验证 round-trip
            assert manager2.config.language == lang_code

    @given(
        st.integers(min_value=10, max_value=255),
        st.booleans(),
        st.booleans(),
        st.booleans(),
        st.integers(min_value=1, max_value=16),
        st.sampled_from(SUPPORTED_LANGUAGES)
    )
    @settings(max_examples=100)
    def test_full_config_round_trip(
        self,
        max_len: int,
        add_ts: bool,
        backup: bool,
        parallel: bool,
        workers: int,
        lang: str
    ):
        """Property 3: 完整配置的 Round-Trip 测试
        
        Feature: internationalization, Property 3: Configuration Round-Trip
        Validates: Requirements 2.1, 2.2, 2.4
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / "config.json"
            
            # 创建配置
            original = RenameConfig(
                max_filename_length=max_len,
                add_timestamp=add_ts,
                auto_backup=backup,
                parallel_processing=parallel,
                max_workers=workers,
                language=lang
            )
            
            # 保存
            manager1 = ConfigManager.__new__(ConfigManager)
            manager1.config_file = config_file
            manager1.config = original
            manager1.save_config()
            
            # 加载
            manager2 = ConfigManager.__new__(ConfigManager)
            manager2.config_file = config_file
            manager2.config = manager2._load_config()
            
            # 验证所有字段
            assert manager2.config.max_filename_length == max_len
            assert manager2.config.add_timestamp == add_ts
            assert manager2.config.auto_backup == backup
            assert manager2.config.parallel_processing == parallel
            assert manager2.config.max_workers == workers
            assert manager2.config.language == lang


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
