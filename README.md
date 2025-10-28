<div align="center">

# Z-Launcher
# <img src="https://github.com/Master-Rus/Z-Launcher/blob/main/ui/screen.png" />


Альтернатива https://github.com/bol-van/zapret-win-bundle  
Используются скрипты из https://github.com/Flowseal/zapret-discord-youtube  
Также вы можете материально поддержать оригинального разработчика zapret [тут](https://github.com/bol-van/zapret?tab=readme-ov-file#%D0%BF%D0%BE%D0%B4%D0%B4%D0%B5%D1%80%D0%B6%D0%B0%D1%82%D1%8C-%D1%80%D0%B0%D0%B7%D1%80%D0%B0%D0%B1%D0%BE%D1%82%D1%87%D0%B8%D0%BA%D0%B0)
</div>

> [!WARNING]
>
> ### АНТИВИРУСЫ
> WinDivert может вызвать реакцию антивируса.
> WinDivert - это инструмент для перехвата и фильтрации трафика, необходимый для работы zapret.
> Замена iptables и NFQUEUE в Linux, которых нет под Windows.
> Он может использоваться как хорошими, так и плохими программами, но сам по себе не является вирусом.
> Драйвер WinDivert64.sys подписан для возможности загрузки в 64-битное ядро Windows.
> Но антивирусы склонны относить подобное к классам повышенного риска или хакерским инструментам.
> В случае проблем используйте исключения или выключайте антивирус совсем.
>
> **Выдержка из [`readme.md`](https://github.com/bol-van/zapret-win-bundle/blob/master/readme.md#%D0%B0%D0%BD%D1%82%D0%B8%D0%B2%D0%B8%D1%80%D1%83%D1%81%D1%8B) репозитория [bol-van/zapret-win-bundle](https://github.com/bol-van/zapret-win-bundle)*

> [!IMPORTANT]
> Все бинарные файлы в папке [`bin`](./zapret/start-service/bin) взяты из [zapret-win-bundle/zapret-winws](https://github.com/bol-van/zapret-win-bundle/tree/master/zapret-winws). Вы можете это проверить с помощью хэшей/контрольных сумм. Проверяйте, что запускаете, используя сборки из интернета!

## ⚙️Использование(Easy)

1. Включите Secure DNS. В Chrome - "Использовать безопасный DNS", и выбрать поставщика услуг DNS (выбрать вариант, отличный от поставщика по умолчанию). В Firefox - "Включить DNS через HTTPS, используя: Максимальную защиту"
    * В **Windows 11** поддерживается включение Secure DNS прямо в настройках - [инструкция тут](https://www.howtogeek.com/765940/how-to-enable-dns-over-https-on-windows-11/). Рекомендуется, если вы пользуетесь Windows 11

2. Загрузите Z-Launcher.exe со [страницы последнего релиза](https://github.com/Master-Rus/Z-Launcher/releases/latest)

3. Запустите ранее скачанный Z-Launcher.exe от имени Администратора

4. Выберите вариант обхода и нажмите "START"

## ⚙️Использование(Ручная сборка)

1. Установите [Python(3.13)](https://www.python.org/downloads/) или более поздние версии.

2. Обновите PiP 
```cmd
python -m pip install --upgrade pip
```
3. Установите PyInstaller
```cmd
python -m pip install pyinstaller
```
4. Установите модули
```cmd
pip install -r requirements.txt
```
5. Соберите проект
```cmd
pyinstaller --noconsole --onefile --icon=launcher_icon.ico --add-data "themes;themes" --add-data "launcher_icon.ico;." --add-data "zapret;zapret" --add-data "version.json;." Launcher.py
```
6. Запустите Z-Launcher из .\dist от имени Администратора

7. Выполните 1-й, затем 4-й пункт из [⚙️Использование(Easy)](https://github.com/Master-Rus/Z-Launcher#%EF%B8%8F%D0%B8%D1%81%D0%BF%D0%BE%D0%BB%D1%8C%D0%B7%D0%BE%D0%B2%D0%B0%D0%BD%D0%B8%D0%B5easy)

## ☑️Распространенные вопросы и проблемы

### Обход не работает / перестал работать

> [!IMPORTANT]
> **Стратегии блокировок со временем изменяются.**
> Определенная стратегия обхода zapret может работать какое-то время, но если меняется способ блокировки или обнаружения обхода блокировки, то она перестанет работать.

- Убедитесь, что адрес ресурса записан в списках доменов или IP

- Проверьте другие стратегии (**`ALT`**/**`FAKE`** и другие)

### Античит ругается на WinDivert

- Прочитайте инструкцию тут - https://github.com/bol-van/zapret-win-bundle/tree/master/windivert-hide

### Требуется цифровая подпись драйвера WinDivert (Windows 7)

- Замените файлы `WinDivert.dll` и `WinDivert64.sys` в папке [`bin`](./zapret/start-service/bin) на одноименные из [zapret-win-bundle/win7](https://github.com/bol-van/zapret-win-bundle/tree/master/win7)
- Пересоберите приложение

### При нажатии на STOP, WinDivert остается в службах

1. Узнайте название службы с помощью команды, в командной строке Windows (Win+R, `cmd`):

```cmd
driverquery | find "Divert"
```

2. Остановите и удалите службу командами:

```cmd
sc stop название_из_первого_шага

sc delete название_из_первого_шага
```

### Не работает <img src="https://cdn-icons-png.flaticon.com/128/5968/5968756.png" height=18 /> Discord

- См. [#252](https://github.com/Flowseal/zapret-discord-youtube/discussions/252)

### Не работает <img src="https://cdn-icons-png.flaticon.com/128/1384/1384060.png" height=18 /> YouTube

- См. [#251](https://github.com/Flowseal/zapret-discord-youtube/discussions/251)

### Не нашли своей проблемы

* Создайте её [тут](https://github.com/Flowseal/zapret-discord-youtube/issues)

## 🗒️Добавление адресов прочих заблокированных ресурсов

Список блокирующихся адресов для обхода можно расширить, добавляя их в:
- [`list-general.txt`](./zapret/start-service/list-general.txt) для доменов (поддомены автоматически учитываются), IP и подсетей

## ⭐Поддержка проекта

Вы можете поддержать проект, поставив :star: этому репозиторию (сверху справа этой страницы)

Также вы можете материально поддержать оригинального разработчика zapret [тут](https://github.com/bol-van/zapret?tab=readme-ov-file#%D0%BF%D0%BE%D0%B4%D0%B4%D0%B5%D1%80%D0%B6%D0%B0%D1%82%D1%8C-%D1%80%D0%B0%D0%B7%D1%80%D0%B0%D0%B1%D0%BE%D1%82%D1%87%D0%B8%D0%BA%D0%B0)


## ⚖️Лицензирование

Проект распространяется на условиях лицензии [GPL-3.0 license](https://github.com/Master-Rus/Z-Launcher/blob/main/LICENSE)

💖 Отдельная благодарность разработчику [zapret](https://github.com/bol-van/zapret) - [bol-van](https://github.com/bol-van)
