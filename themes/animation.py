# src/launcher/animation.py
from datetime import datetime
import math

from PyQt5.QtGui import QColor


def animate_color(parent):
    if parent.target_color == QColor("green"):
        t = (math.sin(datetime.now().timestamp() * 4) + 1) / 2
        parent.current_color = QColor(0, int(128 + 127 * t), 0)
    else:
        r = parent.current_color.red() + (parent.target_color.red() - parent.current_color.red()) * 0.1
        g = parent.current_color.green() + (parent.target_color.green() - parent.current_color.green()) * 0.1
        b = parent.current_color.blue() + (parent.target_color.blue() - parent.current_color.blue()) * 0.1
        parent.current_color = QColor(int(r), int(g), int(b))
    parent.internet_indicator.setStyleSheet(f"background-color:{parent.current_color.name()}; border-radius:8px;")