#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""智能文本提取模块

从 PDF 文件中提取标题，优先使用元数据，失败时分析首页内容。
支持中英文标题识别，针对航空手册等技术文档进行了优化。

Copyright (c) 2024-2026 虎哥
Licensed under the MIT License.

Version: 1.0.0
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Tuple

# 提取配置常量
MIN_TITLE_LENGTH = 4
MAX_TITLE_LENGTH = 120
DEFAULT_MAX_PAGES = 2

# 标题评分关键词（航空/技术文档常见词汇）
TITLE_KEYWORDS = (
    "飞行手册",
    "操作手册",
    "操作程序",
    "技术通告",
    "Flight Manual",
    "Manual",
    "AFM",
)


@dataclass
class ExtractedText:
    """提取结果数据类。

    存储从 PDF 中提取的文本信息及其元数据。

    Attributes:
        text: 提取的文本内容
        confidence: 置信度，范围 0-1
        strategy: 提取策略名称，如 "metadata" 或 "first_pages"
        position: 文本在页面中的位置坐标 (x, y)
        font_size: 文本字体大小
    """

    text: str
    confidence: float
    strategy: str
    position: Tuple[float, float] = (0.0, 0.0)
    font_size: float = 0.0


# 延迟导入 PDF 库，避免启动时报错
try:
    from pypdf import PdfReader
except ImportError:
    PdfReader = None  # type: ignore

try:
    import pdfplumber
except ImportError:
    pdfplumber = None  # type: ignore


class SmartTextExtractor:
    """智能标题提取器。

    从 PDF 文件中智能提取标题，支持多种提取策略：
    1. PDF 元数据 (Title 字段) - 优先级最高
    2. 首页文本启发式分析 - 备选方案

    Attributes:
        logger: 日志记录器实例

    Example:
        >>> extractor = SmartTextExtractor()
        >>> result = extractor.extract_title(Path("document.pdf"))
        >>> if result:
        ...     print(f"标题: {result.text}")
    """

    def __init__(self, logger: Optional[logging.Logger] = None) -> None:
        """初始化提取器。

        Args:
            logger: 日志记录器，如果为 None 则使用模块默认 logger
        """
        self.logger = logger or logging.getLogger(__name__)

    def extract_title(self, pdf_path: Path) -> Optional[ExtractedText]:
        """提取 PDF 标题。

        按优先级尝试不同的提取策略，返回第一个成功的结果。

        Args:
            pdf_path: PDF 文件路径

        Returns:
            ExtractedText: 提取结果，包含文本和元数据；提取失败时返回 None
        """
        # 策略1: 元数据
        title = self._extract_from_metadata(pdf_path)
        if title:
            return ExtractedText(
                text=title,
                confidence=0.9,
                strategy="metadata",
            )

        # 策略2: 首页文本
        title = self._extract_from_first_pages(pdf_path, max_pages=DEFAULT_MAX_PAGES)
        if title:
            return ExtractedText(
                text=title,
                confidence=0.8,
                strategy="first_pages",
            )

        return None

    def _extract_from_metadata(self, pdf_path: Path) -> Optional[str]:
        """从 PDF 元数据提取标题。

        Args:
            pdf_path: PDF 文件路径

        Returns:
            str: 提取的标题，失败时返回 None
        """
        if PdfReader is None:
            return None

        try:
            reader = PdfReader(str(pdf_path))
            candidates = self._collect_metadata_titles(reader)

            for raw in candidates:
                cleaned = self._clean_candidate(raw)
                if cleaned:
                    self.logger.info(f"元数据标题: {cleaned}")
                    return cleaned
        except Exception as e:
            self.logger.debug(f"读取元数据失败: {e}")

        return None

    def _collect_metadata_titles(self, reader: "PdfReader") -> List[str]:
        """收集元数据中的标题候选。

        Args:
            reader: PdfReader 实例

        Returns:
            List[str]: 标题候选列表
        """
        candidates: List[str] = []

        # 尝试 metadata 属性
        meta = getattr(reader, "metadata", None)
        if meta is not None:
            title = getattr(meta, "title", None)
            if isinstance(title, str):
                candidates.append(title)

        # 尝试 documentInfo 属性（旧版 pypdf）
        info = getattr(reader, "documentInfo", None)
        if info is not None:
            title = getattr(info, "title", None)
            if isinstance(title, str):
                candidates.append(title)

        return candidates

    def _extract_from_first_pages(
        self,
        pdf_path: Path,
        max_pages: int = DEFAULT_MAX_PAGES,
    ) -> Optional[str]:
        """从首页文本提取标题。

        分析 PDF 前几页的文本内容，使用启发式算法找出最可能的标题。

        Args:
            pdf_path: PDF 文件路径
            max_pages: 最大分析页数，默认为 2

        Returns:
            str: 提取的标题，失败时返回 None
        """
        if pdfplumber is None:
            return None

        try:
            with pdfplumber.open(str(pdf_path)) as pdf:
                best_line: Optional[str] = None
                best_score = 0.0

                for page in pdf.pages[:max_pages]:
                    text = page.extract_text() or ""
                    for line in text.splitlines():
                        candidate = self._clean_candidate(line)
                        if not candidate:
                            continue
                        score = self._score_line(candidate)
                        if score > best_score:
                            best_score = score
                            best_line = candidate

                if best_line:
                    self.logger.info(f"首页标题: {best_line}")
                    return best_line
        except Exception as e:
            self.logger.warning(f"首页提取失败: {e}")

        return None

    def _clean_candidate(self, text: str) -> str:
        """清理候选文本。

        移除无效字符，检查长度是否在有效范围内。

        Args:
            text: 原始文本

        Returns:
            str: 清理后的文本，无效时返回空字符串
        """
        if not text:
            return ""

        s = text.strip().replace("\u0000", "")

        # 去除首尾括号
        if s.startswith("(") and s.endswith(")"):
            s = s[1:-1].strip()

        # 长度检查
        if len(s) < MIN_TITLE_LENGTH or len(s) > MAX_TITLE_LENGTH:
            return ""

        return s

    def _score_line(self, text: str) -> float:
        """评估文本作为标题的可能性。

        使用多个因素综合评分，包括长度、字符类型、关键词等。

        Args:
            text: 候选文本

        Returns:
            float: 评分值，越高越可能是标题
        """
        score = 1.0

        # 长度因素
        length = len(text)
        if length < 6:
            score *= 0.3
        elif length > 80:
            score *= 0.7

        # 字符类型因素
        has_cjk = any("\u4e00" <= c <= "\u9fff" for c in text)
        has_alpha = any(c.isalpha() and c.isascii() for c in text)
        has_digit = any(c.isdigit() for c in text)

        if has_cjk:
            score *= 1.2
        if has_alpha:
            score *= 1.1
        if has_digit:
            score *= 1.05

        # 关键词加分
        if any(kw in text for kw in TITLE_KEYWORDS):
            score *= 1.3

        return score
