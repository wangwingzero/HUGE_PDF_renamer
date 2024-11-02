import os
import pdfplumber
from pathlib import Path
from tqdm import tqdm
import sys
import tkinter as tk
from tkinter import filedialog, messagebox
import time
import keyboard
import threading
import signal

def check_environment():
    """检查运行环境是否正确"""
    try:
        import pdfplumber
        return True
    except ImportError as e:
        messagebox.showerror("环境错误", 
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
        title="选择PDF文件",
        filetypes=[("PDF文件", "*.pdf"), ("所有文件", "*.*")],
        multiple=True  # 允许多选
    )
    if files:
        print(f"已选择 {len(files)} 个文件")
        return [Path(f) for f in files]
    else:
        print("未选择任何文件，程序将退出")
        return None

def get_largest_text(pdf_path):
    """提取PDF第一页中字体最大的文本"""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            first_page = pdf.pages[0]
            
            # 尝试不同的参数组合来提取文本
            extraction_attempts = [
                # 尝试1：默认参数
                {'x_tolerance': 3, 'y_tolerance': 3},
                # 尝试2：更宽松的参数
                {'x_tolerance': 10, 'y_tolerance': 5},
                # 尝试3：非常宽松的参数
                {'x_tolerance': 15, 'y_tolerance': 10}
            ]
            
            for params in extraction_attempts:
                elements = first_page.extract_words(
                    keep_blank_chars=True,
                    use_text_flow=True,
                    **params
                )
                
                if elements:
                    print(f"\n使用参数 {params} 提取文本:")
                    
                    # 尝试从文本属性中获取字体信息
                    elements_with_info = []
                    for e in elements:
                        # 获取元素的详细信息
                        chars = first_page.chars
                        chars_in_word = [c for c in chars if c['x0'] >= e['x0'] and c['x1'] <= e['x1'] and 
                                       c['top'] >= e['top'] and c['bottom'] <= e['bottom']]
                        
                        if chars_in_word:
                            # 使用字符的最大字体大小作为单词的字体大小
                            max_font_size = max(c.get('size', 0) for c in chars_in_word)
                            if max_font_size > 0:
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
                        
                        print(f"找到的文本元素:")
                        for e in sorted_elements[:5]:  # 显示前5个最大的文本
                            print(f"文本: {e['text']}, 大小: {e['size']}")
                        
                        # 获取所有最大字体的文本元素（允许1的误差）
                        largest_texts = [e for e in sorted_elements if abs(e['size'] - max_size) < 1]
                        
                        # 按位置排序（先上下，后左右）
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
                            print(f"\n合并后的文本: {final_text}")
                            cleaned_text = clean_text(final_text)
                            if cleaned_text:
                                return cleaned_text
            
            print(f"\n{pdf_path.name} 无法提取有效文本")
            return None
            
    except Exception as e:
        print(f"\n处理文件时出错: {e}")
        return None

def clean_text(text):
    """清理和验证文本"""
    # 移除特殊字符和无效内容
    if not text:
        return None
        
    # 移除cid标记
    if 'cid' in text.lower():
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

def merge_text_elements(elements):
    """合并文本元素"""
    result = []
    current_line = []
    current_top = elements[0]['top']
    
    for text in elements:
        if abs(text['top'] - current_top) < 5:
            current_line.append(text['text'].strip())
        else:
            if current_line:
                result.append(''.join(current_line))
            current_line = [text['text'].strip()]
            current_top = text['top']
    
    if current_line:
        result.append(''.join(current_line))
    
    # 只返回前两行，通常标题不会太长
    return ' '.join(result[:2])

def get_top_text(elements):
    """从页面顶部提取文本"""
    print("\n使用位置策略提取文本")
    # 获取页面前20%区域的元素
    page_height = max(e['top'] for e in elements)
    top_threshold = page_height * 0.2
    
    top_elements = sorted(
        [e for e in elements if e['top'] <= top_threshold],
        key=lambda x: (x['top'], x['x0'])
    )
    
    if top_elements:
        result = []
        current_line = []
        current_top = top_elements[0]['top']
        
        for text in top_elements:
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
        print(f"\n使用位置策略得到的文本: {final_text}")
        return final_text
    
    return elements[0]['text'].strip()

def safe_rename(old_path, new_path, max_retries=3, delay=1):
    """安全地重命名文件，处理文件被占用的情况"""
    for attempt in range(max_retries):
        try:
            old_path.rename(new_path)
            return True
        except PermissionError:
            if attempt < max_retries - 1:
                print(f"\n文件被占用，等待{delay}秒后重试...")
                time.sleep(delay)
            else:
                print(f"\n无法重命名文件 {old_path.name}：文件被占用")
                return False
        except Exception as e:
            print(f"\n重命名文件时出错: {e}")
            return False
    return False

def check_for_exit():
    """检查是否按下ESC键"""
    while True:
        if keyboard.is_pressed('esc'):
            print("\n用户按下ESC，正在终止程序...")
            os._exit(0)  # 强制终止程序

def rename_pdfs(files):
    """重命名PDF文件"""
    if not files:  # 用户取消选择
        return
    
    # 启动ESC监听线程
    exit_thread = threading.Thread(target=check_for_exit, daemon=True)
    exit_thread.start()

    try:
        # 使用tqdm创建进度条
        with tqdm(total=len(files), desc="重命名进度") as pbar:
            for pdf_file in files:
                try:
                    print(f"\n处理: {pdf_file.name}")
                    new_name = get_largest_text(pdf_file)
                    
                    if new_name:
                        new_name = "".join(c for c in new_name if c.isalnum() or c in (' ', '-', '_'))
                        new_name = new_name.strip()
                        
                        if not new_name:
                            print(f"无法为 {pdf_file.name} 提取有效文件名")
                            continue
                        
                        new_path = pdf_file.parent / f"{new_name}.pdf"
                        
                        # 只有在文件已存在时才添加数字后缀
                        if new_path.exists() and new_path != pdf_file:
                            counter = 1
                            while new_path.exists():
                                new_path = pdf_file.parent / f"{new_name}_{counter}.pdf"
                                counter += 1
                        
                        if new_path != pdf_file:  # 只在新文件名不同时才重命名
                            print(f"重命名为: {new_path.name}")
                            safe_rename(pdf_file, new_path)
                    else:
                        print(f"无法从 {pdf_file.name} 提取文本")

                except Exception as e:
                    print(f"处理 {pdf_file.name} 时出错: {e}")
                
                finally:
                    # 无论成功与否都更新进度条
                    pbar.update(1)
    
    finally:
        # 直接退出，不显示完成消息
        os._exit(0)

def signal_handler(signum, frame):
    """处理终止信号"""
    print("\n接收到终止信号，正在退出程序...")
    sys.exit(0)

if __name__ == "__main__":
    print("PDF文件重命名工具启动...")
    
    # 注册信号处理器
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # 添加环境检查
    print("检查运行环境...")
    if not check_environment():
        sys.exit(1)
    
    # 安装keyboard库（如果需要）
    try:
        import keyboard
    except ImportError:
        print("安装keyboard库...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'keyboard'], check=True)
        import keyboard
    
    print("\n程序已准备就绪")
    print("按ESC键可以随时终止程序")
    print("\n请在弹出的对话框中选择文件...")
    
    if len(sys.argv) > 1:
        # 如果是从命令行传入路径
        path = Path(sys.argv[1])
        if path.is_file():
            files = [path]
        else:
            files = list(path.glob("*.pdf"))
    else:
        files = select_files()
    
    if files:
        rename_pdfs(files)
    else:
        print("程序已取消")