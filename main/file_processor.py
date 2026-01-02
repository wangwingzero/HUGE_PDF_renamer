#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""文件处理核心模块

负责 PDF 文件的批量重命名处理，包括标题提取、文件名清理、
冲突解决和备份管理。

Copyright (c) 2024-2026 虎哥
Licensed under the MIT License.

Version: 1.0.0
"""

from __future__ import annotations

import logging
import shutil
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Callable, List, Optional, Tuple

from .config import config_manager
from .smart_text_extractor import SmartTextExtractor, ExtractedText

# 文件名处理常量
ILLEGAL_CHARS = '<>:"/\\|?*'
BACKUP_DIR_NAME = "backup"
MAX_CONFLICT_ATTEMPTS = 1000


@dataclass
class RenameResult:
    """单个文件的重命名结果。

    记录重命名操作的完整信息，包括原路径、新路径、成功状态等。

    Attributes:
        original_path: 原始文件路径
        new_path: 新文件路径，失败时为 None
        success: 是否成功
        error_message: 错误信息，成功时为 None
        extracted_text: 提取的文本信息
        backup_path: 备份文件路径，未备份时为 None
    """

    original_path: Path
    new_path: Optional[Path]
    success: bool
    error_message: Optional[str]
    extracted_text: Optional[ExtractedText]
    backup_path: Optional[Path] = None


@dataclass
class ProcessStats:
    """批量处理统计信息。

    记录批量处理的统计数据，包括文件数量、成功/失败数、耗时等。

    Attributes:
        total_files: 总文件数
        successful: 成功数
        failed: 失败数
        start_time: 开始时间
        end_time: 结束时间
    """

    total_files: int = 0
    successful: int = 0
    failed: int = 0
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None

    @property
    def duration(self) -> float:
        """处理耗时（秒）。

        Returns:
            float: 处理耗时，未完成时返回 0.0
        """
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return 0.0

    @property
    def success_rate(self) -> float:
        """成功率。

        Returns:
            float: 成功率，范围 0-1，无文件时返回 0.0
        """
        if self.total_files == 0:
            return 0.0
        return self.successful / self.total_files


# 类型别名
ProgressCallback = Callable[[int, int, Path, RenameResult], None]
CancelCheck = Callable[[], bool]


class FileProcessor:
    """文件处理器。

    提供批量 PDF 重命名功能，支持进度回调和取消操作。

    Attributes:
        logger: 日志记录器
        text_extractor: 文本提取器实例

    Example:
        >>> processor = FileProcessor()
        >>> results, stats = processor.process_files([Path("doc.pdf")])
        >>> print(f"成功率: {stats.success_rate:.1%}")
    """

    def __init__(self, logger: Optional[logging.Logger] = None) -> None:
        """初始化文件处理器。

        Args:
            logger: 日志记录器，如果为 None 则使用模块默认 logger
        """
        self.logger = logger or logging.getLogger(__name__)
        self.text_extractor = SmartTextExtractor(self.logger)

    @property
    def config(self):
        """获取当前配置。

        Returns:
            RenameConfig: 当前配置实例
        """
        return config_manager.config

    def process_files(
        self,
        files: List[Path],
        progress_callback: Optional[ProgressCallback] = None,
        cancel_check: Optional[CancelCheck] = None,
    ) -> Tuple[List[RenameResult], ProcessStats]:
        """批量处理文件。

        遍历文件列表，对每个文件执行重命名操作。支持进度回调和取消检查。

        Args:
            files: 待处理的文件列表
            progress_callback: 进度回调函数，签名为 (当前索引, 总数, 当前文件, 结果)
            cancel_check: 取消检查函数，返回 True 时停止处理

        Returns:
            Tuple[List[RenameResult], ProcessStats]: (结果列表, 统计信息) 元组
        """
        stats = ProcessStats(total_files=len(files), start_time=datetime.now())
        results: List[RenameResult] = []

        for idx, file_path in enumerate(files, start=1):
            # 检查取消
            if cancel_check and cancel_check():
                self.logger.info("用户取消处理")
                break

            result = self._process_single(file_path)
            results.append(result)

            if result.success:
                stats.successful += 1
            else:
                stats.failed += 1

            if progress_callback:
                progress_callback(idx, len(files), file_path, result)

        stats.total_files = len(results)
        stats.end_time = datetime.now()

        self.logger.info(
            f"处理完成: {stats.successful}/{stats.total_files} 成功, "
            f"用时 {stats.duration:.1f}秒"
        )
        return results, stats

    def _process_single(self, file_path: Path) -> RenameResult:
        """处理单个文件。

        Args:
            file_path: 文件路径

        Returns:
            RenameResult: 处理结果
        """
        try:
            self.logger.info(f"处理: {file_path.name}")

            # 提取标题
            extracted = self.text_extractor.extract_title(file_path)
            if not extracted:
                return self._make_error_result(file_path, "无法提取标题")

            # 清理文件名
            clean_name = self._clean_filename(extracted.text)
            if not clean_name:
                return self._make_error_result(
                    file_path, "清理后文件名为空", extracted
                )

            # 生成目标路径
            new_filename = self._generate_filename(clean_name, file_path)
            target = self._resolve_conflict(file_path.parent / new_filename, file_path)

            # 无需重命名
            if target.name == file_path.name:
                return RenameResult(
                    original_path=file_path,
                    new_path=file_path,
                    success=True,
                    error_message=None,
                    extracted_text=extracted,
                )

            # 备份（如果启用）
            backup_path = None
            if self.config.auto_backup:
                backup_path = self._create_backup(file_path)

            # 执行重命名
            file_path.rename(target)
            self.logger.info(f"重命名: {file_path.name} -> {target.name}")

            return RenameResult(
                original_path=file_path,
                new_path=target,
                success=True,
                error_message=None,
                extracted_text=extracted,
                backup_path=backup_path,
            )

        except Exception as e:
            self.logger.error(f"处理失败 {file_path.name}: {e}")
            return self._make_error_result(file_path, str(e))

    def _make_error_result(
        self,
        file_path: Path,
        error: str,
        extracted: Optional[ExtractedText] = None,
    ) -> RenameResult:
        """创建错误结果。

        Args:
            file_path: 文件路径
            error: 错误信息
            extracted: 已提取的文本（如果有）

        Returns:
            RenameResult: 错误结果实例
        """
        return RenameResult(
            original_path=file_path,
            new_path=None,
            success=False,
            error_message=error,
            extracted_text=extracted,
        )

    def _clean_filename(self, text: str) -> str:
        """清理文件名，移除非法字符。

        Args:
            text: 原始文本

        Returns:
            str: 清理后的文件名
        """
        name = text.strip()
        if not name:
            return ""

        # 移除非法字符
        for ch in ILLEGAL_CHARS:
            name = name.replace(ch, "")

        # 合并连续空格
        while "  " in name:
            name = name.replace("  ", " ")

        # 去除首尾点和空格
        name = name.strip(". ")

        # 截断过长文件名
        max_len = self.config.max_filename_length
        if len(name) > max_len:
            name = name[: max_len - 3] + "..."

        return name

    def _generate_filename(self, base_name: str, original_path: Path) -> str:
        """生成最终文件名。

        Args:
            base_name: 基础文件名（不含扩展名）
            original_path: 原始文件路径

        Returns:
            str: 完整文件名（含扩展名）
        """
        filename = base_name

        if self.config.add_timestamp:
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{filename}_{ts}"

        return f"{filename}{original_path.suffix}"

    def _resolve_conflict(self, target: Path, original: Path) -> Path:
        """解决文件名冲突。

        如果目标文件已存在，尝试添加数字后缀或时间戳。

        Args:
            target: 目标路径
            original: 原始路径

        Returns:
            Path: 不冲突的目标路径
        """
        if not target.exists() or target == original:
            return target

        base = target.stem
        suffix = target.suffix
        parent = target.parent

        # 尝试数字后缀
        for idx in range(1, MAX_CONFLICT_ATTEMPTS):
            candidate = parent / f"{base}_{idx}{suffix}"
            if not candidate.exists():
                return candidate

        # 最后使用时间戳
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        return parent / f"{base}_{ts}{suffix}"

    def _create_backup(self, file_path: Path) -> Optional[Path]:
        """创建文件备份。

        Args:
            file_path: 原始文件路径

        Returns:
            Path: 备份文件路径，失败时返回 None
        """
        try:
            backup_dir = file_path.parent / BACKUP_DIR_NAME
            backup_dir.mkdir(exist_ok=True)

            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"{file_path.stem}_{ts}{file_path.suffix}"
            backup_path = backup_dir / backup_name

            shutil.copy2(file_path, backup_path)
            self.logger.info(f"备份: {backup_path}")
            return backup_path
        except Exception as e:
            self.logger.warning(f"备份失败: {e}")
            return None
