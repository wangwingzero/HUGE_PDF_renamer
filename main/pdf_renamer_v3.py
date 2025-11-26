#!/usr/bin/env python3
"""PDF Renamer v3 - 现代 GUI 入口

使用 customtkinter 构建的简洁界面，只保留一个智能模式：
- 自动根据 PDF 元数据和前几页内容提取标题；
- 自动处理文件名清理、重名、备份；
- 用户只需要选择文件/文件夹并点击开始处理。

运行方式（推荐）：
    python -m main.pdf_renamer_v3
或：
    python run_pdf_renamer_v3.py
"""

from __future__ import annotations

from pathlib import Path
from typing import List
from datetime import datetime

import threading
import tkinter.messagebox as messagebox

import customtkinter as ctk

from .config_v3 import config_manager_v3
from .file_processor_v3 import FileProcessorV3
from .utils_v3 import setup_logging_v3


# 配色方案
COLORS = {
    "primary": "#3B82F6",       # 蓝色主色
    "primary_hover": "#2563EB",
    "success": "#10B981",       # 绿色
    "warning": "#F59E0B",       # 橙色
    "error": "#EF4444",         # 红色
    "bg_dark": "#1E1E2E",       # 深色背景
    "bg_card": "#2D2D3F",       # 卡片背景
    "bg_input": "#3D3D4F",      # 输入框背景
    "text": "#F8F8F2",          # 主文字
    "text_muted": "#A0A0B0",    # 次要文字
    "border": "#4D4D5F",        # 边框
}


