"""通用工具（v3），主要是日志相关"""

import logging
import os
from datetime import datetime
from typing import Tuple


def setup_logging_v3(prefix: str = "pdf_renamer_v3", force_new: bool = False) -> Tuple[logging.Logger, str]:
    """设置 v3 日志系统。

    返回 (logger, log_file_path)。
    """

    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    logs_dir = os.path.join(project_root, "logs")
    os.makedirs(logs_dir, exist_ok=True)

    today = datetime.now().strftime("%Y%m%d")
    log_file = os.path.join(logs_dir, f"{prefix}_{today}.log")

    logger = logging.getLogger(prefix)

    if logger.handlers and not force_new:
        return logger, log_file

    logger.handlers.clear()
    logger.setLevel(logging.INFO)

    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(logging.INFO)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    if force_new:
        logger.info(f"日志文件创建于: {log_file}")
        logger.info("日志系统初始化完成 (v3)")

    return logger, log_file
