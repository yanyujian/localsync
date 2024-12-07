from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                           QPushButton, QTreeWidget, QTreeWidgetItem, QLabel, 
                           QFileDialog, QInputDialog, QMessageBox, QSystemTrayIcon, QMenu, QApplication)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QIcon
import yaml
from pathlib import Path
import logging
import asyncio
from .i18n import i18n
from .icons import create_default_icon

logger = logging.getLogger(__name__)

class SyncThread(QThread):
    error_occurred = pyqtSignal(str)
    status_changed = pyqtSignal(str)
    
    def __init__(self, config_data):
        super().__init__()
        self.config_data = config_data
        self._is_running = True
        self._loop = None
        self._current_task = None

    def run(self):
        try:
            from ..main import main
            self.status_changed.emit(i18n.get('sync_started'))
            
            # 创建新的事件循环
            self._loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self._loop)
            
            while self._is_running:
                try:
                    # 创建并保存当前任务的引用
                    self._current_task = self._loop.create_task(main())
                    
                    # 等待任务完成或被取消
                    try:
                        self._loop.run_until_complete(self._current_task)
                    except asyncio.CancelledError:
                        logger.info("Sync task was cancelled")
                        break
                    
                    # 如果已经请求停止，则退出循环
                    if not self._is_running:
                        break
                    
                    # 添加短暂延迟
                    try:
                        self._loop.run_until_complete(asyncio.sleep(0.1))
                    except asyncio.CancelledError:
                        break
                        
                except Exception as e:
                    self.error_occurred.emit(str(e))
                    logger.error(f"Error in sync task: {str(e)}")
                    break
            
        except Exception as e:
            self.error_occurred.emit(str(e))
            logger.error(f"Error in sync thread: {str(e)}")
        finally:
            self._cleanup()

    def _cleanup(self):
        """清理资源"""
        try:
            if self._current_task and not self._current_task.done():
                self._current_task.cancel()
                
            if self._loop and self._loop.is_running():
                # 取消所有待处理的任务
                for task in asyncio.all_tasks(self._loop):
                    task.cancel()
                    try:
                        self._loop.run_until_complete(task)
                    except (asyncio.CancelledError, Exception):
                        pass
                        
            if self._loop:
                try:
                    # 运行一次事件循环以确保所有任务都被清理
                    self._loop.run_until_complete(asyncio.sleep(0))
                except Exception:
                    pass
                finally:
                    self._loop.close()
                    self._loop = None
                    
        except Exception as e:
            logger.error(f"Error during cleanup: {str(e)}")
        finally:
            self.status_changed.emit(i18n.get('sync_stopped'))

    def stop(self):
        """停止同步进程"""
        self._is_running = False
        try:
            if self._current_task and not self._current_task.done():
                self._current_task.cancel()
                
            if self._loop and self._loop.is_running():
                self._loop.call_soon_threadsafe(self._loop.stop)
        except Exception as e:
            logger.error(f"Error stopping sync thread: {str(e)}")

class SyncConfigWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(i18n.get('window_title'))
        self.setMinimumSize(800, 600)
        
        self.config_data = {
            'folders': [],
            'folder_groups': {}
        }
        
        self.sync_thread = None
        self.init_ui()
        self.init_tray()
        self.load_config()
        
        # 确保在显示托盘图标后再隐藏主窗口
        QThread.msleep(100)  # 短暂延迟确保托盘图标已显示
        self.hide()
        # 启动同步
        self.start_sync(show_message=True)

    def init_tray(self):
        """初始化系统托盘"""
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(create_default_icon())
        self.tray_icon.setToolTip(i18n.get('tray_tooltip'))
        
        # 创建托盘菜单
        self.tray_menu = QMenu()
        
        # 显示/隐藏窗口动作
        self.show_action = self.tray_menu.addAction(i18n.get('show_window'))
        self.show_action.triggered.connect(self.toggle_window)
        
        self.tray_menu.addSeparator()
        
        # 同步状态显示
        self.sync_status_action = self.tray_menu.addAction(i18n.get('sync_stopped'))
        self.sync_status_action.setEnabled(False)
        
        # 同步控制按钮
        self.start_sync_action = self.tray_menu.addAction(i18n.get('start_sync'))
        self.start_sync_action.triggered.connect(lambda: self.start_sync(True))
        
        self.stop_sync_action = self.tray_menu.addAction(i18n.get('stop_sync'))
        self.stop_sync_action.triggered.connect(self.stop_sync)
        self.stop_sync_action.setVisible(False)
        
        self.tray_menu.addSeparator()
        
        # 退出按钮
        quit_action = self.tray_menu.addAction(i18n.get('quit'))
        quit_action.triggered.connect(self.quit_application)
        
        self.tray_icon.setContextMenu(self.tray_menu)
        self.tray_icon.activated.connect(self.tray_icon_activated)
        self.tray_icon.show()

    def toggle_window(self):
        """切换窗口显示状态"""
        if self.isVisible():
            self.hide()
            self.show_action.setText(i18n.get('show_window'))
        else:
            self.show()
            self.activateWindow()
            self.show_action.setText(i18n.get('hide_window'))

    def tray_icon_activated(self, reason):
        """处理托盘图标的点击事件"""
        if reason == QSystemTrayIcon.DoubleClick:
            self.toggle_window()

    def save_config(self):
        """保存配置到文件并重启同步"""
        try:
            # 先停止当前同步
            if self.sync_thread and self.sync_thread.isRunning():
                self.stop_sync()
                # 等待确保完全停止
                QThread.msleep(2000)  # 增加等待时间到2秒
            
            # 保存配置
            with open('config.yaml', 'w', encoding='utf-8') as f:
                yaml.safe_dump(self.config_data, f, allow_unicode=True)
            
            # 等待一段时间后启动新的同步
            QThread.msleep(500)
            self.start_sync(show_message=True)
            
            QMessageBox.information(self, i18n.get('success'), i18n.get('config_saved'))
        except Exception as e:
            logger.error(f"{i18n.get('failed_save')}: {e}")
            QMessageBox.warning(self, i18n.get('error'), f"{i18n.get('failed_save')}: {e}")

    def restart_sync(self):
        """重启同步进程"""
        self.stop_sync()
        self.start_sync(show_message=False)

    def start_sync(self, show_message=True):
        """在单独的线程中启动同步进程"""
        if self.sync_thread is None or not self.sync_thread.isRunning():
            self.sync_thread = SyncThread(self.config_data)
            self.sync_thread.error_occurred.connect(self.handle_sync_error)
            self.sync_thread.status_changed.connect(self.update_sync_status)
            
            # 更新按钮状态
            self.sync_btn.setText(i18n.get('stop_sync'))
            self.start_sync_action.setVisible(False)
            self.stop_sync_action.setVisible(True)
            
            self.sync_thread.start()
            
            if show_message:
                self.tray_icon.showMessage(
                    i18n.get('sync_started_title'),
                    i18n.get('sync_started_message'),
                    QSystemTrayIcon.Information,
                    2000
                )

    def stop_sync(self):
        """停止同步进程"""
        if self.sync_thread and self.sync_thread.isRunning():
            self.sync_thread.stop()
            # 给一个更长的超时时间
            if not self.sync_thread.wait(2000):  # 等待2秒
                logger.warning("Sync thread did not stop gracefully")
                self.sync_thread.terminate()  # 强制终止
                self.sync_thread.wait()
            
            # 更新按钮状态
            self.sync_btn.setText(i18n.get('start_sync'))
            self.start_sync_action.setVisible(True)
            self.stop_sync_action.setVisible(False)
            
            self.update_sync_status(i18n.get('sync_stopped'))

    def update_sync_status(self, status: str):
        """更新同步状态"""
        self.sync_status_action.setText(status)
        self.details_label.setText(status)

    def quit_application(self):
        """退出应用程序"""
        self.stop_sync()
        QApplication.quit()

    def closeEvent(self, event):
        """重写关闭事件，使窗口隐藏而不是退出"""
        if self.tray_icon.isVisible():
            self.hide()
            event.ignore()
        else:
            event.accept()

    def handle_sync_error(self, error_msg):
        """处理同步错误"""
        # 只记录日志，不显示错误对话框
        logger.error(f"Sync error occurred: {error_msg}")
        # 更新按钮状态
        self.sync_btn.setText(i18n.get('start_sync'))

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QHBoxLayout(central_widget)

        # 左侧树形视图
        tree_layout = QVBoxLayout()
        self.tree = QTreeWidget()
        self.tree.setHeaderLabel(i18n.get('sync_groups'))
        tree_layout.addWidget(self.tree)

        # 左侧按钮组
        button_layout = QHBoxLayout()
        self.add_group_btn = QPushButton(i18n.get('add_group'))
        self.add_folder_btn = QPushButton(i18n.get('add_folder'))
        self.remove_btn = QPushButton(i18n.get('remove'))
        
        button_layout.addWidget(self.add_group_btn)
        button_layout.addWidget(self.add_folder_btn)
        button_layout.addWidget(self.remove_btn)
        
        tree_layout.addLayout(button_layout)
        layout.addLayout(tree_layout)

        # 右侧详情和操作区
        details_layout = QVBoxLayout()
        self.details_label = QLabel(i18n.get('select_item'))
        details_layout.addWidget(self.details_label)

        # 保存和启动按钮
        action_layout = QHBoxLayout()
        self.save_btn = QPushButton(i18n.get('save_config'))
        self.sync_btn = QPushButton(i18n.get('start_sync'))
        
        action_layout.addWidget(self.save_btn)
        action_layout.addWidget(self.sync_btn)
        
        details_layout.addLayout(action_layout)
        layout.addLayout(details_layout)

        # 连接信号
        self.add_group_btn.clicked.connect(self.add_group)
        self.add_folder_btn.clicked.connect(self.add_folder)
        self.remove_btn.clicked.connect(self.remove_item)
        self.save_btn.clicked.connect(self.save_config)
        self.sync_btn.clicked.connect(self.toggle_sync)
        self.tree.itemSelectionChanged.connect(self.update_details)

    def load_config(self):
        try:
            with open('config.yaml', 'r', encoding='utf-8') as f:
                self.config_data = yaml.safe_load(f) or {'folders': [], 'folder_groups': {}}
            self.update_tree()
        except Exception as e:
            logger.error(f"{i18n.get('failed_load')}: {e}")
            QMessageBox.warning(self, i18n.get('error'), f"{i18n.get('failed_load')}: {e}")

    def update_tree(self):
        self.tree.clear()
        
        # 添加默认同步组
        default_group = QTreeWidgetItem(self.tree, [i18n.get('default_group')])
        for folder in self.config_data.get('folders', []):
            QTreeWidgetItem(default_group, [str(folder)])
        
        # 添加其他同步组
        for group_name, folders in self.config_data.get('folder_groups', {}).items():
            group_item = QTreeWidgetItem(self.tree, [group_name])
            for folder in folders:
                QTreeWidgetItem(group_item, [str(folder)])
        
        self.tree.expandAll()

    def add_group(self):
        name, ok = QInputDialog.getText(
            self, 
            i18n.get('new_group'),
            i18n.get('enter_group_name')
        )
        if ok and name:
            if name not in self.config_data['folder_groups']:
                self.config_data['folder_groups'][name] = []
                self.update_tree()
            else:
                QMessageBox.warning(self, i18n.get('error'), i18n.get('group_exists'))

    def add_folder(self):
        selected = self.tree.selectedItems()
        if not selected:
            QMessageBox.warning(self, i18n.get('error'), i18n.get('select_group'))
            return

        folder = QFileDialog.getExistingDirectory(self, i18n.get('select_folder'))
        if folder:
            item = selected[0]
            if item.parent() is None:  # 是组节点
                group_name = item.text(0)
                if group_name == i18n.get('default_group'):
                    self.config_data['folders'].append(folder)
                else:
                    self.config_data['folder_groups'][group_name].append(folder)
                self.update_tree()

    def remove_item(self):
        """删除选中的项目"""
        selected = self.tree.selectedItems()
        if not selected:
            return

        item = selected[0]
        if item.parent() is None:  # 组节点
            group_name = item.text(0)
            if group_name == i18n.get('default_group'):
                self.config_data['folders'] = []
            else:
                del self.config_data['folder_groups'][group_name]
        else:  # 文件夹节点
            group_item = item.parent()
            folder_path = item.text(0)
            if group_item.text(0) == i18n.get('default_group'):
                self.config_data['folders'].remove(folder_path)
            else:
                self.config_data['folder_groups'][group_item.text(0)].remove(folder_path)

        self.update_tree()

    def update_details(self):
        selected = self.tree.selectedItems()
        if not selected:
            self.details_label.setText(i18n.get('select_item'))
            return

        item = selected[0]
        if item.parent() is None:  # 组节点
            group_name = item.text(0)
            if group_name == i18n.get('default_group'):
                folders = self.config_data['folders']
            else:
                folders = self.config_data['folder_groups'][group_name]
            self.details_label.setText(i18n.get('group_info', group_name, len(folders)))
        else:  # 文件夹节点
            folder_path = item.text(0)
            self.details_label.setText(i18n.get('folder_info', folder_path))

    def toggle_sync(self):
        """切换同步状态"""
        if self.sync_thread and self.sync_thread.isRunning():
            self.stop_sync()
        else:
            self.start_sync()