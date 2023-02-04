import logging
import os
import time
from datetime import datetime, timedelta, timezone
from http import HTTPStatus

import requests
import telegram
from dotenv import load_dotenv

import exceptions
import logger_config

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

VIEWABLE_DAYS_TO_REQUEST_PROJECTS = 7 * 2

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(logger_config.get_file_handler())
logger.addHandler(logger_config.get_stream_handler())


def check_tokens() -> None:
    """Проверка переменных окружения."""
    variables = {
        'PRACTICUM_TOKEN': PRACTICUM_TOKEN,
        'TELEGRAM_TOKEN': TELEGRAM_TOKEN,
        'TELEGRAM_CHAT_ID': TELEGRAM_CHAT_ID,
    }
    if not all(variables.values()):
        no_valid = [key for key, value in variables.items() if value is None]
        raise TypeError('Отсутствие необходимых переменных окружения: '
                        f'{", ".join(no_valid)}')


def send_message(bot: telegram.Bot, message: str) -> None:
    """Отправка сообщения в Telegram-чат."""
    try:
        bot.send_message(text=message, chat_id=TELEGRAM_CHAT_ID)
        logger.debug(f'Отправлено сообщение в чат телеграмма: "{message}"')
    except telegram.error.TelegramError as error:
        logger.error(error)
        raise telegram.error.TelegramError('Ошибка в работе телеграма')


def get_api_answer(timestamp: int) -> dict:
    """Получить ответ от запроса к ендпоинту."""
    try:
        response = requests.get(
            ENDPOINT,
            headers=HEADERS,
            params={'from_date': timestamp}
        )
    except requests.RequestException as error:
        raise exceptions.RequestException(
            'Некоторое неоднозначное исключение: ', error)
    if response.status_code != HTTPStatus.OK:
        raise exceptions.StatusCodeNot200RequestsError(
            response.status_code, ENDPOINT)
    return response.json()


def check_response(response: dict) -> None:
    """Проверка ответа API на соответствие документации."""
    if not isinstance(response, dict):
        raise TypeError(f'Ответ запроса - {type(response)}, а ожидается dict')
    homeworks = response.get('homeworks')
    if not isinstance(homeworks, list):
        raise TypeError(f'"homeworks" в запроса - {type(response)}, '
                        'а ожидается list')


def parse_status_experimental(homework: dict) -> str:
    """Извлечения информации о домашней работе."""
    try:
        return (
            f'Изменился статус проверки работы "{homework["homework_name"]}".'
            f'{HOMEWORK_VERDICTS[homework["status"]]}'
        )
    except KeyError as error:
        raise exceptions.ParseStatusError('Ошибка при извлечения homework.',
                                          problem_key=error, array=homework)
    except TypeError:
        raise TypeError(f'Тип homework - {type(homework).__name__},'
                        'а ожидается dict')


def parse_status(homework: dict) -> str:
    """Извлечения информации о домашней работе."""
    if not isinstance(homework, dict):
        raise TypeError(f'Тип homework - {type(homework)}, а ожидается dict')

    if not {'homework_name', 'status'}.issubset(homework):
        raise KeyError('В homework должны быть "homework_name", "status"')

    status = homework['status']
    if status not in HOMEWORK_VERDICTS:
        raise exceptions.ParseStatusError('Не известный вердикт')

    return (
        f'Изменился статус проверки работы "{homework["homework_name"]}".'
        f'{HOMEWORK_VERDICTS[status]}'
    )


def main() -> None:
    """Основная логика работы бота."""
    logger.info('Старт программы')
    try:
        check_tokens()
    except TypeError as error:
        logger.critical(f'{type(error).__name__}: {error}')
        raise SystemExit

    bot: telegram.Bot = telegram.Bot(token=TELEGRAM_TOKEN)
    last_status = ''

    while True:
        try:
            from_date = (
                datetime.now(timezone.utc)
                - timedelta(days=VIEWABLE_DAYS_TO_REQUEST_PROJECTS))
            unix_timestamp = int(from_date.timestamp())
            response: dict = get_api_answer(unix_timestamp)
            check_response(response)
            homeworks: list = response.get('homeworks')
            if not len(homeworks):
                status = 'Пустой список домашних работ.'
            else:
                homework: dict = homeworks[0]
                status: str = parse_status(homework)
            if not last_status == status:
                last_status = status
                send_message(bot, status)
            else:
                logger.debug('Нет изменения статуса')
        except (exceptions.RequestException,
                exceptions.StatusCodeNot200RequestsError,
                exceptions.APIResponseNotMatchError,
                exceptions.ParseStatusError,
                TypeError,
                KeyError,) as error:
            error_text = f'{type(error).__name__}: {error}'
            send_message(bot, f'Сбой в работе программы: {error_text}')
            logger.error(f'{error_text}')
        time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    main()
