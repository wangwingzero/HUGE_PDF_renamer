[English](README_EN.md) | 中文

# 虎哥PDF重命名

> 智能识别 · 批量处理 · 一键重命名

一个简单易用的 PDF 文件批量重命名工具，可以自动提取 PDF 元数据或首页内容作为文件名。

**版本**: v1.0.0  
**作者**: 虎哥  
**许可证**: MIT License

## 功能特点

- 🧠 智能提取 PDF 元数据标题或首页文本
- 📦 支持批量处理多个 PDF 文件
- ⚡ 可选并行处理，提升处理速度
- 🔄 自动处理文件名冲突
- 📝 完整的日志记录
- 💾 可选自动备份原文件

## 快速开始

### 安装依赖

```bash
pip install -r requirements.txt
```

### 运行程序

```bash
python run_tiger_pdf_renamer.py
```

### 使用方式

1. 点击「选择文件」或「选择文件夹」添加 PDF 文件
2. 根据需要调整设置（最大文件名长度、是否备份等）
3. 点击「预览」查看重命名结果
4. 点击「开始处理」执行重命名

## 项目结构

```
pdf_renamer/
├── run_tiger_pdf_renamer.py   # 入口文件
├── main/                       # 核心模块
│   ├── __init__.py            # 包初始化，版本信息
│   ├── pdf_renamer.py         # GUI 主界面
│   ├── config.py              # 配置管理
│   ├── file_processor.py      # 文件处理核心
│   ├── smart_text_extractor.py # PDF 标题提取
│   └── utils.py               # 工具函数
├── config.json                # 用户配置
├── logs/                      # 日志目录
└── requirements.txt           # 依赖列表
```

## 配置说明

配置文件 `config.json` 支持以下选项：

| 选项 | 说明 | 默认值 |
|------|------|--------|
| max_filename_length | 最大文件名长度 | 120 |
| add_timestamp | 添加时间戳后缀 | false |
| auto_backup | 自动备份原文件 | false |
| parallel_processing | 启用并行处理 | true |
| max_workers | 最大并行线程数 | 4 |

## 系统要求

- Python 3.9+
- Windows 7/8/10/11

## 依赖库

- customtkinter - 现代化 GUI 框架
- pypdf - PDF 元数据提取
- pdfplumber - PDF 文本提取

## 技术支持

如有问题或建议，请通过以下方式联系：
- 提交 Issues
- 发送邮件至：86250887@qq.com

## 版权声明

Copyright (c) 2024-2026 虎哥

本软件基于 MIT 许可证发布，详见 [LICENSE](LICENSE) 文件。
