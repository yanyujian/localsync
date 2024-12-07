from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import Qt

def create_default_icon() -> QIcon:
    """创建一个简单的默认图标"""
    pixmap = QPixmap(32, 32)
    pixmap.fill(Qt.transparent)
    return QIcon(pixmap) 