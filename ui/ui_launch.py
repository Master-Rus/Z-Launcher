import os
import sys
import json
import math
import time
import socket
import subprocess as sp
import requests
import webbrowser
from datetime import datetime

from themes.theme_loader import apply_theme

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QGridLayout, QDialog, QMessageBox
)
from PyQt5.QtGui import QFont, QColor, QPainter, QBrush, QPen
from PyQt5.QtCore import Qt, QTimer, QRect


def resource_path(relative_path):
    """Получение абсолютного пути к ресурсу, работающего внутри PyInstaller exe"""
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

class Zlauncher(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self._offset = None
        self.is_running = False
        self.target_color = QColor("gray")
        self.current_color = QColor("gray")

        # Настройка темы
        self.config = {"Theme": "Dark.json", "ThemeBackground": False}
        theme_file_path = resource_path(os.path.join("themes", self.config["Theme"]))
        apply_theme(theme_file_path)

        self.init_ui()
        self.check_running_process()

        # Таймеры
        self.timer = QTimer()
        self.timer.timeout.connect(self.check_running_process)
        self.timer.start(2000)

        self.internet_timer = QTimer()
        self.internet_timer.timeout.connect(self.check_internet)
        self.internet_timer.start(3000)

        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self.animate_color)
        self.animation_timer.start(30)

        self.check_internet()

    def init_ui(self):
        self.setWindowTitle("≪Z≫-Launcher")
        self.setGeometry(100,100,420,0) #self.setGeometry(100,100,420,270)

        # Верхняя панель
        top_bar = QWidget()
        top_layout = QHBoxLayout()
        top_layout.setContentsMargins(10,0,10,0)
        top_bar.setLayout(top_layout)
        top_bar.setStyleSheet("""
            background-color: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #4b4b4b, stop:1 #1c1c1c);
            border-top-left-radius:10px; border-top-right-radius:10px;
        """)

        title_label = QLabel("≪Z≫ Launcher      ")
        title_label.setFont(QFont("Arial", 12, QFont.Bold))
        title_label.setStyleSheet("color:white;")
        title_label.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)

        self.internet_indicator = QLabel()
        self.internet_indicator.setFixedSize(16,16)
        self.internet_indicator.setStyleSheet("background-color: gray; border-radius: 6px;")

        self.internet_status_label = QLabel("Offline")
        self.internet_status_label.setStyleSheet("color:white; background-color:transparent;")

        self.min_button = QPushButton("-")
        self.min_button.setFixedSize(28,28)
        self.min_button.clicked.connect(self.showMinimized)
        self.min_button.setStyleSheet("""
            QPushButton { color:white; background-color:#353535; border:none; border-radius:5px; }
            QPushButton:hover { background-color: #5a5a5a; }
            QPushButton:pressed { background-color: #2c2c2c; }
        """)

        self.close_button = QPushButton("x")
        self.close_button.setFixedSize(28,28)
        self.close_button.clicked.connect(self.close)
        self.close_button.setStyleSheet("""
            QPushButton { color:white; background-color:#ff4b4b; border:none; border-radius:5px; }
            QPushButton:hover { background-color:#ff0000; }
            QPushButton:pressed { background-color:#aa0000; }
        """)

        top_layout.addWidget(title_label)
        top_layout.addStretch()
        top_layout.addWidget(self.internet_indicator)
        top_layout.addWidget(self.internet_status_label)
        top_layout.addWidget(self.min_button)
        top_layout.addWidget(self.close_button)

        # Доступные обходы
        installed_versions_label = QLabel("Доступные обходы:")
        installed_versions_label.setFont(QFont("Arial", 14))
        installed_versions_label.setAlignment(Qt.AlignCenter)

        self.installed_version_combo = QComboBox()
        self.installed_version_combo.setMinimumWidth(200)
        self.installed_version_combo.setStyleSheet("""
            QComboBox {padding:5px; text-align:center; background-color:#2c2c2c; color:white; border-radius:5px;}
            QComboBox QAbstractItemView {background-color:#2c2c2c; selection-background-color:#4bb679; color:white;}
        """)

        zapret_folder = resource_path(os.path.join("zapret", "start-service"))
       
        # Определяем порядок и отображаемые имена
        bat_order = [
            ("Вариант 1", "START-v1.bat"),
            ("Вариант 2", "START-v2.bat"),
            ("Вариант 3", "START-v3.bat"),
            ("Вариант 4", "START-v4.bat"),
            ("Вариант 5", "START-v5.bat"),
            ("Вариант 6", "START-v6.bat"),
            ("МГТС", "START-МГТС.bat"),
            ("МГТС-2", "START-МГТС-2.bat"),
            ("Only-Discord", "START-Only-Discord.bat"),
            ("FAKE-TLS-MOD", "START-FAKE-TLS-MOD.bat")
        ]
        
        self.bat_mapping = {}
        combo_items = []
        
        for display_name, file_name in bat_order:
            file_path = os.path.join(zapret_folder, file_name)
            if os.path.exists(file_path):
                self.bat_mapping[display_name] = file_name
                combo_items.append(display_name)

        # Обновляем ComboBox только один раз
        self.installed_version_combo.clear()
        self.installed_version_combo.addItems(combo_items)
        self.installed_version_combo.setCurrentIndex(0)  # всегда первый выбран

        # Кнопки
        buttons_layout = QVBoxLayout()
        self.play_button = QPushButton("START")
        self.play_button.clicked.connect(self.toggle_bat)
        self.play_button.setStyleSheet("""
            QPushButton {background-color:#4bb679; color:white; border-radius:5px; padding:8px;}
            QPushButton:hover { background-color:#6fcf88; }
            QPushButton:pressed { background-color:#339e5b; }
        """)
        buttons_layout.addWidget(self.play_button)
        
        #Доп.кнопки
        # for name in ["Coming Soon","Coming Soon","Coming Soon"]:
            # btn = QPushButton(name)
            # btn.setStyleSheet("""
                # QPushButton { background-color:#353535; color:white; border-radius:5px; padding:6px; }
                # QPushButton:hover { background-color:#5a5a5a; }
                # QPushButton:pressed { background-color:#2c2c2c; }
            # """)
            # buttons_layout.addWidget(btn)

        grid_layout = QGridLayout()
        self.settings_button = QPushButton("Настройки") #Кнопка настроек
        self.about_button = QPushButton("About")
        self.about_button.clicked.connect(self.show_about_dialog)
        for idx, btn in enumerate([
            self.settings_button, #Кнопка настроек
            self.about_button
        ]):
            btn.setStyleSheet("""
                QPushButton { background-color:#353535; color:white; border-radius:5px; padding:6px; }
                QPushButton:hover { background-color:#5a5a5a; }
                QPushButton:pressed { background-color:#2c2c2c; }
            """)
            grid_layout.addWidget(btn,0,idx)
        buttons_layout.addLayout(grid_layout)
        buttons_layout.setAlignment(Qt.AlignTop)
        buttons_layout.setSpacing(10)

        main_layout = QVBoxLayout()
        main_layout.addWidget(top_bar)
        main_layout.addWidget(installed_versions_label)
        main_layout.addWidget(self.installed_version_combo)
        main_layout.addLayout(buttons_layout)
        main_layout.setAlignment(Qt.AlignCenter)
        main_layout.setSpacing(15)
        self.setLayout(main_layout)

    # --- События мыши ---
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        rect = QRect(0,0,self.width(),self.height())
        painter.setBrush(QBrush(QColor(30,30,30)))
        painter.setPen(QPen(Qt.transparent))
        painter.drawRoundedRect(rect, 10,10)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._offset = event.pos()
    def mouseMoveEvent(self, event):
        if self._offset and event.buttons() == Qt.LeftButton:
            self.move(self.pos() + event.pos() - self._offset)
    def mouseReleaseEvent(self, event):
        self._offset = None

    # --- Процесс ---
    def check_running_process(self):
        try:
            output = sp.check_output('sc query "zapret"', shell=True, text=True)
            self.is_running = "RUNNING" in output
        except sp.CalledProcessError:
            self.is_running = False
        self.update_start_button()

    def toggle_bat(self):
        selected_display_name = self.installed_version_combo.currentText()
        selected_file = self.bat_mapping.get(selected_display_name)
        zapret_folder = os.path.join(os.path.dirname(__file__), "../zapret/start-service")
        bat_path = os.path.join(zapret_folder, selected_file) if selected_file else None

        service_name = "zapret"

        if self.is_running:
            # Останавливаем сервис
            sp.call(f'sc stop "{service_name}"', shell=True)

            # Ждём пока сервис полностью остановится
            timeout = 3  # секунд
            interval = 1
            elapsed = 0
            while elapsed < timeout:
                result = sp.run(f'sc query "{service_name}"', shell=True, capture_output=True, text=True)
                if "STATE              : 1  STOPPED" in result.stdout:
                    break
                time.sleep(interval)
                elapsed += interval

            # Удаляем сервис
            sp.call(f'sc delete "{service_name}"', shell=True)

            self.is_running = False
            self.update_start_button()
        else:
            if bat_path and os.path.exists(bat_path):
                sp.Popen(bat_path, shell=True)
                # is_running обновится через таймер

    def update_start_button(self):
        if self.is_running:
            self.play_button.setText("STOP")
            self.play_button.setStyleSheet("""
                QPushButton {background-color:#ff4b4b; color:white; border-radius:5px; padding:8px;}
                QPushButton:hover {background-color:#ff0000;}
                QPushButton:pressed {background-color:#aa0000;}
            """)
        else:
            self.play_button.setText("START")
            self.play_button.setStyleSheet("""
                QPushButton {background-color:#4bb679; color:white; border-radius:5px; padding:8px;}
                QPushButton:hover { background-color:#6fcf88; }
                QPushButton:pressed { background-color:#339e5b; }
            """)

    # --- Интернет ---
    def check_internet(self):
        try:
            socket.create_connection(("8.8.8.8", 53), timeout=2)
            self.target_color = QColor("green")
        except:
            self.target_color = QColor("red")
        self.internet_status_label.setText("Online" if self.target_color==QColor("green") else "Offline")

    def animate_color(self):
        if self.target_color==QColor("green"):
            t = (math.sin(datetime.now().timestamp()*4)+1)/2
            self.current_color = QColor(0,int(128+127*t),0)
        else:
            r = self.current_color.red() + (self.target_color.red()-self.current_color.red())*0.1
            g = self.current_color.green() + (self.target_color.green()-self.current_color.green())*0.1
            b = self.current_color.blue() + (self.target_color.blue()-self.current_color.blue())*0.1
            self.current_color = QColor(int(r),int(g),int(b))
        self.internet_indicator.setStyleSheet(f"background-color:{self.current_color.name()}; border-radius:8px;")

    def show_about_dialog(self):
        version_file = resource_path("version.json")
        try:
            with open(version_file, "r") as f:
                version = json.load(f).get("version", "unknown version")
        except:
            version = "unknown version"

        dialog = QDialog(self)
        #dialog.setWindowTitle("Zzzz")
        dialog.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        dialog.setStyleSheet("""
            QDialog { background-color: #2c2c2c; border-radius: 10px; }
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
        
        def check_update(self):
            version_file = resource_path("version.json")
            try:
                with open(version_file, "r") as f:
                    local_version = json.load(f).get("version", "unknown version")
            except:
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
                QMessageBox.information(self, "Обновлений нет", f"У тебя уже последняя версия: {local_version}.")
                return

            # Создаем QMessageBox
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
            # cancel_btn просто закрывает окно

        layout = QVBoxLayout()
        label = QLabel(f"Z-Launcher\n\nVersion: {version}\n\nPowered by Master-Rus")
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)

        updt_btn = QPushButton("Обновить")
        updt_btn.setStyleSheet("""
            QPushButton {
            background-color: #FFD700;  /* ярко-жёлтый */
                color: black;
                border-radius: 5px;
                padding: 6px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #FFE55C; }
            QPushButton:pressed { background-color: #E6C200; }
        """)

        close_btn = QPushButton("Закрыть")
        close_btn.clicked.connect(dialog.accept)
        updt_btn.clicked.connect(lambda: check_update(dialog))

        layout.addWidget(updt_btn, alignment=Qt.AlignCenter)
        layout.addWidget(close_btn, alignment=Qt.AlignCenter)

        dialog.setLayout(layout)
        dialog.setFixedSize(300, 200)
        dialog.exec_()


