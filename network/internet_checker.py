# src/launcher/internet_checker.py
import socket

from PyQt5.QtGui import QColor


def check_internet(parent):
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=2)
        parent.target_color = QColor("green")
    except:
        parent.target_color = QColor("red")
    parent.internet_status_label.setText("Online" if parent.target_color == QColor("green") else "Offline")