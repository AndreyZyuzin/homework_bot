import logging


LOG_FORMAT = '%(asctime)s, %(levelname)s, %(message)s'


def get_file_handler() -> logging.FileHandler:
    """Подключение логирование в файл."""
    file_handler = logging.FileHandler("main.log", mode='a')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter(LOG_FORMAT))
    return file_handler


def get_stream_handler() -> logging.StreamHandler:
    """Подключение логирование в консоль."""
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.DEBUG)
    stream_handler.setFormatter(logging.Formatter(LOG_FORMAT))
    return stream_handler
