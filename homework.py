import os
from dotenv import load_dotenv
import requests
from http import HTTPStatus
import time
import telegram
import logging
import exceptions

LOG_FORMAT = '%(asctime)s, %(levelname)s, %(message)s'


def get_file_handler():
    """Подключение логирование в файл."""
    file_handler = logging.FileHandler("main.log", mode='a')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter(LOG_FORMAT))
    return file_handler


def get_stream_handler():
    """Подключение логирование в консоль."""
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.DEBUG)
    stream_handler.setFormatter(logging.Formatter(LOG_FORMAT))
    return stream_handler


def get_logger(name):
    """Подключение само логирование."""
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(get_file_handler())
    logger.addHandler(get_stream_handler())
    return logger


logger = get_logger(__name__)

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


def check_tokens():
    """Проверка переменных окружения."""
    if PRACTICUM_TOKEN is None:
        raise exceptions.PracticumTokenError
    if TELEGRAM_TOKEN is None:
        raise exceptions.TelegramTokenError
    if TELEGRAM_CHAT_ID is None:
        raise exceptions.TelegramChatIdError


def send_message(bot, message):
    """Отправка сообщения в Telegram-чат."""
    try:
        bot.send_message(text=message, chat_id=TELEGRAM_CHAT_ID)
        logger.debug(f'Отправлено сообщение в чат телеграмма: "{message}"')
    except telegram.error.TelegramError as error:
        logger.error(error, exc_info=False)


def get_api_answer(timestamp):
    """Получить ответ от запроса к ендпоинту."""
    try:
        response = requests.get(
            ENDPOINT,
            headers=HEADERS,
            params={'from_date': timestamp}
        )
    except requests.RequestException:
        raise exceptions.RequestException
    if response.status_code != HTTPStatus.OK:
        raise exceptions.StatusCodeNot200RequestsError(
            response.status_code, ENDPOINT)
    return response.json()


def check_response(response):
    """Проверка ответа API на соответствие документации."""
    if not isinstance(response, dict):
        raise TypeError('response: ', type(response))
    if 'homeworks' not in response:
        raise exceptions.APIResponseNotMatchError(
            "'homeworks' не входит в response")
    homeworks = response.get('homeworks')
    if not isinstance(homeworks, list):
        raise TypeError('homeworks: ', type(homeworks))


def parse_status(homework):
    """Извлечения информации о домашней работе."""
    if not isinstance(homework, dict):
        return
    if 'homework_name' not in homework:
        raise exceptions.ParseStatusError(
            "'homework_name' не входит в homework, а должен быть")
    if 'status' not in homework:
        raise exceptions.ParseStatusError(
            "'status' не входит в homework, а должен быть")
    if homework['status'] not in HOMEWORK_VERDICTS:
        raise exceptions.ParseStatusError("Не известный вердикт")
    return (
        f'Изменился статус проверки работы "{homework["homework_name"]}".'
        f'{HOMEWORK_VERDICTS[homework["status"]]}'
    )


def main():
    """Основная логика работы бота."""
    logger.info('Старт программы')
    try:
        check_tokens()
    except exceptions.TokenError as error:
        logger.critical(error, exc_info=False)
        raise SystemExit

    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    last_status = None

    while True:
        try:
            response = get_api_answer(0)
            check_response(response)
            homework = response.get('homeworks')
            if isinstance(homework, list) and len(homework):
                homework = homework[0]
            status = parse_status(homework)
            if not last_status == status:
                last_status = status
                send_message(bot, status)
            else:
                logger.debug('Нет изменения статуса')
            time.sleep(RETRY_PERIOD)
        except (exceptions.RequestException,
                exceptions.StatusCodeNot200RequestsError,
                exceptions.APIResponseNotMatchError,
                exceptions.ParseStatusError) as error:
            error_text = f'{type(error).__name__}: {error}'
            send_message(bot, f'Сбой в работе программы: {error_text}')
            logger.exception(f'{error_text}', exc_info=False)
            raise


if __name__ == '__main__':
    main()
