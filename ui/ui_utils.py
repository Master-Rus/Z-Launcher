# src/launcher/ui_utils.py
import os
import sys

def resource_path(relative_path):
    """Получение абсолютного пути к ресурсу, работающего внутри PyInstaller exe"""
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)