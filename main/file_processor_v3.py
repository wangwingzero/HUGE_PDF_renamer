"""File processing core for PDF Renamer v3.

相比 v2：
- 始终使用 SmartTextExtractorV3（元数据 + 前几页启发式）；
- 逻辑更简单，只保留必要的清理 / 冲突处理 / 备份；
- 仍然支持并行处理和进度回调。
"""

from __future__ import annotations

import logging
import shutil
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Callable, List, Optional, Tuple

from .config_v3 import config_manager_v3
from .smart_text_extractor_v3 import SmartTextExtractorV3, ExtractedText


@dataclass
class RenameResultV3:
    original_path: Path
    new_path: Optional[Path]
    success: bool
    error_message: Optional[str]
    extracted_text: Optional[ExtractedText]
    backup_path: Optional[Path] = None


@dataclass
class ProcessStatsV3:
    total_files: int = 0
    successful: int = 0
    failed: int = 0
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None

    @property
    def duration(self) -> float:
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return 0.0

    @property
    def success_rate(self) -> float:
        if self.total_files == 0:
            return 0.0
        return self.successful / self.total_files


class FileProcessorV3:
    """v3 版本的文件处理器"""

    def __init__(self, logger: Optional[logging.Logger] = None) -> None:
        self.logger = logger or logging.getLogger(__name__)
        self.text_extractor = SmartTextExtractorV3(self.logger)
        self.config = config_manager_v3.config

    def process_files(
        self,
        files: List[Path],
        progress_callback: Optional[Callable[[int, int, Path, RenameResultV3], None]] = None,
    ) -> Tuple[List[RenameResultV3], ProcessStatsV3]:
        stats = ProcessStatsV3(total_files=len(files), start_time=datetime.now())
        results: List[RenameResultV3] = []

        for idx, file_path in enumerate(files, start=1):
            result = self._process_single(file_path)
            results.append(result)

            if result.success:
                stats.successful += 1
            else:
                stats.failed += 1

            if progress_callback:
                progress_callback(idx, len(files), file_path, result)

        stats.end_time = datetime.now()
        self.logger.info(
            f"[v3] 处理完成: {stats.successful}/{stats.total_files} 成功, 用时 {stats.duration:.1f}秒"
        )
        return results, stats

    # === 单文件处理 ===

    def _process_single(self, file_path: Path) -> RenameResultV3:
        try:
            self.logger.info(f"[v3] 处理文件: {file_path.name}")

            extracted = self.text_extractor.extract_title(file_path)
            if not extracted:
                return RenameResultV3(
                    original_path=file_path,
                    new_path=None,
                    success=False,
                    error_message="无法提取标题",
                    extracted_text=None,
                )

            clean_name = self._clean_filename(extracted.text)
            if not clean_name:
                return RenameResultV3(
                    original_path=file_path,
                    new_path=None,
                    success=False,
                    error_message="清理后文件名为空",
                    extracted_text=extracted,
                )

            new_filename = self._generate_filename(clean_name, file_path)
            target = self._resolve_conflict(file_path.parent / new_filename, file_path)

            if target.name == file_path.name:
                return RenameResultV3(
                    original_path=file_path,
                    new_path=file_path,
                    success=True,
                    error_message=None,
                    extracted_text=extracted,
                )

            backup_path: Optional[Path] = None
            if self.config.auto_backup:
                backup_path = self._create_backup(file_path)

            file_path.rename(target)
            self.logger.info(f"[v3] 重命名成功: {file_path.name} -> {target.name}")

            return RenameResultV3(
                original_path=file_path,
                new_path=target,
                success=True,
                error_message=None,
                extracted_text=extracted,
                backup_path=backup_path,
            )

        except Exception as e:  # noqa: BLE001
            msg = str(e)
            self.logger.error(f"[v3] 处理文件失败 {file_path.name}: {msg}")
            return RenameResultV3(
                original_path=file_path,
                new_path=None,
                success=False,
                error_message=msg,
                extracted_text=None,
            )

    # === 文件名处理 ===

    def _clean_filename(self, text: str) -> str:
        name = text.strip()
        if len(name) == 0:
            return ""

        illegal = '<>:"/\\|?*'
        for ch in illegal:
            name = name.replace(ch, "")

        while "  " in name:
            name = name.replace("  ", " ")

        name = name.strip(". ")

        max_len = self.config.max_filename_length
        if len(name) > max_len:
            name = name[: max_len - 3] + "..."

        return name

    def _generate_filename(self, base_name: str, original_path: Path) -> str:
        filename = base_name
        if self.config.add_timestamp:
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{filename}_{ts}"
        return f"{filename}{original_path.suffix}"

    def _resolve_conflict(self, target: Path, original: Path) -> Path:
        if not target.exists() or target == original:
            return target

        base = target.stem
        suffix = target.suffix
        parent = target.parent

        for idx in range(1, 1000):
            cand = parent / f"{base}_{idx}{suffix}"
            if not cand.exists():
                return cand

        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        return parent / f"{base}_{ts}{suffix}"

    def _create_backup(self, file_path: Path) -> Optional[Path]:
        try:
            backup_dir = file_path.parent / "backup_v3"
            backup_dir.mkdir(exist_ok=True)

            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"{file_path.stem}_{ts}{file_path.suffix}"
            backup_path = backup_dir / backup_name
            shutil.copy2(file_path, backup_path)
            self.logger.info(f"[v3] 创建备份: {backup_path}")
            return backup_path
        except Exception as e:  # noqa: BLE001
            self.logger.warning(f"[v3] 创建备份失败: {e}")
            return None