class MainAppV3(ctk.CTk):
    def __init__(self) -> None:
        super().__init__()

        # 窗口标题与图标
        self.title("虎哥PDF重命名V3")
        try:
            icon_path = Path(__file__).resolve().parent.parent / "虎哥图标.ico"
            if icon_path.exists():
                self.wm_iconbitmap(icon_path)
        except Exception:
            pass

        self.geometry("1100x750")
        self.minsize(1000, 700)

        # 设置深色主题
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # 配置窗口背景色
        self.configure(fg_color=COLORS["bg_dark"])

        self.logger, _ = setup_logging_v3()
        self.processor = FileProcessorV3(self.logger)
        self.selected_files: List[Path] = []
        self.is_processing = False

        self._create_widgets()

        self.logger.info("虎哥PDF重命名V3 启动")

    def _create_widgets(self) -> None:
        # 主容器
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        main_container = ctk.CTkFrame(self, fg_color="transparent")
        main_container.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        main_container.grid_columnconfigure(0, weight=1)
        main_container.grid_rowconfigure(1, weight=1)

        # === 顶部标题栏 ===
        self._create_header(main_container)

        # === 主内容区域 ===
        content_frame = ctk.CTkFrame(main_container, fg_color="transparent")
        content_frame.grid(row=1, column=0, sticky="nsew", pady=(16, 0))
        content_frame.grid_columnconfigure(0, weight=2)
        content_frame.grid_columnconfigure(1, weight=1)
        content_frame.grid_rowconfigure(0, weight=1)

        # 左侧：文件列表
        self._create_file_panel(content_frame)

        # 右侧：设置和操作
        self._create_control_panel(content_frame)

        # === 底部状态栏 ===
        self._create_status_bar(main_container)

    def _create_header(self, parent) -> None:
        """顶部标题栏"""
        header = ctk.CTkFrame(parent, fg_color=COLORS["bg_card"], corner_radius=12, height=80)
        header.grid(row=0, column=0, sticky="ew")
        header.grid_propagate(False)
        header.grid_columnconfigure(1, weight=1)

        # 图标 + 标题
        title_frame = ctk.CTkFrame(header, fg_color="transparent")
        title_frame.grid(row=0, column=0, padx=24, pady=20, sticky="w")

        ctk.CTkLabel(
            title_frame,
            text="🐯",
            font=ctk.CTkFont(size=36),
        ).pack(side="left", padx=(0, 12))

        title_text = ctk.CTkFrame(title_frame, fg_color="transparent")
        title_text.pack(side="left")

        ctk.CTkLabel(
            title_text,
            text="虎哥PDF重命名",
            font=ctk.CTkFont(family="Microsoft YaHei", size=24, weight="bold"),
            text_color=COLORS["text"],
        ).pack(anchor="w")

        ctk.CTkLabel(
            title_text,
            text="智能识别 · 批量处理 · 一键重命名",
            font=ctk.CTkFont(size=12),
            text_color=COLORS["text_muted"],
        ).pack(anchor="w")

        # 版本标签
        ctk.CTkLabel(
            header,
            text="v3.0",
            font=ctk.CTkFont(size=12),
            text_color=COLORS["text_muted"],
            fg_color=COLORS["bg_input"],
            corner_radius=6,
            padx=8,
            pady=4,
        ).grid(row=0, column=1, padx=24, sticky="e")

    def _create_file_panel(self, parent) -> None:
        """左侧文件面板"""
        panel = ctk.CTkFrame(parent, fg_color=COLORS["bg_card"], corner_radius=12)
        panel.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        panel.grid_columnconfigure(0, weight=1)
        panel.grid_rowconfigure(2, weight=1)

        # 标题
        header = ctk.CTkFrame(panel, fg_color="transparent")
        header.grid(row=0, column=0, padx=20, pady=(20, 12), sticky="ew")

        ctk.CTkLabel(
            header,
            text="📁 文件列表",
            font=ctk.CTkFont(family="Microsoft YaHei", size=16, weight="bold"),
            text_color=COLORS["text"],
        ).pack(side="left")

        self.file_count_label = ctk.CTkLabel(
            header,
            text="0 个文件",
            font=ctk.CTkFont(size=12),
            text_color=COLORS["text_muted"],
        )
        self.file_count_label.pack(side="right")

        # 按钮行
        btn_frame = ctk.CTkFrame(panel, fg_color="transparent")
        btn_frame.grid(row=1, column=0, padx=20, pady=(0, 12), sticky="ew")

        ctk.CTkButton(
            btn_frame,
            text="📄 选择文件",
            command=self._select_files,
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_hover"],
            font=ctk.CTkFont(size=13),
            height=36,
            corner_radius=8,
        ).pack(side="left", padx=(0, 8))

        ctk.CTkButton(
            btn_frame,
            text="📂 选择文件夹",
            command=self._select_folder,
            fg_color=COLORS["bg_input"],
            hover_color=COLORS["border"],
            font=ctk.CTkFont(size=13),
            height=36,
            corner_radius=8,
        ).pack(side="left", padx=(0, 8))

        ctk.CTkButton(
            btn_frame,
            text="🗑️ 清空",
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

        # 文件列表
        self.files_textbox = ctk.CTkTextbox(
            panel,
            fg_color=COLORS["bg_input"],
            text_color=COLORS["text"],
            font=ctk.CTkFont(family="Consolas", size=12),
            corner_radius=8,
            border_width=0,
        )
        self.files_textbox.grid(row=2, column=0, padx=20, pady=(0, 20), sticky="nsew")

        # 提示文字
        self.files_textbox.insert("1.0", "将 PDF 文件拖放到此处，或点击上方按钮选择文件...\n\n支持批量处理，智能识别文件标题。")
        self.files_textbox.configure(state="disabled", text_color=COLORS["text_muted"])

    def _create_control_panel(self, parent) -> None:
        """右侧控制面板"""
        panel = ctk.CTkFrame(parent, fg_color=COLORS["bg_card"], corner_radius=12)
        panel.grid(row=0, column=1, sticky="nsew")
        panel.grid_columnconfigure(0, weight=1)

        # === 智能模式说明 ===
        mode_frame = ctk.CTkFrame(panel, fg_color=COLORS["bg_input"], corner_radius=8)
        mode_frame.grid(row=0, column=0, padx=20, pady=(20, 16), sticky="ew")

        ctk.CTkLabel(
            mode_frame,
            text="🧠 智能提取模式",
            font=ctk.CTkFont(family="Microsoft YaHei", size=14, weight="bold"),
            text_color=COLORS["primary"],
        ).pack(padx=16, pady=(12, 4), anchor="w")

        ctk.CTkLabel(
            mode_frame,
            text="自动识别 PDF 元数据和首页内容\n小文件精细分析，大文件快速处理",
            font=ctk.CTkFont(size=11),
            text_color=COLORS["text_muted"],
            justify="left",
        ).pack(padx=16, pady=(0, 12), anchor="w")

        # === 设置选项 ===
        settings_frame = ctk.CTkFrame(panel, fg_color="transparent")
        settings_frame.grid(row=1, column=0, padx=20, pady=(0, 16), sticky="ew")

        ctk.CTkLabel(
            settings_frame,
            text="⚙️ 设置",
            font=ctk.CTkFont(family="Microsoft YaHei", size=14, weight="bold"),
            text_color=COLORS["text"],
        ).pack(anchor="w", pady=(0, 12))

        cfg = config_manager_v3.config

        # 最大文件名长度
        len_row = ctk.CTkFrame(settings_frame, fg_color="transparent")
        len_row.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(
            len_row,
            text="最大文件名长度",
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

        for text, var in [
            ("📦 自动备份原文件", self.backup_var),
            ("⚡ 并行处理（更快）", self.parallel_var),
            ("🕐 添加时间戳后缀", self.ts_var),
        ]:
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

        # === 操作按钮 ===
        action_frame = ctk.CTkFrame(panel, fg_color="transparent")
        action_frame.grid(row=2, column=0, padx=20, pady=(8, 20), sticky="ew")

        self.preview_btn = ctk.CTkButton(
            action_frame,
            text="👁️ 预览",
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
            text="🚀 开始处理",
            command=self._start,
            fg_color=COLORS["success"],
            hover_color="#0D9668",
            font=ctk.CTkFont(size=15, weight="bold"),
            height=50,
            corner_radius=8,
            state="disabled",
        )
        self.start_btn.pack(fill="x")

        # === 进度区域 ===
        progress_frame = ctk.CTkFrame(panel, fg_color=COLORS["bg_input"], corner_radius=8)
        progress_frame.grid(row=3, column=0, padx=20, pady=(0, 20), sticky="ew")

        self.progress_label = ctk.CTkLabel(
            progress_frame,
            text="就绪",
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

        # === 日志区域 ===
        log_frame = ctk.CTkFrame(panel, fg_color="transparent")
        log_frame.grid(row=4, column=0, padx=20, pady=(0, 20), sticky="nsew")
        panel.grid_rowconfigure(4, weight=1)

        ctk.CTkLabel(
            log_frame,
            text="📋 处理日志",
            font=ctk.CTkFont(family="Microsoft YaHei", size=12, weight="bold"),
            text_color=COLORS["text"],
        ).pack(anchor="w", pady=(0, 8))

        self.log_text = ctk.CTkTextbox(
            log_frame,
            fg_color=COLORS["bg_input"],
            text_color=COLORS["text_muted"],
            font=ctk.CTkFont(family="Consolas", size=11),
            corner_radius=8,
            height=120,
        )
        self.log_text.pack(fill="both", expand=True)

    def _create_status_bar(self, parent) -> None:
        """底部状态栏"""
        status_bar = ctk.CTkFrame(parent, fg_color=COLORS["bg_card"], corner_radius=8, height=40)
        status_bar.grid(row=2, column=0, sticky="ew", pady=(16, 0))
        status_bar.grid_propagate(False)

        self.status_label = ctk.CTkLabel(
            status_bar,
            text="✨ 准备就绪，选择文件后点击「开始处理」",
            font=ctk.CTkFont(size=12),
            text_color=COLORS["text_muted"],
        )
        self.status_label.pack(side="left", padx=16, pady=10)

        ctk.CTkLabel(
            status_bar,
            text="Made with ❤️ by 虎哥",
            font=ctk.CTkFont(size=11),
            text_color=COLORS["text_muted"],
        ).pack(side="right", padx=16, pady=10)

    # === 文件选择逻辑 ===

    def _select_files(self) -> None:
        from tkinter import filedialog

        paths = filedialog.askopenfilenames(
            title="选择 PDF 文件",
            filetypes=[("PDF 文件", "*.pdf"), ("所有文件", "*.*")],
        )
        if not paths:
            return
        self.selected_files.extend(Path(p) for p in paths)
        self._refresh_file_list()

    def _select_folder(self) -> None:
        from tkinter import filedialog

        folder = filedialog.askdirectory(title="选择包含 PDF 的文件夹")
        if not folder:
            return
        pdfs = list(Path(folder).glob("*.pdf"))
        self.selected_files.extend(pdfs)
        self._refresh_file_list()

    def _clear_files(self) -> None:
        self.selected_files.clear()
        self._refresh_file_list()

    def _refresh_file_list(self) -> None:
        self.files_textbox.configure(state="normal", text_color=COLORS["text"])
        self.files_textbox.delete("1.0", "end")

        if not self.selected_files:
            self.files_textbox.insert("1.0", "将 PDF 文件拖放到此处，或点击上方按钮选择文件...\n\n支持批量处理，智能识别文件标题。")
            self.files_textbox.configure(text_color=COLORS["text_muted"])
        else:
            for i, p in enumerate(self.selected_files, 1):
                size_mb = p.stat().st_size / 1024 / 1024
                self.files_textbox.insert("end", f"{i:3d}. {p.name}  ({size_mb:.1f} MB)\n")

        self.files_textbox.configure(state="disabled")

        count = len(self.selected_files)
        self.file_count_label.configure(text=f"{count} 个文件")

        state = "normal" if count > 0 else "disabled"
        self.preview_btn.configure(state=state)
        self.start_btn.configure(state=state)

        if count > 0:
            self.status_label.configure(text=f"✅ 已选择 {count} 个文件，点击「开始处理」进行重命名")

    # === 设置与处理 ===

    def _apply_settings(self) -> None:
        try:
            max_len = int(self.max_len_var.get())
        except ValueError:
            messagebox.showerror("错误", "最大长度必须是整数")
            return

        config_manager_v3.update_config(
            max_filename_length=max_len,
            auto_backup=self.backup_var.get(),
            parallel_processing=self.parallel_var.get(),
            add_timestamp=self.ts_var.get(),
        )

    def _preview(self) -> None:
        if not self.selected_files:
            messagebox.showwarning("提示", "请先选择文件")
            return

        self._apply_settings()
        self.status_label.configure(text="⏳ 正在生成预览...")
        self._log("开始生成预览...")

        def worker() -> None:
            try:
                results, _ = self.processor.process_files(self.selected_files, progress_callback=None)
                self.after(0, lambda: self._show_preview_results(results))
            except Exception as e:
                self.after(0, lambda: self._log(f"❌ 预览失败: {e}"))

        threading.Thread(target=worker, daemon=True).start()

    def _show_preview_results(self, results) -> None:
        ok = sum(1 for r in results if r.success)
        total = len(results)

        self._log(f"\n{'='*40}")
        self._log(f"📋 预览结果: {ok}/{total} 可重命名")
        self._log(f"{'='*40}")

        for r in results:
            if r.success and r.new_path is not None:
                self._log(f"✅ {r.original_path.name}")
                self._log(f"   → {r.new_path.name}")
            else:
                self._log(f"❌ {r.original_path.name}")
                self._log(f"   原因: {r.error_message}")

        self.status_label.configure(text=f"👁️ 预览完成: {ok}/{total} 可重命名")

    def _start(self) -> None:
        if not self.selected_files:
            messagebox.showwarning("提示", "请先选择文件")
            return

        if self.is_processing:
            return

        self._apply_settings()
        self.is_processing = True

        # 清空左侧列表，准备实时显示处理结果
        self.files_textbox.configure(state="normal", text_color=COLORS["text"])
        self.files_textbox.delete("1.0", "end")
        self.files_textbox.configure(state="disabled")

        total = len(self.selected_files)
        self.progress_bar.set(0)
        self.progress_label.configure(text="开始处理...")
        self.start_btn.configure(state="disabled", text="⏳ 处理中...")
        self.status_label.configure(text=f"🚀 正在处理 {total} 个文件...")

        self._log(f"\n{'='*40}")
        self._log(f"🚀 开始处理 {total} 个文件")
        self._log(f"{'='*40}")

        def cb(current: int, total_files: int, current_file: Path, result) -> None:
            progress = current / max(total_files, 1)
            self.after(
                0,
                lambda: self._on_progress(current, total_files, current_file, progress, result),
            )

        def worker() -> None:
            try:
                results, stats = self.processor.process_files(self.selected_files, progress_callback=cb)
                self.after(0, lambda: self._on_done(results, stats))
            except Exception as e:
                self.after(0, lambda: self._log(f"❌ 处理失败: {e}"))
                self.after(0, lambda: self._reset_ui())

        threading.Thread(target=worker, daemon=True).start()

    def _on_progress(
        self,
        current: int,
        total: int,
        current_file: Path,
        progress: float,
        result,
    ) -> None:
        self.progress_bar.set(progress)
        self.progress_label.configure(text=f"处理中 {current}/{total}")
        self.current_file_label.configure(
            text=current_file.name[:50] + "..." if len(current_file.name) > 50 else current_file.name
        )
        self._append_incremental_result(current, result)

    def _on_done(self, results, stats) -> None:
        ok = sum(1 for r in results if r.success)
        total = len(results)

        self.progress_bar.set(1.0)
        self.progress_label.configure(text=f"完成 {ok}/{total}")
        self.current_file_label.configure(text="")

        # 显示结果
        rate = stats.success_rate * 100
        emoji = "🎉" if rate >= 90 else ("✅" if rate >= 70 else "⚠️")

        self._log(f"\n{emoji} 处理完成!")
        self._log(f"   成功: {ok}/{total} ({rate:.1f}%)")
        self._log(f"   用时: {stats.duration:.1f} 秒")

        self.status_label.configure(text=f"{emoji} 完成: {ok}/{total} 成功，用时 {stats.duration:.1f}s")

        self._reset_ui()

    def _reset_ui(self) -> None:
        self.is_processing = False
        self.start_btn.configure(state="normal", text="🚀 开始处理")

    def _log(self, msg: str) -> None:
        ts = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert("end", f"[{ts}] {msg}\n")
        self.log_text.see("end")

    def _append_incremental_result(self, index: int, result) -> None:
        """处理中实时追加一条重命名结果到左侧列表"""
        self.files_textbox.configure(state="normal", text_color=COLORS["text"])

        old_name = result.original_path.name
        if result.success and result.new_path is not None:
            new_name = result.new_path.name
            if old_name != new_name:
                self.files_textbox.insert("end", f"{index:3d}. ✅ {old_name}\n")
                self.files_textbox.insert("end", f"     → {new_name}\n")
            else:
                self.files_textbox.insert("end", f"{index:3d}. ✅ {old_name} (无需更改)\n")
        else:
            self.files_textbox.insert("end", f"{index:3d}. ❌ {old_name}\n")
            if result.error_message:
                self.files_textbox.insert("end", f"     原因: {result.error_message}\n")

        self.files_textbox.see("end")
        self.files_textbox.configure(state="disabled")

    def _show_rename_results(self, results) -> None:
        """处理完成后更新文件列表，显示原文件名 → 新文件名"""
        self.files_textbox.configure(state="normal", text_color=COLORS["text"])
        self.files_textbox.delete("1.0", "end")

        for i, r in enumerate(results, 1):
            old_name = r.original_path.name
            if r.success and r.new_path is not None:
                new_name = r.new_path.name
                if old_name != new_name:
                    self.files_textbox.insert("end", f"{i:3d}. ✅ {old_name}\n")
                    self.files_textbox.insert("end", f"     → {new_name}\n")
                else:
                    self.files_textbox.insert("end", f"{i:3d}. ✅ {old_name} (无需更改)\n")
            else:
                self.files_textbox.insert("end", f"{i:3d}. ❌ {old_name}\n")
                self.files_textbox.insert("end", f"     原因: {r.error_message}\n")

        self.files_textbox.configure(state="disabled")


def main() -> None:
    app = MainAppV3()
    app.mainloop()


if __name__ == "__main__":
    main()
