import os
import sys
import subprocess
from pathlib import Path

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

if __name__ == "__main__":
    # 如果不是管理员权限，请求提升权限
    if not is_admin():
        import ctypes
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, f'"{__file__}"', None, 1
        )
        sys.exit()

    # 获取程序所在目录
    if getattr(sys, 'frozen', False):
        base_path = os.path.dirname(sys.executable)
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))

    # 运行右键菜单管理程序进行注册
    manager_path = os.path.join(base_path, "虎哥PDF重命名工具_右键菜单管理.exe")
    subprocess.run([manager_path, "--register"], check=True)
    
    print("\n安装完成！按任意键退出...")
    input() 