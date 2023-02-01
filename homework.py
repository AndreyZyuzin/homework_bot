import logging
import os
import time
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

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(logger_config.get_file_handler())
logger.addHandler(logger_config.get_stream_handler())


def check_tokens(*args: object) -> None:
    """Проверка переменных окружения."""
    no_valid = [v for v in args if globals().get(v) is None]
    if no_valid:
        raise NameError(f'Отсутствуют {", ".join(no_valid)}')


def send_message(bot: telegram.Bot, message: str) -> None:
    """Отправка сообщения в Telegram-чат."""
    try:
        bot.send_message(text=message, chat_id=TELEGRAM_CHAT_ID)
        logger.debug(f'Отправлено сообщение в чат телеграмма: "{message}"')
    except telegram.error.TelegramError as error:
        logger.error(error)


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


def check_response(response: dict) -> dict:
    """Проверка ответа API на соответствие документации."""
    if not isinstance(response, dict):
        raise TypeError(f'Ответ запроса - {type(response)}, а ожидается dict')
    homeworks = response.get('homeworks')
    if not isinstance(homeworks, list):
        raise TypeError(f'"homeworks" в запроса - {type(response)}, '
                        'а ожидается list')
    if len(homeworks) == 0:
        raise exceptions.EmptyHomeworkArrayException(
            'Пустой список домашних работ.')
    return homeworks[0]


def parse_status(homework: dict) -> str:
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


def parse_status_experimental(homework: dict) -> str:
    """Извлечения информации о домашней работе."""
    if not isinstance(homework, dict):
        raise TypeError(f'Тип homework - {type(homework)}, а ожидается dict')
    for key in ('homework_name', 'status'):
        if key not in homework:
            raise KeyError(f'{key} должен входит в homework')
    if homework['status'] not in HOMEWORK_VERDICTS:
        raise exceptions.ParseStatusError('Не известный вердикт')
    return (
        f'Изменился статус проверки работы "{homework["homework_name"]}".'
        f'{HOMEWORK_VERDICTS[homework["status"]]}'
    )


def main() -> None:
    """Основная логика работы бота."""
    logger.info('Старт программы')
    try:
        check_tokens('PRACTICUM_TOKEN', 'TELEGRAM_TOKEN', 'TELEGRAM_CHAT_ID')
    except NameError as error:
        logger.critical(f'{type(error).__name__}: {error}')
        raise SystemExit

    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    last_status = None

    while True:
        try:
            response = get_api_answer(0)
            homework = check_response(response)
            status = parse_status(homework)
            if not last_status == status:
                last_status = status
                send_message(bot, status)
            else:
                logger.debug('Нет изменения статуса')
        except (exceptions.RequestException,
                exceptions.StatusCodeNot200RequestsError,
                exceptions.APIResponseNotMatchError,
                exceptions.ParseStatusError,
                exceptions.EmptyHomeworkArrayException,
                TypeError,
                KeyError,) as error:
            error_text = f'{type(error).__name__}: {error}'
            send_message(bot, f'Сбой в работе программы: {error_text}')
            logger.error(f'{error_text}')
        time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    main()
