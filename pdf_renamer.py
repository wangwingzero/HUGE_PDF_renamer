# 标准库导入
import os
import sys
import signal
import threading
from datetime import datetime
from pathlib import Path

# 第三方库导入
import pdfplumber
from tqdm import tqdm
import keyboard

# tkinter相关导入
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog, messagebox

# 本地模块导入
from utils import setup_logging

def check_environment():
    """检查运行环境是否正确"""
    try:
        import pdfplumber
        return True
    except ImportError as e:
        messagebox.showerror("虎大王PDF重命名 - 环境错误", 
            f"缺少必要的库: {str(e)}\n"
            "请确保已安装 pdfplumber:\n"
            "pip install pdfplumber")
        return False

def select_files():
    """打开文件选择对话框"""
    root = tk.Tk()
    root.withdraw()  # 隐藏主窗口
    print("\n请选择PDF文件...")
    files = filedialog.askopenfilenames(
        title="虎大王PDF重命名 - 选择PDF文件",
        filetypes=[("PDF文件", "*.pdf"), ("所有文件", "*.*")],
        multiple=True
    )
    if files:
        logger.info(f"已选择 {len(files)} 个文件")
        return [Path(f) for f in files]
    else:
        logger.info("未选择任何文件，程序将退出")
        return None

def get_largest_text(pdf_path):
    """提取PDF第一页中字体最大的文本"""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            first_page = pdf.pages[0]
            
            # 添加更多提取参数组合
            extraction_attempts = [
                {'x_tolerance': 3, 'y_tolerance': 3},
                {'x_tolerance': 10, 'y_tolerance': 5},
                {'x_tolerance': 15, 'y_tolerance': 10},
                {'x_tolerance': 20, 'y_tolerance': 15}  # 更宽松的参数
            ]
            
            for params in extraction_attempts:
                elements = first_page.extract_words(
                    keep_blank_chars=True,
                    use_text_flow=True,
                    **params
                )
                
                if elements:
                    logger.info(f"使用参数 {params} 提取文本:")
                    elements_with_info = []
                    
                    # 优化字体大小检测
                    for e in elements:
                        chars = first_page.chars
                        chars_in_word = [c for c in chars if c['x0'] >= e['x0'] and c['x1'] <= e['x1'] and 
                                       c['top'] >= e['top'] and c['bottom'] <= e['bottom']]
                        
                        if chars_in_word:
                            max_font_size = max(c.get('size', 0) for c in chars_in_word)
                            if max_font_size > 0 and not all('cid' in c.get('text', '').lower() for c in chars_in_word):
                                elements_with_info.append({
                                    'text': e['text'],
                                    'size': max_font_size,
                                    'top': e['top'],
                                    'x0': e['x0']
                                })
                    
                    if elements_with_info:
                        # 按字体大小降序排序
                        sorted_elements = sorted(elements_with_info, key=lambda x: x['size'], reverse=True)
                        max_size = sorted_elements[0]['size']
                        
                        logger.info(f"找到的文本元素:")
                        for e in sorted_elements[:5]:
                            logger.info(f"文本: {e['text']}, 大小: {e['size']}")
                        
                        # 获取所有最大字体的文本元素
                        largest_texts = [e for e in sorted_elements if abs(e['size'] - max_size) < 1]
                        
                        # 按位置排序
                        largest_texts.sort(key=lambda x: (x['top'], x['x0']))
                        
                        if largest_texts:
                            # 合并同一行的文本
                            result = []
                            current_line = []
                            current_top = largest_texts[0]['top']
                            
                            for text in largest_texts:
                                if abs(text['top'] - current_top) < 5:
                                    current_line.append(text['text'].strip())
                                else:
                                    if current_line:
                                        result.append(''.join(current_line))
                                    current_line = [text['text'].strip()]
                                    current_top = text['top']
                            
                            if current_line:
                                result.append(''.join(current_line))
                            
                            final_text = ' '.join(result)
                            logger.info(f"合并后的文本: {final_text}")
                            cleaned_text = clean_text(final_text)
                            if cleaned_text:
                                return cleaned_text
                                
            logger.warning(f"{pdf_path.name} 无法提取有效文本")
            return None
            
    except Exception as e:
        logger.error(f"处理文件时出错: {e}")
        return None

def clean_text(text):
    """清理和验证文本"""
    if not text:
        return None

    # 如果文本全是 cid，则尝试下一个提取参数
    if all('cid' in word.lower() for word in text.split()):
        return None
        
    # 基本清理
    text = text.strip()
    # 只保留允许的字符
    text = "".join(c for c in text if c.isalnum() or c in (' ', '-', '_', '（', '）', '(', ')', '【', '】'))
    
    # 限制长度
    if len(text) > 50:  # 限制最大长度
        text = text[:47] + "..."
    
    # 验证文本是否有效
    if len(text) < 2:  # 太短的文本可能无效
        return None
        
    # 确保文本包含至少一个中文字符或字母
    if not any(c.isalpha() for c in text):
        return None
        
    return text

