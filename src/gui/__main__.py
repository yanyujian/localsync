import sys
from PyQt5.QtWidgets import QApplication
from .main_window import SyncConfigWindow

def main():
    app = QApplication(sys.argv)
    window = SyncConfigWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main() 