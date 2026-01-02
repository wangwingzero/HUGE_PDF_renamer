#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""虎哥PDF重命名 - GUI 主模块

使用 customtkinter 构建的现代化界面，提供文件选择、预览、
批量重命名等功能。

Copyright (c) 2024-2026 虎哥
Licensed under the MIT License.

Version: 1.0.0
"""

from __future__ import annotations

import threading
import time
import tkinter.messagebox as messagebox
from datetime import datetime
from pathlib import Path
from tkinter import filedialog
from typing import List, Optional, Tuple

import customtkinter as ctk

from .config import config_manager
from .file_processor import FileProcessor, RenameResult
from .i18n import i18n, I18nManager
from .utils import setup_logging

# ============================================================
# 应用常量
# ============================================================

APP_VERSION = "v1.0.0"
APP_AUTHOR = "虎哥"

# ============================================================
# 主题配色
# ============================================================

COLORS = {
    "primary": "#3B82F6",
    "primary_hover": "#2563EB",
    "success": "#10B981",
    "success_hover": "#0D9668",
    "warning": "#F59E0B",
    "error": "#EF4444",
    "error_hover": "#DC2626",
    "bg_dark": "#1E1E2E",
    "bg_card": "#2D2D3F",
    "bg_input": "#3D3D4F",
    "text": "#F8F8F2",
    "text_muted": "#A0A0B0",
    "border": "#4D4D5F",
}

# UI 常量
WINDOW_SIZE = "1100x750"
WINDOW_MIN_SIZE = (1000, 700)
ICON_FILENAME = "huge_icon.ico"


# ============================================================
# 主应用类
# ============================================================


class MainApp(ctk.CTk):
    """主应用窗口。

    基于 customtkinter 的现代化 GUI 界面，提供 PDF 批量重命名功能。

    Attributes:
        logger: 日志记录器
        processor: 文件处理器
        selected_files: 已选择的文件列表
        is_processing: 是否正在处理中
        cancel_requested: 是否请求取消
        i18n: 国际化管理器
    """

    def __init__(self) -> None:
        """初始化主应用窗口。"""
        super().__init__()
        self._init_i18n()
        self._setup_window()
        self._init_state()
        self._create_widgets()
        self.logger.info(f"{i18n.get('app.name')} {APP_VERSION} 启动")

    # --------------------------------------------------------
    # 初始化
    # --------------------------------------------------------

    def _init_i18n(self) -> None:
        """初始化国际化设置。"""
        # 从配置加载语言设置
        lang = config_manager.config.language
        i18n.set_language(lang)

    def _setup_window(self) -> None:
        """配置窗口属性。"""
        self.title(i18n.get("app.name"))
        self._set_icon()
        self.geometry(WINDOW_SIZE)
        self.minsize(*WINDOW_MIN_SIZE)

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        self.configure(fg_color=COLORS["bg_dark"])

    def _set_icon(self) -> None:
        """设置窗口图标。"""
        try:
            icon_path = Path(__file__).resolve().parent.parent / "resources" / ICON_FILENAME
            if icon_path.exists():
                self.wm_iconbitmap(icon_path)
        except Exception:
            pass

    def _init_state(self) -> None:
        """初始化应用状态。"""
        self.logger, _ = setup_logging()
        self.processor = FileProcessor(self.logger)
        self.selected_files: List[Path] = []
        self.is_processing = False
        self.cancel_requested = False
        self._pending_results: List[Tuple[int, RenameResult]] = []
        self._last_ui_update = 0.0

    # --------------------------------------------------------
    # UI 构建
    # --------------------------------------------------------

    def _create_widgets(self) -> None:
        """创建所有 UI 组件。"""
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        main_container = ctk.CTkFrame(self, fg_color="transparent")
        main_container.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        main_container.grid_columnconfigure(0, weight=1)
        main_container.grid_rowconfigure(1, weight=1)

        self._create_header(main_container)
        self._create_content(main_container)
        self._create_status_bar(main_container)

    def _create_header(self, parent: ctk.CTkFrame) -> None:
        """创建顶部标题栏。"""
        header = ctk.CTkFrame(
            parent, fg_color=COLORS["bg_card"], corner_radius=12, height=80
        )
        header.grid(row=0, column=0, sticky="ew")
        header.grid_propagate(False)
        header.grid_columnconfigure(1, weight=1)

        # 标题区域
        title_frame = ctk.CTkFrame(header, fg_color="transparent")
        title_frame.grid(row=0, column=0, padx=24, pady=20, sticky="w")

        ctk.CTkLabel(title_frame, text="🐯", font=ctk.CTkFont(size=36)).pack(
            side="left", padx=(0, 12)
        )

        title_text = ctk.CTkFrame(title_frame, fg_color="transparent")
        title_text.pack(side="left")

        ctk.CTkLabel(
            title_text,
            text=i18n.get("app.name"),
            font=ctk.CTkFont(family="Microsoft YaHei", size=24, weight="bold"),
            text_color=COLORS["text"],
        ).pack(anchor="w")

        ctk.CTkLabel(
            title_text,
            text=i18n.get("app.subtitle"),
            font=ctk.CTkFont(size=12),
            text_color=COLORS["text_muted"],
        ).pack(anchor="w")

        # 版本标签
        ctk.CTkLabel(
            header,
            text=APP_VERSION,
            font=ctk.CTkFont(size=12),
            text_color=COLORS["text_muted"],
            fg_color=COLORS["bg_input"],
            corner_radius=6,
            padx=8,
            pady=4,
        ).grid(row=0, column=1, padx=24, sticky="e")

    def _create_content(self, parent: ctk.CTkFrame) -> None:
        """创建主内容区域。"""
        content = ctk.CTkFrame(parent, fg_color="transparent")
        content.grid(row=1, column=0, sticky="nsew", pady=(16, 0))
        content.grid_columnconfigure(0, weight=2, uniform="panel")
        content.grid_columnconfigure(1, weight=1, uniform="panel")
        content.grid_rowconfigure(0, weight=1)

        self._create_file_panel(content)
        self._create_control_panel(content)

    def _create_file_panel(self, parent: ctk.CTkFrame) -> None:
        """创建左侧文件面板。"""
        panel = ctk.CTkFrame(parent, fg_color=COLORS["bg_card"], corner_radius=12)
        panel.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        panel.grid_columnconfigure(0, weight=1)
        panel.grid_rowconfigure(2, weight=1)

        # 标题行
        header = ctk.CTkFrame(panel, fg_color="transparent")
        header.grid(row=0, column=0, padx=20, pady=(20, 12), sticky="ew")

        ctk.CTkLabel(
            header,
            text=i18n.get("panel.files"),
            font=ctk.CTkFont(family="Microsoft YaHei", size=16, weight="bold"),
            text_color=COLORS["text"],
        ).pack(side="left")

        self.file_count_label = ctk.CTkLabel(
            header,
            text=i18n.get("panel.files.count", count=0),
            font=ctk.CTkFont(size=12),
            text_color=COLORS["text_muted"],
        )
        self.file_count_label.pack(side="right")

        # 按钮行
        self._create_file_buttons(panel)

        # 文件列表
        self.files_textbox = ctk.CTkTextbox(
            panel,
            fg_color=COLORS["bg_input"],
            text_color=COLORS["text"],
            font=ctk.CTkFont(family="Consolas", size=12),
            corner_radius=8,
            border_width=0,
            wrap="word",
        )
        self.files_textbox.grid(row=2, column=0, padx=20, pady=(0, 20), sticky="nsew")
        self.files_textbox.bind("<MouseWheel>", self._on_files_scroll)
        self._show_placeholder_text()

    def _create_file_buttons(self, panel: ctk.CTkFrame) -> None:
        """创建文件操作按钮。"""
        btn_frame = ctk.CTkFrame(panel, fg_color="transparent")
        btn_frame.grid(row=1, column=0, padx=20, pady=(0, 12), sticky="ew")

        ctk.CTkButton(
            btn_frame,
            text=i18n.get("btn.select_files"),
            command=self._select_files,
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_hover"],
            font=ctk.CTkFont(size=13),
            height=36,
            corner_radius=8,
        ).pack(side="left", padx=(0, 8))

        ctk.CTkButton(
            btn_frame,
            text=i18n.get("btn.select_folder"),
            command=self._select_folder,
            fg_color=COLORS["bg_input"],
            hover_color=COLORS["border"],
            font=ctk.CTkFont(size=13),
            height=36,
            corner_radius=8,
        ).pack(side="left", padx=(0, 8))

        ctk.CTkButton(
            btn_frame,
            text=i18n.get("btn.clear"),
            command=self._clear_files,
            fg_color="transparent",
            hover_color=COLORS["error"],
            border_width=1,
            border_color=COLORS["border"],
            font=ctk.CTkFont(size=13),
            height=36,
            width=80,
            corner_radius=8,
        ).pack(side="left")

    def _show_placeholder_text(self) -> None:
        """显示占位提示文字。"""
        self.files_textbox.insert(
            "1.0",
            i18n.get("panel.files.placeholder"),
        )
        self.files_textbox.configure(state="disabled", text_color=COLORS["text_muted"])

    def _on_files_scroll(self, event) -> None:
        """文件列表滚轮事件。"""
        self.files_textbox._textbox.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _on_log_scroll(self, event) -> None:
        """日志区域滚轮事件。"""
        self.log_text._textbox.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _create_control_panel(self, parent: ctk.CTkFrame) -> None:
        """创建右侧控制面板。"""
        panel = ctk.CTkFrame(parent, fg_color=COLORS["bg_card"], corner_radius=12)
        panel.grid(row=0, column=1, sticky="nsew")
        panel.grid_columnconfigure(0, weight=1)
        panel.grid_rowconfigure(0, weight=1)

        self.control_scrollable = ctk.CTkScrollableFrame(
            panel,
            fg_color="transparent",
            corner_radius=0,
        )
        self.control_scrollable.grid(row=0, column=0, sticky="nsew", padx=4, pady=4)
        self.control_scrollable.grid_columnconfigure(0, weight=1)

        self._create_mode_info(self.control_scrollable)
        self._create_settings(self.control_scrollable)
        self._create_action_buttons(self.control_scrollable)
        self._create_progress_area(self.control_scrollable)
        self._create_log_area(self.control_scrollable)

    def _create_mode_info(self, panel: ctk.CTkFrame) -> None:
        """创建模式说明区域。"""
        mode_frame = ctk.CTkFrame(panel, fg_color=COLORS["bg_input"], corner_radius=8)
        mode_frame.pack(fill="x", padx=16, pady=(16, 12))

        ctk.CTkLabel(
            mode_frame,
            text=i18n.get("mode.smart"),
            font=ctk.CTkFont(family="Microsoft YaHei", size=14, weight="bold"),
            text_color=COLORS["primary"],
        ).pack(padx=16, pady=(12, 4), anchor="w")

        ctk.CTkLabel(
            mode_frame,
            text=i18n.get("mode.smart.desc"),
            font=ctk.CTkFont(size=11),
            text_color=COLORS["text_muted"],
            justify="left",
        ).pack(padx=16, pady=(0, 12), anchor="w")

    def _create_settings(self, panel: ctk.CTkFrame) -> None:
        """创建设置区域。"""
        settings_frame = ctk.CTkFrame(panel, fg_color="transparent")
        settings_frame.pack(fill="x", padx=16, pady=(0, 12))

        ctk.CTkLabel(
            settings_frame,
            text=i18n.get("settings.title"),
            font=ctk.CTkFont(family="Microsoft YaHei", size=14, weight="bold"),
            text_color=COLORS["text"],
        ).pack(anchor="w", pady=(0, 12))

        cfg = config_manager.config

        # 最大文件名长度
        len_row = ctk.CTkFrame(settings_frame, fg_color="transparent")
        len_row.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(
            len_row,
            text=i18n.get("settings.max_length"),
            font=ctk.CTkFont(size=12),
            text_color=COLORS["text"],
        ).pack(side="left")

        self.max_len_var = ctk.StringVar(value=str(cfg.max_filename_length))
        ctk.CTkEntry(
            len_row,
            textvariable=self.max_len_var,
            width=70,
            height=32,
            fg_color=COLORS["bg_input"],
            border_color=COLORS["border"],
            corner_radius=6,
        ).pack(side="right")

        # 复选框选项
        self.backup_var = ctk.BooleanVar(value=cfg.auto_backup)
        self.parallel_var = ctk.BooleanVar(value=cfg.parallel_processing)
        self.ts_var = ctk.BooleanVar(value=cfg.add_timestamp)

        checkboxes = [
            (i18n.get("settings.backup"), self.backup_var),
            (i18n.get("settings.parallel"), self.parallel_var),
            (i18n.get("settings.timestamp"), self.ts_var),
        ]

        for text, var in checkboxes:
            ctk.CTkCheckBox(
                settings_frame,
                text=text,
                variable=var,
                font=ctk.CTkFont(size=12),
                text_color=COLORS["text"],
                fg_color=COLORS["primary"],
                hover_color=COLORS["primary_hover"],
                border_color=COLORS["border"],
                corner_radius=4,
            ).pack(anchor="w", pady=4)

        # 语言选择
        self._create_language_selector(settings_frame)

    def _create_language_selector(self, parent: ctk.CTkFrame) -> None:
        """创建语言选择下拉框。"""
        lang_row = ctk.CTkFrame(parent, fg_color="transparent")
        lang_row.pack(fill="x", pady=(8, 4))

        ctk.CTkLabel(
            lang_row,
            text=i18n.get("settings.language"),
            font=ctk.CTkFont(size=12),
            text_color=COLORS["text"],
        ).pack(side="left")

        # 获取可用语言列表
        languages = i18n.get_available_languages()
        lang_names = [name for _, name in languages]
        lang_codes = [code for code, _ in languages]

        # 当前语言
        current_lang = config_manager.config.language
        current_name = i18n.get_language_display_name(current_lang)

        self.lang_var = ctk.StringVar(value=current_name)
        self.lang_menu = ctk.CTkOptionMenu(
            lang_row,
            variable=self.lang_var,
            values=lang_names,
            command=self._on_language_change,
            fg_color=COLORS["bg_input"],
            button_color=COLORS["primary"],
            button_hover_color=COLORS["primary_hover"],
            dropdown_fg_color=COLORS["bg_card"],
            dropdown_hover_color=COLORS["bg_input"],
            font=ctk.CTkFont(size=12),
            width=100,
            height=32,
            corner_radius=6,
        )
        self.lang_menu.pack(side="right")

        # 保存语言代码映射
        self._lang_code_map = dict(zip(lang_names, lang_codes))

    def _on_language_change(self, selected_name: str) -> None:
        """语言切换回调。"""
        lang_code = self._lang_code_map.get(selected_name, "zh_CN")

        # 保存到配置
        config_manager.update_config(language=lang_code)

        # 切换语言
        i18n.set_language(lang_code)

        # 显示重启提示
        messagebox.showinfo(
            i18n.get("dialog.info"),
            i18n.get("settings.language.restart_hint")
        )

    def _create_action_buttons(self, panel: ctk.CTkFrame) -> None:
        """创建操作按钮区域。"""
        action_frame = ctk.CTkFrame(panel, fg_color="transparent")
        action_frame.pack(fill="x", padx=16, pady=(8, 16))

        self.preview_btn = ctk.CTkButton(
            action_frame,
            text=i18n.get("btn.preview"),
            command=self._preview,
            fg_color=COLORS["bg_input"],
            hover_color=COLORS["border"],
            font=ctk.CTkFont(size=14),
            height=44,
            corner_radius=8,
            state="disabled",
        )
        self.preview_btn.pack(fill="x", pady=(0, 8))

        self.start_btn = ctk.CTkButton(
            action_frame,
            text=i18n.get("btn.start"),
            command=self._start,
            fg_color=COLORS["success"],
            hover_color=COLORS["success_hover"],
            font=ctk.CTkFont(size=15, weight="bold"),
            height=50,
            corner_radius=8,
            state="disabled",
        )
        self.start_btn.pack(fill="x", pady=(0, 8))

        self.cancel_btn = ctk.CTkButton(
            action_frame,
            text=i18n.get("btn.cancel"),
            command=self._cancel_processing,
            fg_color=COLORS["error"],
            hover_color=COLORS["error_hover"],
            font=ctk.CTkFont(size=14),
            height=44,
            corner_radius=8,
            state="disabled",
        )
        self.cancel_btn.pack(fill="x")

    def _create_progress_area(self, panel: ctk.CTkFrame) -> None:
        """创建进度区域。"""
        progress_frame = ctk.CTkFrame(
            panel, fg_color=COLORS["bg_input"], corner_radius=8
        )
        progress_frame.pack(fill="x", padx=16, pady=(0, 16))

        self.progress_label = ctk.CTkLabel(
            progress_frame,
            text=i18n.get("progress.ready"),
            font=ctk.CTkFont(size=12),
            text_color=COLORS["text"],
        )
        self.progress_label.pack(padx=16, pady=(12, 8), anchor="w")

        self.progress_bar = ctk.CTkProgressBar(
            progress_frame,
            fg_color=COLORS["bg_dark"],
            progress_color=COLORS["primary"],
            height=8,
            corner_radius=4,
        )
        self.progress_bar.pack(padx=16, pady=(0, 8), fill="x")
        self.progress_bar.set(0)

        self.current_file_label = ctk.CTkLabel(
            progress_frame,
            text="",
            font=ctk.CTkFont(size=11),
            text_color=COLORS["text_muted"],
        )
        self.current_file_label.pack(padx=16, pady=(0, 12), anchor="w")

    def _create_log_area(self, panel: ctk.CTkFrame) -> None:
        """创建日志区域。"""
        log_frame = ctk.CTkFrame(panel, fg_color="transparent")
        log_frame.pack(fill="x", padx=16, pady=(0, 16))

        ctk.CTkLabel(
            log_frame,
            text=i18n.get("log.title"),
            font=ctk.CTkFont(family="Microsoft YaHei", size=12, weight="bold"),
            text_color=COLORS["text"],
        ).pack(anchor="w", pady=(0, 8))

        self.log_text = ctk.CTkTextbox(
            log_frame,
            fg_color=COLORS["bg_input"],
            text_color=COLORS["text_muted"],
            font=ctk.CTkFont(family="Consolas", size=11),
            corner_radius=8,
            height=150,
            wrap="word",
        )
        self.log_text.pack(fill="x")
        self.log_text.bind("<MouseWheel>", self._on_log_scroll)

    def _create_status_bar(self, parent: ctk.CTkFrame) -> None:
        """创建底部状态栏。"""
        status_bar = ctk.CTkFrame(
            parent, fg_color=COLORS["bg_card"], corner_radius=8, height=40
        )
        status_bar.grid(row=2, column=0, sticky="ew", pady=(16, 0))
        status_bar.grid_propagate(False)

        self.status_label = ctk.CTkLabel(
            status_bar,
            text=i18n.get("status.ready"),
            font=ctk.CTkFont(size=12),
            text_color=COLORS["text_muted"],
        )
        self.status_label.pack(side="left", padx=16, pady=10)

        ctk.CTkLabel(
            status_bar,
            text=i18n.get("footer.author", author=APP_AUTHOR),
            font=ctk.CTkFont(size=11),
            text_color=COLORS["text_muted"],
        ).pack(side="right", padx=16, pady=10)

    # --------------------------------------------------------
    # 文件选择
    # --------------------------------------------------------

    def _select_files(self) -> None:
        """选择 PDF 文件。"""
        paths = filedialog.askopenfilenames(
            title=i18n.get("dialog.select_pdf_files"),
            filetypes=[
                (i18n.get("dialog.pdf_files"), "*.pdf"),
                (i18n.get("dialog.all_files"), "*.*"),
            ],
        )
        if paths:
            self.selected_files.extend(Path(p) for p in paths)
            self._refresh_file_list()

    def _select_folder(self) -> None:
        """选择文件夹。"""
        folder = filedialog.askdirectory(title=i18n.get("dialog.select_folder"))
        if folder:
            pdfs = list(Path(folder).glob("*.pdf"))
            self.selected_files.extend(pdfs)
            self._refresh_file_list()

    def _clear_files(self) -> None:
        """清空文件列表。"""
        self.selected_files.clear()
        self._refresh_file_list()

    def _refresh_file_list(self) -> None:
        """刷新文件列表显示。"""
        self.files_textbox.configure(state="normal", text_color=COLORS["text"])
        self.files_textbox.delete("1.0", "end")

        if not self.selected_files:
            self._show_placeholder_text()
        else:
            for i, p in enumerate(self.selected_files, 1):
                try:
                    size_mb = p.stat().st_size / 1024 / 1024
                    self.files_textbox.insert(
                        "end", f"{i:3d}. {p.name}  ({size_mb:.1f} MB)\n"
                    )
                except OSError:
                    self.files_textbox.insert(
                        "end",
                        f"{i:3d}. {p.name}  ({i18n.get('panel.files.unreadable')})\n"
                    )
            self.files_textbox.configure(state="disabled")

        count = len(self.selected_files)
        self.file_count_label.configure(text=i18n.get("panel.files.count", count=count))

        state = "normal" if count > 0 else "disabled"
        self.preview_btn.configure(state=state)
        self.start_btn.configure(state=state)

        if count > 0:
            self.status_label.configure(
                text=i18n.get("status.selected", count=count)
            )

    # --------------------------------------------------------
    # 设置与处理
    # --------------------------------------------------------

    def _apply_settings(self) -> None:
        """应用当前设置。"""
        try:
            max_len = int(self.max_len_var.get())
        except ValueError:
            messagebox.showerror(
                i18n.get("dialog.error"),
                i18n.get("dialog.max_length_error")
            )
            return

        config_manager.update_config(
            max_filename_length=max_len,
            auto_backup=self.backup_var.get(),
            parallel_processing=self.parallel_var.get(),
            add_timestamp=self.ts_var.get(),
        )

    def _preview(self) -> None:
        """预览重命名结果。"""
        if not self.selected_files:
            messagebox.showwarning(
                i18n.get("dialog.warning"),
                i18n.get("dialog.select_files_first")
            )
            return

        self._apply_settings()
        self.status_label.configure(text=i18n.get("status.generating_preview"))
        self._log(i18n.get("log.preview_start"))

        def worker() -> None:
            try:
                results, _ = self.processor.process_files(self.selected_files)
                self.after(0, lambda: self._show_preview_results(results))
            except Exception as e:
                self.after(0, lambda: self._log(i18n.get("log.preview_failed", error=str(e))))

        threading.Thread(target=worker, daemon=True).start()

    def _show_preview_results(self, results: List[RenameResult]) -> None:
        """显示预览结果。"""
        ok = sum(1 for r in results if r.success)
        total = len(results)

        self._log(f"\n{'='*40}")
        self._log(i18n.get("log.preview_result", success=ok, total=total))
        self._log(f"{'='*40}")

        for r in results:
            if r.success and r.new_path is not None:
                self._log(f"✅ {r.original_path.name}")
                self._log(f"   → {r.new_path.name}")
            else:
                self._log(f"❌ {r.original_path.name}")
                self._log(f"   {i18n.get('log.reason', reason=r.error_message)}")

        self.status_label.configure(
            text=i18n.get("status.preview_done", success=ok, total=total)
        )

    def _cancel_processing(self) -> None:
        """取消处理。"""
        self.cancel_requested = True
        self.cancel_btn.configure(state="disabled", text=i18n.get("btn.cancel.cancelling"))
        self._log(i18n.get("log.cancel_requested"))

    def _start(self) -> None:
        """开始处理。"""
        if not self.selected_files or self.is_processing:
            return

        self._apply_settings()
        self._prepare_processing()

        total = len(self.selected_files)
        self._log(f"\n{'='*40}")
        self._log(i18n.get("log.process_start", count=total))
        self._log(f"{'='*40}")

        def progress_callback(
            current: int, total_files: int, current_file: Path, result: RenameResult
        ) -> None:
            if self.cancel_requested:
                return
            progress = current / max(total_files, 1)
            self.after(
                0,
                lambda: self._on_progress(
                    current, total_files, current_file, progress, result
                ),
            )

        def worker() -> None:
            try:
                results, stats = self.processor.process_files(
                    self.selected_files,
                    progress_callback=progress_callback,
                    cancel_check=lambda: self.cancel_requested,
                )
                self.after(0, self._flush_pending_results)
                self.after(0, lambda: self._on_done(results, stats))
            except Exception as e:
                self.after(0, lambda: self._log(i18n.get("log.process_failed", error=str(e))))
                self.after(0, self._reset_ui)

        threading.Thread(target=worker, daemon=True).start()

    def _prepare_processing(self) -> None:
        """准备处理状态。"""
        self.is_processing = True
        self.cancel_requested = False
        self._pending_results = []
        self._last_ui_update = 0

        self.files_textbox.configure(state="normal", text_color=COLORS["text"])
        self.files_textbox.delete("1.0", "end")
        self.files_textbox.configure(state="disabled")

        total = len(self.selected_files)
        self.progress_bar.set(0)
        self.progress_label.configure(text=i18n.get("progress.starting"))
        self.start_btn.configure(state="disabled", text=i18n.get("btn.start.processing"))
        self.preview_btn.configure(state="disabled")
        self.cancel_btn.configure(state="normal", text=i18n.get("btn.cancel"))
        self.status_label.configure(text=i18n.get("status.processing", count=total))

    def _on_progress(
        self,
        current: int,
        total: int,
        current_file: Path,
        progress: float,
        result: RenameResult,
    ) -> None:
        """处理进度回调。"""
        self.progress_bar.set(progress)
        self.progress_label.configure(
            text=i18n.get("progress.processing", current=current, total=total)
        )

        name = current_file.name
        display_name = name[:50] + "..." if len(name) > 50 else name
        self.current_file_label.configure(text=display_name)

        self._pending_results.append((current, result))

        now = time.time()
        if now - self._last_ui_update > 0.3 or len(self._pending_results) >= 50:
            self._flush_pending_results()
            self._last_ui_update = now

    def _flush_pending_results(self) -> None:
        """批量刷新待显示的结果。"""
        if not self._pending_results:
            return

        self.files_textbox.configure(state="normal")

        for index, result in self._pending_results:
            old_name = result.original_path.name
            if result.success and result.new_path is not None:
                new_name = result.new_path.name
                if old_name != new_name:
                    self.files_textbox.insert("end", f"{index:3d}. ✅ {old_name}\n")
                    self.files_textbox.insert("end", f"     → {new_name}\n")
                else:
                    self.files_textbox.insert(
                        "end",
                        f"{index:3d}. ✅ {old_name} ({i18n.get('log.no_change')})\n"
                    )
            else:
                self.files_textbox.insert("end", f"{index:3d}. ❌ {old_name}\n")
                if result.error_message:
                    self.files_textbox.insert(
                        "end",
                        f"     {i18n.get('log.reason', reason=result.error_message)}\n"
                    )

        self.files_textbox.see("end")
        self.files_textbox.configure(state="disabled")
        self._pending_results.clear()

    def _on_done(self, results: List[RenameResult], stats) -> None:
        """处理完成回调。"""
        ok = sum(1 for r in results if r.success)
        total = len(results)
        was_cancelled = self.cancel_requested
        rate = stats.success_rate * 100

        self.progress_bar.set(1.0)
        self.progress_label.configure(
            text=i18n.get("progress.done", success=ok, total=total)
        )
        self.current_file_label.configure(text="")

        if was_cancelled:
            self._log(f"\n{i18n.get('log.process_cancelled')}")
            self._log(f"   {i18n.get('log.processed_count', count=total)}")
            self._log(f"   {i18n.get('log.success_count', success=ok, rate=f'{rate:.1f}')}")
            self.status_label.configure(
                text=i18n.get("status.cancelled", total=total, success=ok)
            )
        else:
            emoji = "🎉" if rate >= 90 else ("✅" if rate >= 70 else "⚠️")
            self._log(f"\n{i18n.get('log.process_done', emoji=emoji)}")
            self._log(f"   {i18n.get('log.success_count', success=ok, rate=f'{rate:.1f}')} / {total}")
            self._log(f"   {i18n.get('log.duration', time=f'{stats.duration:.1f}')}")
            self.status_label.configure(
                text=i18n.get("status.done", emoji=emoji, success=ok, total=total, time=f"{stats.duration:.1f}")
            )

        self._reset_ui()

    def _reset_ui(self) -> None:
        """重置 UI 状态。"""
        self.is_processing = False
        self.cancel_requested = False
        self.start_btn.configure(state="normal", text=i18n.get("btn.start"))
        self.preview_btn.configure(
            state="normal" if self.selected_files else "disabled"
        )
        self.cancel_btn.configure(state="disabled", text=i18n.get("btn.cancel"))

    def _log(self, msg: str) -> None:
        """写入日志。"""
        ts = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert("end", f"[{ts}] {msg}\n")
        self.log_text.see("end")


# ============================================================
# 入口函数
# ============================================================


def main() -> None:
    """应用入口。"""
    app = MainApp()
    app.mainloop()


if __name__ == "__main__":
    main()