def check_for_exit():
    """检查是否按下ESC键"""
    while True:
        if keyboard.is_pressed('esc'):
            logger.info("\n用户按下ESC，正在终止程序...")
            os._exit(0)

def rename_pdfs(files):
    """重命名PDF文件"""
    if not files:
        return
    
    # 创建进度窗口
    window = tk.Tk()
    window.title("虎大王PDF重命名工具 - 处理进度")
    window.geometry("400x150")
    window.attributes('-topmost', True)
    
    # 添加进度信息
    label = tk.Label(window, text=f"正在处理 {len(files)} 个PDF文件...", font=("Microsoft YaHei", 10))
    label.pack(pady=10)
    
    # 创建进度条
    progress = ttk.Progressbar(window, length=300, mode='determinate', maximum=len(files))
    progress.pack(pady=10)
    
    # 添加详情标签
    detail_label = tk.Label(window, text="准备开始...", font=("Microsoft YaHei", 9))
    detail_label.pack(pady=5)
    
    try:
        # 启动ESC监听线程
        exit_thread = threading.Thread(target=check_for_exit, daemon=True)
        exit_thread.start()
        
        # 处理文件
        for index, pdf_file in enumerate(files, 1):
            try:
                detail_label.config(text=f"正在处理: {pdf_file.name}")
                window.update()
                
                logger.info(f"处理: {pdf_file.name}")
                new_name = get_largest_text(pdf_file)
                
                if new_name:
                    new_path = pdf_file.parent / f"{new_name}.pdf"
                    if new_path.exists() and new_path != pdf_file:
                        counter = 1
                        while new_path.exists():
                            new_path = pdf_file.parent / f"{new_name}_{counter}.pdf"
                            counter += 1
                    
                    if new_path != pdf_file:
                        logger.info(f"重命名为: {new_path.name}")
                        pdf_file.rename(new_path)
                        detail_label.config(text=f"完成: {new_path.name}")
                else:
                    logger.warning(f"无法从 {pdf_file.name} 提取文本")
                    detail_label.config(text=f"跳过: {pdf_file.name}")
                
                progress['value'] = index
                window.update()
                
            except Exception as e:
                logger.error(f"处理 {pdf_file.name} 时出错: {e}")
                detail_label.config(text=f"出错: {pdf_file.name}")
                window.update()
        
        # 处理完成后延迟1秒关闭窗口
        detail_label.config(text="处理完成!")
        window.update()
        window.after(1000, window.destroy)  # 1秒后自动关闭
        window.mainloop()
        
    except Exception as e:
        logger.error(f"处理过程出错: {e}")
        if window:
            window.destroy()
            
    finally:
        sys.exit(0)

def signal_handler(signum, frame):
    """处理终止信号"""
    logger.info("接收到终止信号正在退出程序...")
    sys.exit(0)

def merge_files_from_args():
    """从命令行参数合并文件列表"""
    files = []
    for arg in sys.argv[1:]:
        # 移除引号
        arg = arg.strip('"').strip("'")
        path = Path(arg)
        if path.is_file() and path.suffix.lower() in ['.pdf', '.PDF']:
            files.append(path)
        elif path.is_dir():
            pdf_files = list(path.glob("*.pdf")) + list(path.glob("*.PDF"))
            files.extend(pdf_files)
    return files

# 创建全局logger对象
logger = None

if __name__ == "__main__":
    # 初始化logger
    logger, log_file = setup_logging('pdf_renamer', force_new=False)
    logger.name = 'pdf_renamer'
    logger.info("虎大王PDF重命名工具启动...")
    
    # 记录环境信息
    logger.info(f"Python版本: {sys.version}")
    logger.info(f"Python路径: {sys.executable}")
    logger.info(f"工作目录: {os.getcwd()}")
    logger.info(f"命令行参数: {sys.argv}")
    
    # 注册信号处理器
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    if not check_environment():
        sys.exit(1)
    
    logger.info("程序已准备就绪")
    logger.info("按ESC键可以随时终止程序")
    
    try:
        if len(sys.argv) > 1:
            # 处理传入的文件列表
            files = merge_files_from_args()
            if not files:
                logger.error("未找到有效的PDF文件")
                sys.exit(1)
        else:
            # 打开文件选择对话框
            files = select_files()
            if not files:
                logger.info("未选择文件")
                sys.exit(0)
        
        # 处理文件
        logger.info(f"找到 {len(files)} 个PDF文件")
        
        # 显示处理进度窗口并处理文件
        root = tk.Tk()
        root.withdraw()  # 隐藏主窗口
        rename_pdfs(files)
        
    except Exception as e:
        logger.error(f"程序运行出错: {e}")
        messagebox.showerror("错误", str(e))
        sys.exit(1)