### Telegram-бот
Телеграм-бот, который обращается к API сервиса Практикум.Домашка и узнает статус вашей домашней работы.

### Стэк Технологий.
- Python 3.9
- python-telegram-bot==13.7
- requests
- logging
- Errors and Exceptions
- python-dotenv


### Как запустить проект:

Клонировать репозиторий и перейти в него в командной строке:

```
git clone git@github.com:AndreyZyuzin/homework_bot.git
```

```
cd homework_bot
```

Cоздать и активировать виртуальное окружение:

```
python3 -m venv env
```

* Если у вас Linux/macOS

    ```
    source env/bin/activate
    ```

* Если у вас windows

    ```
    source env/scripts/activate
    ```

```
python3 -m pip install --upgrade pip
```

Установить зависимости из файла requirements.txt:

```
pip install -r requirements.txt
```

Запустить проект:

```
python3 homework.py
```

### Автор.
Выполнено **Зюзиным Андреем** в качестве проектного задания Яндекс.Практикум
