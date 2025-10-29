# src/launcher/process_manager.py
import os
import subprocess as sp
import time

def check_running_process(parent):
    try:
        output = sp.check_output('sc query "zapret"', shell=True, text=True)
        parent.is_running = "RUNNING" in output
    except sp.CalledProcessError:
        parent.is_running = False
    parent.update_start_button()

def toggle_bat(parent):
    selected_display_name = parent.installed_version_combo.currentText()
    selected_file = parent.bat_mapping.get(selected_display_name)
    zapret_folder = os.path.join(os.path.dirname(__file__), "../zapret/start-service")
    bat_path = os.path.join(zapret_folder, selected_file) if selected_file else None

    service_name = "zapret"

    if parent.is_running:
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

        parent.is_running = False
        parent.update_start_button()
    else:
        if bat_path and os.path.exists(bat_path):
            sp.Popen(bat_path, shell=True)
            # is_running обновится через таймер

def update_start_button(parent):
    if parent.is_running:
        parent.play_button.setText("STOP")
        parent.play_button.setStyleSheet("""
            QPushButton {background-color:#ff4b4b; color:white; border-radius:5px; padding:8px;}
            QPushButton:hover {background-color:#ff0000;}
            QPushButton:pressed {background-color:#aa0000;}
        """)
    else:
        parent.play_button.setText("START")
        parent.play_button.setStyleSheet("""
            QPushButton {background-color:#4bb679; color:white; border-radius:5px; padding:8px;}
            QPushButton:hover { background-color:#6fcf88; }
            QPushButton:pressed { background-color:#339e5b; }
        """)