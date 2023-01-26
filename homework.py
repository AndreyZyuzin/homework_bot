import logging
import sys
import os
from dotenv import load_dotenv
import requests
import time
from telegram.ext import CommandHandler, Updater, Filters, MessageHandler
from telegram import ReplyKeyboardMarkup


load_dotenv()


PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_PERIOD = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_VERDICTS = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}

LOG_FORMAT = '%(asctime)s, %(levelname)s, %(message)s'


def check_tokens():
    """Проверка переменных окружения."""


def send_message(bot, message):
    """Отправка сообщения в Telegram-чат."""


def get_api_answer(timestamp):
    """Получить запрос к ендпоинту."""
    homework_statuses = requests.get(
        ENDPOINT,
        headers=HEADERS,
        params={'from_date': timestamp}
    )


def check_response(response):
    """Проверка ответа API на соответствие."""


def parse_status(homework):
    """Извлечения информации о домашней работе."""
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def main():
    """Основная логика работы бота."""
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    handler_1 = logging.FileHandler(filename='log/main.log', mode='a')
    handler_1.setFormatter(logging.Formatter(LOG_FORMAT))
    handler_1.setLevel(logging.INFO)

    handler_2 = logging.StreamHandler(sys.stdout)
    handler_2.setFormatter(logging.Formatter(LOG_FORMAT))
    handler_2.setLevel(logging.DEBUG)

    logger.addHandler(handler_1)
    logger.addHandler(handler_2)

#    bot = telegram.Bot(token=TELEGRAM_TOKEN)
#    timestamp = int(time.time())

#    ...
#
#    while True:
#        try:
#
#            ...
#
#        except Exception as error:
#            message = f'Сбой в работе программы: {error}'
#            ...
#        ...
#

if __name__ == '__main__':
    main()
