# src/launcher/zlauncher.py
import os

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QComboBox, QGridLayout
from PyQt5.QtGui import QFont, QColor, QPainter, QBrush, QPen
from PyQt5.QtCore import Qt, QTimer, QRect, pyqtSlot, QPropertyAnimation

from themes.theme_loader import apply_theme
from ui.ui_utils import resource_path
from services.process_manager import check_running_process, toggle_bat, update_start_button
from network.internet_checker import check_internet
from themes.animation import animate_color
from section.about_dialog import show_about_dialog


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

        self.ping_timer = QTimer()
        self.ping_timer.timeout.connect(self.update_ping)
        self.ping_timer.start(5000)  # обновляем каждые 5 секунд
        QTimer.singleShot(2000, self.update_ping)  # задержанный вызов первого пинга

    def init_ui(self):
        self.setWindowTitle("≪Z≫-Launcher")
        self.setGeometry(100, 100, 400, 0)

        # Верхняя панель
        top_bar = QWidget()
        top_layout = QHBoxLayout()
        top_layout.setContentsMargins(10, 0, 10, 0)
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
        self.internet_indicator.setFixedSize(16, 16)
        self.internet_indicator.setStyleSheet("background-color: gray; border-radius: 6px;")

        self.internet_status_label = QLabel("Offline")
        self.internet_status_label.setStyleSheet("color:white; background-color:transparent;")

        self.min_button = QPushButton("-")
        self.min_button.setFixedSize(28, 28)
        self.min_button.clicked.connect(self.showMinimized)
        self.min_button.setStyleSheet("""
            QPushButton { color:white; background-color:#353535; border:none; border-radius:5px; }
            QPushButton:hover { background-color: #5a5a5a; }
            QPushButton:pressed { background-color: #2c2c2c; }
        """)

        self.close_button = QPushButton("x")
        self.close_button.setFixedSize(28, 28)
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
        installed_versions_label = QLabel("Доступные стратегии обхода:")
        installed_versions_label.setFont(QFont("Arial", 13))
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

        grid_layout = QGridLayout()
        self.settings_button = QPushButton("Настройки")
        self.about_button = QPushButton("About")
        self.about_button.clicked.connect(self.show_about_dialog)
        for idx, btn in enumerate([
            self.settings_button,
            self.about_button
        ]):
            btn.setStyleSheet("""
                QPushButton { background-color:#353535; color:white; border-radius:5px; padding:6px; }
                QPushButton:hover { background-color:#5a5a5a; }
                QPushButton:pressed { background-color:#2c2c2c; }
            """)
            grid_layout.addWidget(btn, 0, idx)
        buttons_layout.addLayout(grid_layout)
        buttons_layout.setAlignment(Qt.AlignTop)
        buttons_layout.setSpacing(10)

        main_layout = QVBoxLayout()
        main_layout.addWidget(top_bar)
        main_layout.addWidget(installed_versions_label)
        main_layout.addWidget(self.installed_version_combo)
        main_layout.addLayout(buttons_layout)

        # Пинг и Powered by
        powered_label = QLabel("Powered by Master-Rus")
        powered_label.setStyleSheet("color: gray; font-size: 10px;")
        powered_label.setAlignment(Qt.AlignRight)

        self.ping_label = QLabel("Loading ping...")
        self.ping_label.setStyleSheet("color: gray; font-size: 10px;")
        self.ping_label.setAlignment(Qt.AlignLeft)

        # Объединяем обе метки в один QHBoxLayout
        footer_layout = QHBoxLayout()
        footer_layout.addWidget(self.ping_label)
        footer_layout.addStretch()
        footer_layout.addWidget(powered_label)

        main_layout.addLayout(footer_layout)

        main_layout.setAlignment(Qt.AlignCenter)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(10, 10, 10, 10)
        self.setLayout(main_layout)

    def update_ping(self):
        from network.ping_checker import ping_host
        ping_host(callback=self)

    @pyqtSlot(object)
    def on_ping_result(self, ping_time):
        if ping_time is not None:
            formatted_ping = f"{int(ping_time)}"

            if ping_time < 100:
                color = "green"
            elif 100 <= ping_time <= 200:
                color = "yellow"
            else:
                color = "red"

            html_text = f"<span style='color: gray;'>Ping:</span> <span style='color: {color};'>{formatted_ping} ms</span>"
            self.ping_label.setText(html_text)
        else:
            html_text = "<span style='color: gray;'>Ping: --- ms</span>"
            self.ping_label.setText(html_text)
        self.ping_label.setStyleSheet("font-size: 10px;")

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        rect = QRect(0, 0, self.width(), self.height())
        painter.setBrush(QBrush(QColor(30, 30, 30)))
        painter.setPen(QPen(Qt.transparent))
        painter.drawRoundedRect(rect, 10, 10)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._offset = event.pos()

    def mouseMoveEvent(self, event):
        if self._offset and event.buttons() == Qt.LeftButton:
            self.move(self.pos() + event.pos() - self._offset)

    def mouseReleaseEvent(self, event):
        self._offset = None

    def check_running_process(self):
        check_running_process(self)

    def toggle_bat(self):
        toggle_bat(self)

    def update_start_button(self):
        update_start_button(self)

    def check_internet(self):
        check_internet(self)

    def animate_color(self):
        animate_color(self)

    def show_about_dialog(self):
        show_about_dialog(self)