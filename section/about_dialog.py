# src/launcher/about_dialog.py
import os
import json
import webbrowser
import requests
from PyQt5.QtCore import Qt, QRect
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QMessageBox, QApplication
from PyQt5.QtGui import QPainter, QColor, QBrush


def show_about_dialog(parent):
    version_file = os.path.join(os.path.dirname(__file__), "../version.json")
    try:
        with open(version_file, "r") as f:
            version = json.load(f).get("version", "unknown version")
    except Exception:
        version = "unknown version"

    dialog = AboutDialog(parent, version)  # ← передаём version
    dialog.exec_()


class AboutDialog(QDialog):
    def __init__(self, parent=None, version="unknown version"):
        super().__init__(parent)
        self.version = version  # ← сохраняем version в self.version

        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.resize(200, 110)

        # Стиль диалога
        self.setStyleSheet("""
            QDialog { background-color: #5c5b5b; border-radius: 10px; }
            QLabel { color: white; font-size: 14px; }
            QPushButton {
                background-color: #4bb679;
                color: white;
                border-radius: 5px;
                padding: 6px;
            }
            QPushButton:hover { background-color: #6fcf88; }
            QPushButton:pressed { background-color: #339e5b; }
        """)

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignLeft | Qt.AlignTop)

        title_label = QLabel("Z-Launcher")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(title_label)

        version_label = QLabel(f"Version: {self.version}")  # ← используем self.version
        layout.addWidget(version_label)

        buttons_layout = QHBoxLayout()
        updt_btn = QPushButton("Обновить")
        updt_btn.setStyleSheet("""
            QPushButton {
                background-color: #FFD700;
                color: black;
                border-radius: 5px;
                padding: 6px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #FFE55C; }
            QPushButton:pressed { background-color: #E6C200; }
        """)
        close_btn = QPushButton("Закрыть")
        close_btn.clicked.connect(self.accept)

        buttons_layout.addWidget(updt_btn)
        buttons_layout.addStretch()
        buttons_layout.addWidget(close_btn)

        layout.addLayout(buttons_layout)

        self.setLayout(layout)
        self.setFixedSize(200, 110)

        updt_btn.clicked.connect(lambda: self.check_update())

    def check_update(self):
        version_file = os.path.join(os.path.dirname(__file__), "../version.json")
        try:
            with open(version_file, "r") as f:
                local_version = json.load(f).get("version", "unknown version")
        except Exception:
            local_version = "unknown version"

        GITHUB_URL = "https://raw.githubusercontent.com/Master-Rus/Z-Launcher/main/version.json"
        RELEASE_PAGE = "https://github.com/Master-Rus/Z-Launcher/releases/latest"

        try:
            response = requests.get(GITHUB_URL, timeout=5)
            response.raise_for_status()
            data = response.json()
            remote_version = data.get("version", "unknown")
        except Exception as e:
            QMessageBox.warning(self, "Ошибка сети", f"Не удалось проверить обновления:\n{e}")
            return

        if remote_version == local_version:
            QMessageBox.information(self, "Обновлений нет", f"У вас уже установлена последняя версия.")
            return

        msg = QMessageBox(self)
        msg.setWindowTitle("Обновление доступно")
        msg.setText(f"Найдена новая версия: {remote_version}\nТекущая: {local_version}\n\nОбновить сейчас?")
        msg.setIcon(QMessageBox.Information)

        update_now_btn = msg.addButton("ДА", QMessageBox.AcceptRole)
        open_page_btn = msg.addButton("Открыть страницу релиза", QMessageBox.ActionRole)
        cancel_btn = msg.addButton("НЕТ", QMessageBox.RejectRole)

        msg.exec_()

        clicked = msg.clickedButton()
        if clicked == update_now_btn or clicked == open_page_btn:
            webbrowser.open(RELEASE_PAGE)

    def paintEvent(self, event):
        """
        Рисует фон с закруглёнными углами.
        """
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        rect = self.rect()

        # Фон окна
        painter.setBrush(QBrush(QColor(30, 30, 30)))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(rect, 10, 10)  # радиус закругления