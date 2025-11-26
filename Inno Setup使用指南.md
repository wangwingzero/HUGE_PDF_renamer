# 🔧 Inno Setup 安装包制作指南

## 📋 准备工作

### 1. 下载和安装 Inno Setup
- 访问：https://jrsoftware.org/isinfo.php
- 下载最新版本（推荐6.2.2或更高版本）
- 安装时选择中文语言包

### 2. 确认文件准备完成
确保以下文件存在：
- ✅ `dist/虎大王PDF重命名工具v2/` 文件夹（已构建的程序）
- ✅ `pdf_renamer.ico` 图标文件
- ✅ `setup.iss` 配置文件（已更新）

## 🚀 制作安装包步骤

### 方法1：使用配置文件（推荐）

1. **打开 Inno Setup Compiler**
2. **选择 "File" → "Open"**
3. **选择项目根目录的 `setup.iss` 文件**
4. **点击 "Build" → "Compile"** 或按 `Ctrl+F9`
5. **等待编译完成**

### 方法2：使用脚本向导

1. **打开 Inno Setup**
2. **选择 "Create a new script file using the Script Wizard"**
3. **按照向导填写信息**：
   - Application Name: 虎大王PDF重命名工具
   - Application Version: 2.0.0
   - Company: 虎大王
   - Application Executable: `dist/虎大王PDF重命名工具v2/虎大王PDF重命名工具v2.exe`

## 📊 配置说明

### 当前 setup.iss 配置特点：

#### 🔸 基本信息
- **应用名称**: 虎大王PDF重命名工具
- **版本**: 2.0.0
- **发布者**: 虎大王
- **安装目录**: `%ProgramFiles%/虎大王PDF重命名工具`

#### 🔸 安装特性
- **中文界面**: 使用简体中文安装界面
- **现代样式**: WizardStyle=modern
- **最低权限**: 普通用户即可安装
- **压缩优化**: LZMA压缩，减小安装包体积

#### 🔸 用户选项
- **桌面图标**: 用户可选择是否创建
- **快速启动**: 支持Windows 6.1以下版本
- **开始菜单**: 自动创建程序组

#### 🔸 文件包含
- 主程序及所有依赖文件
- 递归包含_internal文件夹
- 自动创建所需目录结构

## ⚙️ 自定义配置

### 修改安装包名称
```ini
OutputBaseFilename=你的自定义名称
```

### 添加许可协议
```ini
LicenseFile=LICENSE.txt
```

### 修改安装目录
```ini
DefaultDirName={autopf}\你的应用名称
```

### 添加卸载信息
```ini
[UninstallDelete]
Type: filesandordirs; Name: "{app}\logs"
```

## 🎯 编译结果

### 成功编译后会生成：
- **安装包文件**: `Output/虎大王PDF重命名工具v2.0_安装包.exe`
- **大小**: 约50-100MB（压缩后）
- **安装时间**: 约1-2分钟

### 安装包特点：
- ✅ **专业外观**: 现代化安装界面
- ✅ **中文支持**: 完整的中文安装体验
- ✅ **一键安装**: 用户只需双击即可安装
- ✅ **卸载支持**: 支持完整卸载和清理
- ✅ **权限友好**: 无需管理员权限

## 🛠️ 故障排除

### 常见编译错误

**错误1: 找不到源文件**
```
解决: 确保dist文件夹存在且路径正确
检查: dist/虎大王PDF重命名工具v2/虎大王PDF重命名工具v2.exe
```

**错误2: 图标文件错误** 
```
解决: 确保pdf_renamer.ico文件存在
或注释掉: ;SetupIconFile=pdf_renamer.ico
```

**错误3: 编码问题**
```
解决: 确保setup.iss文件使用UTF-8编码保存
```

### 调试技巧

1. **查看详细日志**: Build → View Log
2. **语法检查**: Tools → Check Script Syntax
3. **预览安装**: 编译后测试安装过程

## 📦 分发建议

### 安装包文件命名
```
虎大王PDF重命名工具v2.0_安装包.exe
```

### 分发方式
1. **直接分发**: 单个exe文件，用户双击安装
2. **网盘分享**: 上传到百度网盘、阿里云盘等
3. **软件站发布**: 提交到各大软件下载站

### 安装包优势
- 🎯 **用户友好**: 标准的Windows安装体验
- 🛡️ **安全可靠**: 数字签名支持（如果有证书）
- 🔄 **版本管理**: 支持升级和卸载
- 📁 **自动配置**: 自动创建快捷方式和注册表项

---

**现在您可以制作专业的Windows安装包了！** 🎊

使用Inno Setup制作的安装包比ZIP便携版更专业，适合正式发布和分发。 