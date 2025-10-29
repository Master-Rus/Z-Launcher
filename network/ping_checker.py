# network/ping_checker.py
import platform
import subprocess
import threading  # ← добавлен
from PyQt5.QtCore import QMetaObject, Qt, Q_ARG


def ping_host(callback=None):
    def _run_ping():
        system = platform.system().lower()
        if system == "windows":
            command = ["ping", "-n", "1", "-w", "4000", "yandex.ru"]
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE
        else:
            command = ["ping", "-c", "1", "-W", "4", "yandex.ru"]
            startupinfo = None

        try:
            output_bytes = subprocess.check_output(
                command,
                stderr=subprocess.STDOUT,
                universal_newlines=False,
                startupinfo=startupinfo
            )
            try:
                output = output_bytes.decode('utf-8')
            except UnicodeDecodeError:
                output = output_bytes.decode('cp866', errors='ignore')

            result = parse_ping_output(output)
        except (subprocess.CalledProcessError, Exception):
            result = None

        if callback:
            QMetaObject.invokeMethod(
                callback,
                "on_ping_result",
                Qt.QueuedConnection,
                Q_ARG(object, result)
            )

    thread = threading.Thread(target=_run_ping)
    thread.start()


def parse_ping_output(output):
    """
    Парсит вывод команды ping и возвращает время ответа в миллисекундах.
    Поддерживает русскую и английскую локали Windows, а также Linux.
    """
    for line in output.strip().split("\n"):
        # Английская версия
        if "time=" in line.lower():
            parts = line.split("time=")
            if len(parts) < 2:
                continue
            time_part = parts[1].strip().split()[0]
            time_part = time_part.replace("ms", "").replace(",", ".").replace("<", "").strip()
            try:
                ping_time = float(time_part)
                return ping_time
            except ValueError:
                continue

        # Русская версия — только если есть "Ответ от"
        if "Ответ от" in line:
            if "время" in line:
                # Берём всё после "время="
                after_time = line.split("время=")[-1]
                # Берём первое слово (например, "68мс")
                time_part = after_time.strip().split()[0]
                time_part = time_part.replace("мс", "").replace(",", ".").replace("<", "").strip()
                try:
                    ping_time = float(time_part)
                    return ping_time
                except ValueError:
                    continue
    return None