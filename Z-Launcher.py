import os
import sys
import ctypes
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QSystemTrayIcon

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_as_admin():
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
    sys.exit()

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

if __name__ == "__main__":
    if not is_admin():
        run_as_admin()
        sys.exit()
    app = QApplication(sys.argv)

    icon_path = resource_path("launcher_icon.ico")

    tray_icon = QSystemTrayIcon(QIcon(icon_path))
    tray_icon.show()  # показываем в трее
    app.setWindowIcon(QIcon(icon_path))  # для окна приложения

    from ui.ui_launch import Zlauncher
    window = Zlauncher()
    window.show()

    sys.exit(app.exec_())
