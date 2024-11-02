import os
import sys
import winreg
import ctypes
from pathlib import Path
import logging
import argparse
from utils import setup_logging  # 使用相同的日志设置

def is_admin():
    """检查是否具有管理员权限"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_as_admin():
    """以管理员权限重新运行程序"""
    if not is_admin():
        # 重新以管理员权限运行程序
        ctypes.windll.shell32.ShellExecuteW(
            None, 
            "runas", 
            sys.executable, 
            " ".join(["right_click.py"] + [f'"{arg}"' if ' ' in arg else arg for arg in sys.argv[1:]]),
            None, 
            1
        )
        return True
    return False

def register_context_menu():
    """注册右键菜单"""
    try:
        # 获取程序所在目录
        if getattr(sys, 'frozen', False):
            # 如果是打包后的exe
            base_path = os.path.dirname(sys.executable)
            pdf_renamer_path = os.path.join(base_path, "虎哥PDF重命名工具.exe")
        else:
            # 如果是源码运行
            base_path = os.path.dirname(os.path.abspath(__file__))
            pdf_renamer_path = os.path.join(base_path, "pdf_renamer.py")
        
        if not os.path.exists(pdf_renamer_path):
            logger.error(f"找不到程序文件: {pdf_renamer_path}")
            return False
            
        # 构建命令
        if getattr(sys, 'frozen', False):
            file_command = f'"{pdf_renamer_path}" %*'
            dir_command = f'"{pdf_renamer_path}" "%1"'
        else:
            pythonw_path = os.path.join(os.path.dirname(sys.executable), "pythonw.exe")
            file_command = f'cmd /c """{pythonw_path}" "{pdf_renamer_path}" %*"'
            dir_command = f'cmd /c """{pythonw_path}" "{pdf_renamer_path}" "%1""'

        try:
            pdf_key = winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, r"SystemFileAssociations\.pdf\shell\PDFTigerRename")
            winreg.SetValue(pdf_key, "", winreg.REG_SZ, "虎哥PDF重命名工具")
            command_key = winreg.CreateKey(pdf_key, "command")
            winreg.SetValue(command_key, "", winreg.REG_SZ, file_command)
            winreg.SetValueEx(pdf_key, "Icon", 0, winreg.REG_SZ, "%SystemRoot%\\System32\\shell32.dll,46")
            
            # 设置多选模式
            winreg.SetValueEx(pdf_key, "MultiSelectModel", 0, winreg.REG_SZ, "Player")
            logger.info("成功注册PDF文件菜单")
        except Exception as e:
            logger.error(f"注册PDF文件菜单失败: {str(e)}")
            return False

        try:
            dir_key = winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, r"Directory\shell\PDFTigerRename")
            winreg.SetValue(dir_key, "", winreg.REG_SZ, "虎哥重命名此文件夹内PDF")
            dir_command_key = winreg.CreateKey(dir_key, "command")
            winreg.SetValue(dir_command_key, "", winreg.REG_SZ, dir_command)
            winreg.SetValueEx(dir_key, "Icon", 0, winreg.REG_SZ, "%SystemRoot%\\System32\\shell32.dll,46")
            
            logger.info("成功注册目录菜单")
        except Exception as e:
            logger.error(f"注册目录菜单失败: {str(e)}")

        logger.info("右键菜单注册成功")
        return True
        
    except Exception as e:
        logger.error(f"注册右键菜单失败: {str(e)}")
        return False

def unregister_context_menu():
    """移除右键菜单"""
    try:
        success = False
        
        # 删除PDF文件的右键菜单
        try:
            winreg.DeleteKey(winreg.HKEY_CLASSES_ROOT, r"SystemFileAssociations\.pdf\shell\PDFTigerRename\command")
            winreg.DeleteKey(winreg.HKEY_CLASSES_ROOT, r"SystemFileAssociations\.pdf\shell\PDFTigerRename")
            logger.info("成功移除PDF文件菜单")
            success = True
        except WindowsError as e:
            logger.warning(f"移除PDF文件菜单失败: {str(e)}")

        # 删除目录的右键菜单
        try:
            winreg.DeleteKey(winreg.HKEY_CLASSES_ROOT, r"Directory\shell\PDFTigerRename\command")
            winreg.DeleteKey(winreg.HKEY_CLASSES_ROOT, r"Directory\shell\PDFTigerRename")
            logger.info("成功移除目录菜单")
            success = True
        except WindowsError as e:
            logger.warning(f"移除目录菜单失败: {str(e)}")

        # 清理旧版本可能存在的注册表项
        try:
            old_keys = [
                r"*\shell\PDFAutoRenamer",
                r"*\shell\PDFTigerRename",
                r".pdf\shell\PDFAutoRenamer",
                r".pdf\shell\PDFTigerRename",
            ]
            for key in old_keys:
                try:
                    winreg.DeleteKey(winreg.HKEY_CLASSES_ROOT, f"{key}\\command")
                    winreg.DeleteKey(winreg.HKEY_CLASSES_ROOT, key)
                except WindowsError:
                    pass
            logger.info("已清理旧版本注册表项")
        except Exception:
            pass

        if success:
            logger.info("右键菜单移除成功")
            return True
        else:
            logger.error("所有移除尝试都失败了")
            return False
        
    except Exception as e:
        logger.error(f"移除右键菜单失败: {str(e)}")
        return False

def main():
    parser = argparse.ArgumentParser(description='虎大王PDF重命名工具 - 右键菜���管理')
    parser.add_argument('--register', action='store_true', help='册右键菜单')
    parser.add_argument('--unregister', action='store_true', help='移除右键菜单')
    
    args = parser.parse_args()
    
    # 检查是否有任何参数
    if not (args.register or args.unregister):
        parser.print_help()
        logger.info("未提供任何参数，显示帮助信息")
        return
    
    # 检查管理员权限
    if not is_admin():
        if run_as_admin():
            logger.info("正在以管理员权限重新运行程序")
            sys.exit(0)
        else:
            logger.error("需要管理员权限来修改注册表")
            sys.exit(1)
    
    # 处理注册/注销命令
    if args.register:
        success = register_context_menu()
        if success:
            print("\n右键菜单注册成功！")
            print('- 在任文件上右键可以看到"虎哥PDF重命名工具"选项')
            print('- 在文件夹上右键可以看到"虎哥重命名此文件夹内PDF"选项')
        else:
            print("\n右键菜单注册失败，请查看日志文件了解详情。")
        sys.exit(0 if success else 1)
    elif args.unregister:
        success = unregister_context_menu()
        if success:
            print("\n右键菜单移除成功！")
        else:
            print("\n右键菜单移除失败，请查看日志文件了解详情。")
        sys.exit(0 if success else 1)

# 创建全局logger对象
logger = None

if __name__ == "__main__":
    # 初始化logger，强制创建新文件
    logger, log_file = setup_logging('right_click', force_new=True)
    logger.name = 'right_click'  # 设置logger名称以区分来源
    logger.info("虎大王PDF重命名工具 - 右键菜单管理启动...")
    
    main()