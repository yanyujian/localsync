# Folder Synchronizer 文件夹同步工具

A real-time folder synchronization tool that supports multiple folder groups, system tray operation, and automatic synchronization.
一个实时监控并在多个目录之间同步更改的文件夹同步工具。支持多组文件夹同步，系统托盘运行，自动同步等功能。

## Features 功能特点

- Real-time monitoring of file system changes
  实时监控文件系统变化
- Support for multiple folder group synchronization
  支持多组文件夹同步配置
- Synchronization of file creation, modification, and deletion
  支持文件的创建、修改和删除同步
- Recursive handling of subdirectories
  递归处理子目录
- Cross-platform compatibility (Windows, Linux, macOS)
  跨平台兼容（Windows、Linux、macOS）
- System tray operation, non-intrusive
  系统托盘运行，不打扰工作
- Intelligent file conflict resolution
  智能文件冲突解决
- File protection during editing
  编辑过程中的文件保护机制
- Multi-language support (English/Chinese, based on system language)
  支持中英文界面（根据系统语言自动选择）

## Installation 安装

1. Clone the repository 克隆仓库：   ```bash
   git clone https://github.com/yanyujian/localsync.git
   cd localsync   ```

2. Install dependencies 安装依赖：   ```bash
   pip install -r requirements.txt   ```

## Configuration 配置

Create a `config.yaml` file to configure synchronization folders. Two configuration methods are supported:
创建 `config.yaml` 文件来配置同步文件夹。支持两种配置方式：

1. Single group sync 单组同步：

```yaml
folders:
  - "D:/test_sync/folder1"
  - "D:/test_sync/folder2"
  - "D:/test_sync/folder3"
```

2. Multiple groups sync 多组同步：

```yaml
folder_groups:
  documents:  # Document sync group 文档同步组
    - "D:/test_sync/docs/work"
    - "D:/test_sync/docs/backup"
    - "D:/test_sync/docs/archive"
  
  source_code:  # Code sync group 代码同步组
    - "D:/test_sync/code/dev"
    - "D:/test_sync/code/backup"
  
  media:  # Media files sync group 媒体文件同步组
    - "D:/test_sync/media/photos"
    - "D:/test_sync/media/process"
    - "D:/test_sync/media/backup"
```

## Usage 使用方法

1. Start the program 启动程序：
   ```bash
   python -m src.gui
   ```

2. System Tray Operation 系统托盘操作：
   - Double-click tray icon: Show/hide main window
     双击托盘图标：显示/隐藏主窗口
   - Right-click tray icon: Access quick menu
     右键托盘图标：访问快捷菜单
     - Show/Hide Window 显示/隐藏窗口
     - Start/Stop Sync 开始/停止同步
     - Exit 退出程序

3. Main Interface Features 主界面功能：
   - Add/Remove sync groups
     添加/删除同步组
   - Add/Remove sync folders
     添加/删除同步文件夹
   - Start/Stop synchronization
     启动/停止同步
   - Save configuration
     保存配置

4. File Operations 文件操作：
   - Create, modify or delete files in any sync folder
     在任意同步文件夹中创建、修改或删除文件
   - Changes automatically sync to other folders in the same group
     变更会自动同步到同组的其他文件夹
   - Different groups are independent
     不同组之间的文件夹互不影响

## Safety Features 安全特性

1. File Protection 文件保护：
   - Files being edited won't be overwritten
     正在编辑的文件不会被同步覆盖
   - Deletion creates timestamped backup (e.g., file.txt.deleted.at20240101120000)
     删除操作会创建带时间戳的备份（例如：file.txt.deleted.at20240101120000）
   - Smart conflict handling based on timestamps and content
     基于时间戳和内容的智能冲突处理

2. Sync Control 同步控制：
   - Pause/Resume sync anytime
     可随时暂停/恢复同步
   - Auto restart after config changes
     配置修改后自动重启同步
   - Auto recovery from exceptions
     异常情况自动恢复

3. Data Safety 数据安全：
   - File content verification using MD5 hash
     使��� MD5 哈希验证文件内容
   - Deleted file history preservation
     保留删除文件的历史记录
   - Prevention of accidental data loss
     防止意外数据丢失

## Notes 注意事项

1. Path Guidelines 路径说明：
   - Use forward slashes (/) in paths
     使用正斜杠 (/) 分隔路径
   - Absolute paths recommended
     建议使用绝对路径
   - Ensure read/write permissions
     确保有读写权限

2. Performance Considerations 性能考虑：
   - More sync groups = More resources
     同步组越多，资源占用越大
   - Group folders reasonably
     建议根据需要合理分组
   - Pause unused sync groups
     可以随时暂停不需要的同步组

3. Common Issues 常见问题：
   - Check folder permissions if sync fails
     如果同步未生效，检查文件夹权限
   - Restart sync if program not responding
     如果程序无响应，可以重启同步
   - Save and restart sync after config changes
     配置文件修改后需要保存并重启同步

## Development 开发说明

Project Structure 项目结构：
```
folder_sync/
├── README.md
├── requirements.txt
├── config.yaml
├── src/
│   ├── __init__.py
│   ├── main.py          # Program entry 程序入口
│   ├── file_handler.py  # File operations 文件操作处理
│   ├── sync_manager.py  # Sync management 同步管理
│   ├── config_loader.py # Config loading 配置加载
│   └── gui/            # Graphical interface 图形界面
│       ├── __init__.py
│       ├── __main__.py
│       ├── main_window.py
│       ├── i18n.py
│       └── icons.py
└── tests/
    ├── __init__.py
    └── test_sync.py
```

## Requirements 环境要求

- Python 3.8+
- Dependencies 依赖包：
  - watchdog==3.0.0
  - pyyaml==6.0.1
  - PyQt5==5.15.9

## Contributing 贡献

Issues and Pull Requests are welcome. Please follow these steps:
欢迎提交 Issue 和 Pull Request。请遵循以下步骤：

1. Fork the repository 复刻仓库
2. Create your feature branch 创建特性分支
3. Commit your changes 提交更改
4. Push to the branch 推送到分支
5. Create a Pull Request 创建拉取请求

## License 许可证

This project is licensed under the MIT License.
本项目采用 MIT 许可证。

## Authors 作者

- yanyujian - Initial work 初始工作


