# 标准库导入
import os
import sys
import signal
import threading
from datetime import datetime
from pathlib import Path
import time

# 第三方库导入
import pdfplumber
from tqdm import tqdm
import keyboard

# tkinter相关导入
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog, messagebox
from tkinter import font as tkfont
import sv_ttk  # 需要先安装: pip install sv-ttk

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
    
    # 应用sv-ttk主题
    sv_ttk.set_theme("light")
    
    print("\n请选择PDF文件...")
    files = filedialog.askopenfilenames(
        title="选择PDF文件",
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
    window.title("PDF重命名")
    
    # 设置更大的窗口尺寸
    window_width = 600
    window_height = 400
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = (screen_width - window_width) // 2
    y = (screen_height - window_height) // 2
    window.geometry(f"{window_width}x{window_height}+{x}+{y}")
    
    # 设置窗口样式
    window.configure(bg='#ffffff')
    sv_ttk.set_theme("light")
    
    # 创建主框架
    main_frame = ttk.Frame(window, padding="30")
    main_frame.pack(fill=tk.BOTH, expand=True)
    
    # 定义所有字体
    title_font = tkfont.Font(family="黑体", size=12, weight="bold")
    count_font = tkfont.Font(family="黑体", size=9)
    detail_font = tkfont.Font(family="Arial", size=9)
    
    # 标题标签
    title_label = ttk.Label(
        main_frame, 
        text="正在处理文件...", 
        font=title_font
    )
    title_label.pack(pady=(0, 20))
    
    # 创建两个进度条框架
    progress_frame = ttk.Frame(main_frame)
    progress_frame.pack(fill=tk.X, pady=(0, 20))
    
    # 总体进度标签和进度条
    total_progress_label = ttk.Label(
        progress_frame,
        text="总体进度",
        font=count_font
    )
    total_progress_label.pack(anchor=tk.W)
    
    total_progress = ttk.Progressbar(
        progress_frame,
        length=500,
        mode='determinate',
        maximum=len(files)
    )
    total_progress.pack(fill=tk.X, pady=(5, 10))
    
    # 当前文件进度标签和进度条
    file_progress_label = ttk.Label(
        progress_frame,
        text="当前文件",
        font=count_font
    )
    file_progress_label.pack(anchor=tk.W)
    
    file_progress = ttk.Progressbar(
        progress_frame,
        length=500,
        mode='determinate',
        maximum=100  # 百分比进度
    )
    file_progress.pack(fill=tk.X, pady=(5, 0))
    
    # 创建文本框来显示处理详情
    text_frame = ttk.Frame(main_frame)
    text_frame.pack(fill=tk.BOTH, expand=True)
    
    # 添加处理详情的文本框
    text_widget = tk.Text(
        text_frame,
        font=detail_font,
        height=12,
        wrap=tk.WORD,
        background='#f5f5f5',  # 浅灰色背景
        relief='flat'  # 扁平化效果
    )
    text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    
    # 添加滚动条
    scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=text_widget.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    text_widget.configure(yscrollcommand=scrollbar.set)
    
    # 处理计数 - 使用小号字体
    count_label = ttk.Label(
        main_frame,
        text=f"0 / {len(files)}",
        font=count_font
    )
    count_label.pack(pady=(10, 0))
    
    def update_text(message, tag=None):
        """更新文本框内容并添加动画效果"""
        text_widget.insert(tk.END, message + "\n", tag)
        text_widget.see(tk.END)
        text_widget.update()
    
    def update_file_progress(percentage):
        """更新单个文件的进度条"""
        current = file_progress['value']
        steps = (percentage - current) / 10  # 将进度分成10步来实现平滑动画
        for i in range(10):
            file_progress['value'] = current + (steps * (i + 1))
            window.update()
            window.after(5)  # 短暂延迟实现平滑效果
    
    # 配置文本标签样式
    text_widget.tag_configure("success", foreground="green")
    text_widget.tag_configure("error", foreground="red")
    text_widget.tag_configure("info", foreground="blue")
    text_widget.tag_configure("progress", foreground="#666666")  # 进度信息使用灰色

    try:
        exit_thread = threading.Thread(target=check_for_exit, daemon=True)
        exit_thread.start()
        
        for index, pdf_file in enumerate(files, 1):
            try:
                # 重置文件进度条
                file_progress['value'] = 0
                
                # 更新进度信息
                count_label.config(text=f"处理进度：{index} / {len(files)}")
                
                # 显示当前处理的文件
                update_text(f"正在处理: {pdf_file.name}", "info")
                
                # 更新文件进度 - 开始处理
                update_file_progress(30)
                logger.info(f"处理: {pdf_file.name}")
                
                # 提取文本
                update_text("正在提取文件文本...", "progress")
                new_name = get_largest_text(pdf_file)
                update_file_progress(60)
                
                if new_name:
                    new_path = pdf_file.parent / f"{new_name}.pdf"
                    if new_path.exists() and new_path != pdf_file:
                        counter = 1
                        while new_path.exists():
                            new_path = pdf_file.parent / f"{new_name}_{counter}.pdf"
                            counter += 1
                    
                    if new_path != pdf_file:
                        update_text("正在重命名文件...", "progress")
                        update_file_progress(80)
                        # 显示重命名详情，使用箭头标识转换过程
                        update_text(f"✓ {pdf_file.name} → {new_path.name}", "success")
                        pdf_file.rename(new_path)
                        update_file_progress(100)
                else:
                    update_text(f"✗ 无法处理: {pdf_file.name}", "error")
                    update_file_progress(100)
                
                # 更新总进度条并添加动画效果
                current = total_progress['value']
                steps = (index - current) / 10
                for i in range(10):
                    total_progress['value'] = current + (steps * (i + 1))
                    window.update()
                    window.after(10)
                
            except Exception as e:
                update_text(f"处理出错: {pdf_file.name}\n错误信息: {str(e)}", "error")
                update_file_progress(100)
        
        # 处理完成动画
        def complete_animation():
            title_label.config(text="处理完成!")
            update_text("\n✨ 所有文件处理完成! ✨", "success")
            
            # 渐变消失效果
            def fade_out():
                for alpha in [0.9, 0.7, 0.5, 0.3]:
                    window.attributes('-alpha', alpha)
                    window.update()
                    time.sleep(0.05)
                window.destroy()
                # 直接使用time.sleep而不是after
                time.sleep(2)
                os._exit(0)  # 使用os._exit确保程序完全退出
            
            # 显示完成信息3秒后开始淡出
            window.after(3000, fade_out)
        
        window.after(500, complete_animation)
        window.mainloop()
        
    except Exception as e:
        logger.error(f"处理过程出错: {e}")
        if window:
            window.destroy()
            time.sleep(3)
            os._exit(1)

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
    
    # 注册信号处理器
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    if not check_environment():
        sys.exit(1)
    
    logger.info("程序已准备就绪")
    logger.info("按ESC键可以随时终止程序")
    
    try:
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