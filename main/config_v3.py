"""配置管理（v3）"""

import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict


@dataclass
class RenameConfigV3:
    """v3 版本的重命名配置（精简版）"""

    max_filename_length: int = 120
    add_timestamp: bool = False
    auto_backup: bool = False
    parallel_processing: bool = True
    max_workers: int = 4


class ConfigManagerV3:
    """配置管理器（v3）"""

    def __init__(self) -> None:
        base_dir = Path(__file__).resolve().parent.parent
        self.config_file = base_dir / "config_v3.json"
        self.config = self.load_config()

    def load_config(self) -> RenameConfigV3:
        if self.config_file.exists():
            try:
                with open(self.config_file, "r", encoding="utf-8") as f:
                    data: Dict[str, Any] = json.load(f)
                return RenameConfigV3(**data)
            except Exception:
                pass
        return RenameConfigV3()

    def save_config(self) -> bool:
        try:
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(asdict(self.config), f, ensure_ascii=False, indent=2)
            return True
        except Exception:
            return False

    def update_config(self, **kwargs: Any) -> bool:
        try:
            for key, value in kwargs.items():
                if hasattr(self.config, key):
                    setattr(self.config, key, value)
            return self.save_config()
        except Exception:
            return False


config_manager_v3 = ConfigManagerV3()
