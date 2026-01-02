English | [中文](README.md)

# Tiger PDF Renamer

> Smart Extract · Batch Process · One-Click Rename

A simple and easy-to-use PDF batch renaming tool that automatically extracts PDF metadata or first-page content as filenames.

**Version**: v1.0.0  
**Author**: Tiger (虎哥)  
**License**: MIT License

## Features

- 🧠 Smart extraction of PDF metadata titles or first-page text
- 📦 Batch processing of multiple PDF files
- ⚡ Optional parallel processing for faster speed
- 🔄 Automatic filename conflict resolution
- 📝 Complete logging
- 💾 Optional automatic backup of original files
- 🌐 Multi-language support (Chinese/English)

## Quick Start

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Run the Application

```bash
python run_tiger_pdf_renamer.py
```

### Usage

1. Click "Select Files" or "Select Folder" to add PDF files
2. Adjust settings as needed (max filename length, backup option, etc.)
3. Click "Preview" to see the renaming results
4. Click "Start Processing" to execute the renaming

## Project Structure

```
pdf_renamer/
├── run_tiger_pdf_renamer.py   # Entry point
├── main/                       # Core modules
│   ├── __init__.py            # Package initialization, version info
│   ├── pdf_renamer.py         # GUI main interface
│   ├── config.py              # Configuration management
│   ├── file_processor.py      # File processing core
│   ├── smart_text_extractor.py # PDF title extraction
│   ├── utils.py               # Utility functions
│   └── i18n/                  # Internationalization
│       ├── __init__.py        # I18nManager class
│       ├── zh_CN.py           # Chinese language pack
│       └── en_US.py           # English language pack
├── config.json                # User configuration
├── logs/                      # Log directory
└── requirements.txt           # Dependencies
```

## Configuration

The configuration file `config.json` supports the following options:

| Option | Description | Default |
|--------|-------------|---------|
| max_filename_length | Maximum filename length | 120 |
| add_timestamp | Add timestamp suffix | false |
| auto_backup | Auto backup original files | false |
| parallel_processing | Enable parallel processing | true |
| max_workers | Maximum parallel threads | 4 |
| language | Interface language (zh_CN/en_US) | zh_CN |

## System Requirements

- Python 3.9+
- Windows 7/8/10/11

## Dependencies

- customtkinter - Modern GUI framework
- pypdf - PDF metadata extraction
- pdfplumber - PDF text extraction

## Technical Support

For questions or suggestions, please contact:
- Submit Issues
- Email: 86250887@qq.com

## License

Copyright (c) 2024-2026 Tiger (虎哥)

This software is released under the MIT License. See [LICENSE](LICENSE) file for details