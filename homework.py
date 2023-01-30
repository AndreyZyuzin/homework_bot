import os
from dotenv import load_dotenv
import requests
from datetime import datetime, timedelta, timezone
import time
import telegram
from telegram.ext import CommandHandler, Updater, Filters, MessageHandler
from telegram import ReplyKeyboardMarkup

import app_logger

logger = app_logger.get_logger(__name__)
load_dotenv()


PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_PERIOD = 6
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_VERDICTS = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}

VIEWABLE_DAYS_TO_REQUEST_PROJECTS = 7 * 14

def check_tokens():
    """Проверка переменных окружения."""
    url = f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/getUpdates'
    response = requests.get(url).json()
    if not response.get('ok'):
        return False
    response = get_api_answer(int(time.time()))
    if 'homeworks' not in response:
        return False
    return True


def send_message(bot, message):
    """Отправка сообщения в Telegram-чат."""
    bot.send_message(text=message, chat_id=TELEGRAM_CHAT_ID)


def get_api_answer(timestamp):
    """Получить запрос к ендпоинту."""
    return requests.get(
        ENDPOINT,
        headers=HEADERS,
        params={'from_date': timestamp}
    ).json()


def check_response(response):
    """Проверка ответа API на соответствие документации."""
    return True


def parse_status(homework):
    """Извлечения информации о домашней работе."""
    if homework:
        return (
            f'Изменился статус проверки работы "{homework["lesson_name32"]}".'
            f'{HOMEWORK_VERDICTS[homework["status"]]}'
        )
    return (f'За последние {VIEWABLE_DAYS_TO_REQUEST_PROJECTS} дней '
            'домашнее задания не отправлялось')


def get_last_homework(homeworks):
    """Получить последнюю работу."""
    if len(homeworks) == 0:
        return {}
    # return sorted(homeworks, key=lambda hw: hw['id'], reverse=True)[0]
    return sorted(
        homeworks,
        key=lambda hw: datetime.strptime(hw['date_updated'],
                                         '%Y-%m-%dT%H:%M:%S%z'),
        reverse=True
    )[0]


def main():
    """Основная логика работы бота."""
    logger.info('Старт программы')
    check_tokens()

    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    last_updated_homework = None

    while True:
        try:
            from_date = (datetime.now(timezone.utc)
                         - timedelta(days=VIEWABLE_DAYS_TO_REQUEST_PROJECTS))
            unix_timestamp = int(from_date.timestamp())

            response = get_api_answer(unix_timestamp)

            if not check_response(response):
                pass

            homework = get_last_homework(response.get('homeworks'))
            if not last_updated_homework == homework:
                last_updated_homework = homework.copy()
                status = parse_status(homework)
                send_message(bot, status)
                logger.debug(status)
            else:
                logger.debug('Нет изменения статуса')
            time.sleep(RETRY_PERIOD)
        except Exception as error:
            error_text = f'{type(error).__name__}: {error}'
            send_message(bot, f'Сбой в работе программы: {error_text}')
            logger.exception(f'{error_text}', exc_info=True)
            raise


    logger.info('Завершение работы программы')


if __name__ == '__main__':
    main()
