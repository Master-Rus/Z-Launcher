from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtWidgets import QApplication
import json
import os

def apply_theme(file_path):
    if not os.path.exists(file_path):
        return
    with open(file_path, "r", encoding="utf-8") as f:
        theme = json.load(f)
    palette_config = theme.get("palette", {})
    palette = QPalette()
    role_map = {
        "Window": QPalette.Window, "WindowText": QPalette.WindowText,
        "Base": QPalette.Base, "AlternateBase": QPalette.AlternateBase,
        "ToolTipBase": QPalette.ToolTipBase, "ToolTipText": QPalette.ToolTipText,
        "Text": QPalette.Text, "Button": QPalette.Button, "ButtonText": QPalette.ButtonText,
        "BrightText": QPalette.BrightText, "Link": QPalette.Link,
        "Highlight": QPalette.Highlight, "HighlightedText": QPalette.HighlightedText
    }
    for k, v in palette_config.items():
        if k in role_map:
            palette.setColor(role_map[k], QColor(v))
    QApplication.setPalette(palette)
    if "stylesheet" in theme:
        QApplication.setStyleSheet(theme["stylesheet"])
