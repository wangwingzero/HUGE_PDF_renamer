"""
Smart text extractor for PDF Renamer v3.

设计目标：
- 先从 PDF 元数据中快速获取标题（使用 pypdf）；
- 失败时只分析前几页文本，避免整本扫描；
- 大文件优先走快速逻辑，小文件可以尝试稍微精细一点；
- 对外只暴露一个统一方法：extract_title(path) -> Optional[ExtractedText]。

注意：本模块复用 v2 中的 ExtractedText 数据结构，避免重复定义。
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional, List, Tuple
from dataclasses import dataclass

import logging


@dataclass
class ExtractedText:
    """v3 用到的提取结果结构，字段与 v2 保持兼容"""

    text: str
    confidence: float  # 0-1，置信度
    strategy: str
    position: Tuple[float, float]
    font_size: float

try:
    from pypdf import PdfReader
except Exception:  # pragma: no cover - 运行时缺失依赖时给出日志
    PdfReader = None  # type: ignore

try:
    import pdfplumber
except Exception:  # pragma: no cover
    pdfplumber = None  # type: ignore


class SmartTextExtractorV3:
    """针对 v3 的智能标题提取器。

    优先顺序：
    1. PDF 元数据（Title）；
    2. 前几页文本的行标题（仅少量启发式，避免复杂耗时分析）；
    """

    def __init__(self, logger: Optional[logging.Logger] = None) -> None:
        self.logger = logger or logging.getLogger(__name__)

    # === 对外主入口 ===

    def extract_title(self, pdf_path: Path) -> Optional[ExtractedText]:
        """综合使用多种方式提取标题。

        返回 ExtractedText，如果完全失败则返回 None。
        """
        # 1. 元数据
        title = self._extract_from_metadata(pdf_path)
        if title:
            return ExtractedText(
                text=title,
                confidence=0.9,
                strategy="metadata_v3",
                position=(0.0, 0.0),
                font_size=0.0,
            )

        # 2. 前几页快速扫描
        title2 = self._extract_from_first_pages(pdf_path, max_pages=2)
        if title2:
            return ExtractedText(
                text=title2,
                confidence=0.8,
                strategy="first_pages_v3",
                position=(0.0, 0.0),
                font_size=0.0,
            )

        return None

    # === 具体策略实现 ===

    def _extract_from_metadata(self, pdf_path: Path) -> Optional[str]:
        if PdfReader is None:
            return None

        try:
            reader = PdfReader(str(pdf_path))
            # 先尝试 XMP / metadata，再退回 documentInfo
            meta = getattr(reader, "metadata", None)
            info = getattr(reader, "documentInfo", None)

            candidates: List[str] = []
            if meta is not None:
                title = getattr(meta, "title", None)
                if isinstance(title, str):
                    candidates.append(title)
            if info is not None:
                raw_title = getattr(info, "title", None)
                if isinstance(raw_title, str):
                    candidates.append(raw_title)

            for raw in candidates:
                cleaned = self._clean_candidate(raw)
                if cleaned:
                    self.logger.info(f"v3: 使用元数据标题: {cleaned}")
                    return cleaned
        except Exception as e:
            self.logger.debug(f"v3: 读取元数据失败: {e}")

        return None

    def _extract_from_first_pages(self, pdf_path: Path, max_pages: int = 2) -> Optional[str]:
        if pdfplumber is None:
            return None

        try:
            with pdfplumber.open(str(pdf_path)) as pdf:
                pages = pdf.pages[:max_pages]
                best_line = None
                best_score = 0.0

                for page in pages:
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
                    self.logger.info(f"v3: 从前几页识别标题: {best_line}")
                    return best_line
        except Exception as e:
            self.logger.warning(f"v3: 从前几页提取标题失败: {e}")

        return None

    # === 文本清理与评分 ===

    def _clean_candidate(self, text: str) -> str:
        if not text:
            return ""

        s = text.strip().replace("\u0000", "")
        # 去除首尾括号
        if s.startswith("(") and s.endswith(")"):
            s = s[1:-1].strip()

        # 长度约束
        if len(s) < 4 or len(s) > 120:
            return ""

        return s

    def _score_line(self, text: str) -> float:
        """简单打分：综合中英文、数字、关键词等。"""
        score = 1.0

        # 太短或太长降分
        if len(text) < 6:
            score *= 0.3
        elif len(text) > 80:
            score *= 0.7

        has_digit = any(c.isdigit() for c in text)
        has_alpha = any("A" <= c <= "Z" or "a" <= c <= "z" for c in text)
        has_cjk = any("\u4e00" <= c <= "\u9fff" for c in text)

        if has_cjk:
            score *= 1.2
        if has_alpha:
            score *= 1.1
        if has_digit:
            score *= 1.05

        # 常见关键词加分
        keywords = [
            "飞行手册",
            "操作手册",
            "操作程序",
            "技术通告",
            "Flight Manual",
            "Manual",
            "AFM",
        ]
        if any(k in text for k in keywords):
            score *= 1.3

        return score
