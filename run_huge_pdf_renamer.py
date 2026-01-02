#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""虎哥PDF重命名 - 启动脚本

独立启动脚本，放在项目根目录，方便直接运行 GUI。

使用方法:
    python run_tiger_pdf_renamer.py

或者直接双击运行（Windows）。

Copyright (c) 2024-2026 虎哥
Licensed under the MIT License.

Version: 1.0.0
"""

from __future__ import annotations

import sys
from pathlib import Path

# 确保项目根目录在 sys.path 中
ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from main.pdf_renamer import main


if __name__ == "__main__":
    main()
