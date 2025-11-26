import os
import logging
from datetime import datetime

def setup_logging(prefix, force_new=False):
    """设置日志系统
    
    Args:
        prefix (str): 日志文件名前缀，例如 'pdf_renamer' 或 'right_click'
        force_new (bool): 是否强制创建新的日志文件
        
    Returns:
        tuple: (logger对象, 日志文件路径)
    """
    # 获取脚本所在目录
    script_dir = os.path.dirname(os.path.abspath(__file__))
    logs_dir = os.path.join(script_dir, 'logs')
    os.makedirs(logs_dir, exist_ok=True)
    
    # 使用当天日期作为日志文件名
    today = datetime.now().strftime('%Y%m%d')
    log_file = os.path.join(logs_dir, f"pdf_renamer_{today}.log")
    
    # 创建logger对象
    logger = logging.getLogger('pdf_renamer')
    
    # 如果logger已经有处理器，并且不强制创建新文件，则直接返回
    if logger.handlers and not force_new:
        return logger, log_file
        
    # 清除现有的处理器
    logger.handlers.clear()
    logger.setLevel(logging.INFO)
    
    # 创建文件处理器
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.INFO)
    
    # 创建控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # 创建格式化器
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # 设置格式化器
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # 添加处理器到logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    # 初始日志
    if force_new:
        logger.info(f"日志文件创建于: {log_file}")
        logger.info(f"日志系统初始化完成")
    
    return logger, log_file

def check_and_create_dir(path):
    """检查并创建目录
    
    Args:
        path (str): 目录路径
        
    Returns:
        bool: 是否成功创建/确认目录存在
    """
    try:
        os.makedirs(path, exist_ok=True)
        return True
    except Exception as e:
        logging.error(f"创建目录失败 {path}: {str(e)}")
        return False

def is_path_exists(path):
    """检查路径是否存在
    
    Args:
        path (str): 要检查的路径
        
    Returns:
        bool: 路径是否存在
    """
    return os.path.exists(path)