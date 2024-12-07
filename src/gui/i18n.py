import locale
import sys
from typing import Dict

class I18n:
    def __init__(self):
        # 获取系统语言
        self.system_lang = locale.getdefaultlocale()[0]
        
        # 翻译字典
        self.translations: Dict[str, Dict[str, str]] = {
            'en': {
                'window_title': "Folder Sync Configuration",
                'sync_groups': "Sync Groups",
                'add_group': "Add Group",
                'add_folder': "Add Folder",
                'remove': "Remove",
                'save_config': "Save Configuration",
                'start_sync': "Start Sync",
                'select_item': "Select an item to view details",
                'new_group': "New Group",
                'enter_group_name': "Enter group name:",
                'error': "Error",
                'success': "Success",
                'group_exists': "Group already exists!",
                'select_group': "Please select a group first!",
                'select_folder': "Select Folder",
                'config_saved': "Configuration saved successfully!",
                'failed_load': "Failed to load configuration",
                'failed_save': "Failed to save configuration",
                'failed_sync': "Failed to start sync",
                'group_info': "Group: {}\nFolders: {}",
                'folder_info': "Folder: {}",
                'default_group': "Default Group",
                'show_window': "Show Window",
                'quit': "Quit",
                'minimize_to_tray': "Application minimized to tray",
                'tray_tooltip': "Folder Synchronizer",
                'sync_started': "Synchronization is running",
                'sync_stopped': "Synchronization stopped",
                'sync_started_title': "Sync Started",
                'sync_started_message': "Folder synchronization has started",
                'stop_sync': "Stop Sync",
                'sync_status': "Sync Status",
                'hide_window': "Hide Window",
            },
            'zh': {
                'window_title': "文件夹同步配置",
                'sync_groups': "同步组",
                'add_group': "添加组",
                'add_folder': "添加文件夹",
                'remove': "删除",
                'save_config': "保存配置",
                'start_sync': "开始同步",
                'select_item': "选择一个项目查看详情",
                'new_group': "新建组",
                'enter_group_name': "请输入组名：",
                'error': "错误",
                'success': "成功",
                'group_exists': "组已存在！",
                'select_group': "请先选择一个组！",
                'select_folder': "选择文件夹",
                'config_saved': "配置保存成功！",
                'failed_load': "加载配置失败",
                'failed_save': "保存配置失败",
                'failed_sync': "启动同步失败",
                'group_info': "组：{}\n文件夹数：{}",
                'folder_info': "文件夹：{}",
                'default_group': "默认同步组",
                'show_window': "显示窗口",
                'quit': "退出",
                'minimize_to_tray': "应用程序已最��化到系统托盘",
                'tray_tooltip': "文件夹同步工具",
                'sync_started': "同步正在运行",
                'sync_stopped': "同步已停止",
                'sync_started_title': "同步已启动",
                'sync_started_message': "文件夹同步已开始运行",
                'stop_sync': "停止同步",
                'sync_status': "同步状态",
                'hide_window': "隐藏窗口",
            }
        }
        
        # 设置当前语言
        self.current_lang = 'en' if self.system_lang.startswith('en') else 'zh'
        
    def get(self, key: str, *args) -> str:
        """获取翻译文本"""
        text = self.translations[self.current_lang].get(key, key)
        if args:
            return text.format(*args)
        return text

# 创建全局翻译实例
i18n = I18n() 