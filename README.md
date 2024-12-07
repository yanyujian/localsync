# Folder Synchronizer 文件夹同步工具

A real-time folder synchronization tool that monitors and replicates changes across multiple directories.
一个实时监控并在多个目录之间同步更改的文件夹同步工具。

## Features 功能特点

- Real-time monitoring of file system changes
  实时监控文件系统变化
- Synchronization of multiple folders
  多文件夹同步
- Support for file creation, modification, and deletion
  支持文件的创建、修改和删除
- Recursive handling of subdirectories
  递归处理子目录
- Cross-platform compatibility (Windows, Linux, macOS)
  跨平台兼容（Windows、Linux、macOS）
- Intelligent file conflict resolution
  智能文件冲突解决
- Protection against file corruption during editing
  编辑过程中的文件保护机制

## Installation 安装

1. Clone the repository 克隆仓库   ```bash
   git clone https://github.com/yourusername/folder-synchronizer.git
   cd folder-synchronizer   ```

2. Install dependencies 安装依赖   ```bash
   pip install -r requirements.txt   ```

## Configuration 配置

Create a `config.yaml` file in the root directory with your folder paths:
在根目录创建 `config.yaml` 文件，配置需要同步的文件夹路径：
