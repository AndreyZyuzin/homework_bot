import os
from dotenv import load_dotenv
import requests
from http import HTTPStatus
import time
import telegram
import logging
import exceptions

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s, %(levelname)s, %(message)s')
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
    # if 'PRACTICUM_TOKEN' not in globals():
    #     raise exceptions.TokenError
    # if 'TELEGRAM_TOKEN' not in globals():
    #     raise exceptions.TokenError
    # if 'TELEGRAM_CHAT_ID' not in globals():
    #     raise exceptions.TokenError
    if PRACTICUM_TOKEN is None:
        raise exceptions.TokenError
    if TELEGRAM_TOKEN is None:
        raise exceptions.TokenError
    if TELEGRAM_CHAT_ID is None:
        raise exceptions.TokenError
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
    try:
        bot.send_message(text=message, chat_id=TELEGRAM_CHAT_ID)
    except Exception as error:
        logging.error(error, exc_info=False)
        raise telegram.error.TelegramError
    logging.debug(f'Отправлено сообщение в чат телеграмма: "{message}"')


def get_api_answer(timestamp):
    """Получить запрос к ендпоинту."""
    try:
        response = requests.get(
            ENDPOINT,
            headers=HEADERS,
            params={'from_date': timestamp}
        )
    except requests.RequestException as error:
        raise Exception('adf')
    if response.status_code != HTTPStatus.OK:
        raise exceptions.StatusCodeNot200RequestsError(
            response.status_code, ENDPOINT)

    return response.json()


def check_response(response):
    """Проверка ответа API на соответствие документации."""
    if not isinstance(response, dict):
        raise TypeError
    if 'homeworks' not in response:
        raise exceptions.APIResponseNotMatchError
    homeworks = response.get('homeworks')
    if not isinstance(homeworks, list):
        raise TypeError
    homework = homeworks[0] if len(homeworks) else None
    if homework and 'homework_name' not in homework:
        raise exceptions.APIResponseNotMatchError
    # if 'status' not in homework:
    #     raise exceptions.APIResponseNotMatchError
    return True


def parse_status(homework):
    """Извлечения информации о домашней работе."""
    if not isinstance(homework, dict):
        return
    if 'homework_name' not in homework:
        raise Exception('Понятный текст')
    if 'status' not in homework:
        raise Exception('Понятный текст')
    if homework["status"] not in HOMEWORK_VERDICTS:
        raise exceptions.TokenError
    return (
        f'Изменился статус проверки работы "{homework["homework_name"]}".'
        f'{HOMEWORK_VERDICTS[homework["status"]]}'
    )


def main():
    """Основная логика работы бота."""
    logging.info('Старт программы')
    try:
        check_tokens()
    except Exception as error:
        logging.critical(error, exc_info=False)
        raise SystemExit

    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    last_status = None

    while True:
        try:
            response = get_api_answer(0)
            check_response(response)
            homework = response.get('homeworks')
            if isinstance(homework, list):
                if len(homework):
                    homework = homework[0]
            status = parse_status(homework)
            if not last_status == status:
                last_status = status
                send_message(bot, status)
                logging.debug(status)
            else:
                logging.debug('Нет изменения статуса')
            time.sleep(RETRY_PERIOD)
        except requests.RequestException as error:
            raise
        except Exception as error:
            error_text = f'{type(error).__name__}: {error}'
            send_message(bot, f'Сбой в работе программы: {error_text}')
            logging.exception(f'{error_text}', exc_info=True)
            raise


    logging.info('Завершение работы программы')


if __name__ == '__main__':
    main()
