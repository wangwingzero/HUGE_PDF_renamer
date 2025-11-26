#!/usr/bin/env python3
"""虎哥PDF重命名V3 独立启动脚本

放在项目根目录，方便直接运行 GUI：
    python run_pdf_renamer_v3.py
或：
    python d:/pdf_renamer/run_pdf_renamer_v3.py

内部会导入 main.pdf_renamer_v3 中的 main() 并启动界面。
"""

from __future__ import annotations

import sys
from pathlib import Path

# 确保项目根目录在 sys.path 中（通常已经在，但这里显式保证一次）
ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from main.pdf_renamer_v3 import main


if __name__ == "__main__":
    main()
