#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""通用工具模块

提供日志配置等基础功能，支持日志文件按日期轮转。

Copyright (c) 2024-2026 虎哥
Licensed under the MIT License.

Version: 1.0.0
"""

from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path
from typing import Tuple

# 日志配置常量
LOG_DIR_NAME = "logs"
LOG_PREFIX = "tiger_pdf_renamer"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def setup_logging(
    prefix: str = LOG_PREFIX,
    force_new: bool = False,
) -> Tuple[logging.Logger, str]:
    """设置日志系统。

    配置文件日志和控制台日志，日志文件按日期命名，存放在项目根目录的 logs/ 文件夹中。

    Args:
        prefix: 日志文件名前缀，默认为 "tiger_pdf_renamer"
        force_new: 是否强制创建新的日志处理器，默认为 False

    Returns:
        Tuple[logging.Logger, str]: (logger 实例, 日志文件路径) 元组

    Example:
        >>> logger, log_path = setup_logging()
        >>> logger.info("应用启动")
    """
    project_root = Path(__file__).resolve().parent.parent
    logs_dir = project_root / LOG_DIR_NAME
    logs_dir.mkdir(exist_ok=True)

    today = datetime.now().strftime("%Y%m%d")
    log_file = logs_dir / f"{prefix}_{today}.log"

    logger = logging.getLogger(prefix)

    # 如果已有处理器且不强制刷新，直接返回
    if logger.handlers and not force_new:
        return logger, str(log_file)

    # 清理旧处理器并重新配置
    logger.handlers.clear()
    logger.setLevel(logging.INFO)

    formatter = logging.Formatter(LOG_FORMAT, datefmt=LOG_DATE_FORMAT)

    # 文件处理器
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # 控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    if force_new:
        logger.info(f"日志文件: {log_file}")
        logger.info("日志系统初始化完成")

    return logger, str(log_file)
