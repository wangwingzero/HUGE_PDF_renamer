; 脚本由 Inno Setup 脚本向导生成
#define MyAppName "虎哥PDF重命名工具"
#define MyAppVersion "1.0"
#define MyAppPublisher "虎大王"
#define MyAppURL "mailto:86250887@qq.com"
#define MyAppExeName "虎哥PDF重命名工具.exe"

[Setup]
; 注: AppId的值为单独标识该应用程序。
; 不要为其他安装程序使用相同的AppId值。
AppId={{A1B2C3D4-E5F6-4747-8899-AABBCCDDEEFF}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
; 以下行修改为你的图标文件路径
SetupIconFile=pdf_renamer.ico
Compression=lzma
SolidCompression=yes
WizardStyle=modern
; 请求管理员权限
PrivilegesRequired=admin

[Languages]
Name: "chinesesimp"; MessagesFile: "compiler:Languages\ChineseSimplified.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "dist\虎哥PDF重命名工具.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\虎哥PDF重命名工具_右键菜单管理.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\安装右键菜单.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\卸载右键菜单.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "README.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "LICENSE"; DestDir: "{app}"; Flags: ignoreversion
; 注意: 不要在任何共享系统文件上使用"Flags: ignoreversion"

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\安装右键菜单"; Filename: "{app}\安装右键菜单.exe"
Name: "{group}\卸载右键菜单"; Filename: "{app}\卸载右键菜单.exe"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\安装右键菜单.exe"; Description: "安装右键菜单"; Flags: postinstall runascurrentuser
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[UninstallRun]
Filename: "{app}\卸载右键菜单.exe"; Flags: runascurrentuser 