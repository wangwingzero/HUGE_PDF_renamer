#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""English Language Pack (US English)

Contains all UI text translations in English.

Copyright (c) 2024-2026 Tiger
Licensed under the MIT License.
"""

TRANSLATIONS = {
    # ============================================================
    # App Info
    # ============================================================
    "app.name": "Tiger PDF Renamer",
    "app.subtitle": "Smart Extract · Batch Process · One-Click Rename",

    # ============================================================
    # File Panel
    # ============================================================
    "panel.files": "📁 File List",
    "panel.files.count": "{count} files",
    "panel.files.placeholder": "Drag and drop PDF files here, or click the buttons above to select files...\n\nSupports batch processing with smart title extraction.",
    "panel.files.unreadable": "Unreadable",

    # ============================================================
    # Buttons
    # ============================================================
    "btn.select_files": "📄 Select Files",
    "btn.select_folder": "📂 Select Folder",
    "btn.clear": "🗑️ Clear",
    "btn.preview": "👁️ Preview",
    "btn.start": "🚀 Start Processing",
    "btn.start.processing": "⏳ Processing...",
    "btn.cancel": "⏹️ Cancel",
    "btn.cancel.cancelling": "⏹️ Cancelling...",

    # ============================================================
    # Settings
    # ============================================================
    "settings.title": "⚙️ Settings",
    "settings.max_length": "Max Filename Length",
    "settings.backup": "📦 Auto Backup Original Files",
    "settings.parallel": "⚡ Parallel Processing (Faster)",
    "settings.timestamp": "🕐 Add Timestamp Suffix",
    "settings.language": "🌐 Language",
    "settings.language.restart_hint": "Restart required for full language change",

    # ============================================================
    # Mode Description
    # ============================================================
    "mode.smart": "🧠 Smart Extraction Mode",
    "mode.smart.desc": "Auto-detect PDF metadata and first page content\nDetailed analysis for small files, fast processing for large files",

    # ============================================================
    # Status Messages
    # ============================================================
    "status.ready": "✨ Ready. Select files and click 'Start Processing'",
    "status.selected": "✅ {count} files selected. Click 'Start Processing' to rename",
    "status.processing": "🚀 Processing {count} files...",
    "status.generating_preview": "⏳ Generating preview...",
    "status.preview_done": "👁️ Preview done: {success}/{total} can be renamed",
    "status.done": "{emoji} Done: {success}/{total} succeeded in {time}s",
    "status.cancelled": "⚠️ Cancelled: Processed {total} files, {success} succeeded",

    # ============================================================
    # Progress
    # ============================================================
    "progress.ready": "Ready",
    "progress.starting": "Starting...",
    "progress.processing": "Processing {current}/{total}",
    "progress.done": "Done {success}/{total}",

    # ============================================================
    # Log
    # ============================================================
    "log.title": "📋 Processing Log",
    "log.preview_start": "Generating preview...",
    "log.preview_result": "📋 Preview result: {success}/{total} can be renamed",
    "log.preview_failed": "❌ Preview failed: {error}",
    "log.process_start": "🚀 Processing {count} files",
    "log.process_failed": "❌ Processing failed: {error}",
    "log.process_done": "{emoji} Processing complete!",
    "log.process_cancelled": "⚠️ Processing cancelled!",
    "log.processed_count": "Processed: {count} files",
    "log.success_count": "Success: {success} ({rate}%)",
    "log.duration": "Duration: {time} seconds",
    "log.cancel_requested": "⚠️ Cancel requested, waiting for current file to finish...",
    "log.reason": "Reason: {reason}",
    "log.no_change": "No change needed",

    # ============================================================
    # Dialogs
    # ============================================================
    "dialog.error": "Error",
    "dialog.warning": "Notice",
    "dialog.info": "Information",
    "dialog.max_length_error": "Max length must be an integer",
    "dialog.select_files_first": "Please select files first",
    "dialog.select_pdf_files": "Select PDF Files",
    "dialog.select_folder": "Select Folder Containing PDFs",
    "dialog.pdf_files": "PDF Files",
    "dialog.all_files": "All Files",

    # ============================================================
    # Footer
    # ============================================================
    "footer.author": "Made with ❤️ by {author}",
}
