class TokenError(Exception):
    """Класс исключений из-за неверного токена."""

    def __init__(self):
        """Начальная установка исключения."""
        super().__init__('Error token')

    def __str__(self):
        """Сообщение исключения."""
        return ('Не подходит токен')


class StatusCodeNot200RequestsError(Exception):
    """Исключение при неудачи при связи с эндпоинтом."""

    def __init__(self, status_code=None, endpoint=None):
        """Инициализация исключение."""
        message = f'{type(self).__name__}: '
        if endpoint:
            message += f'Endpoint - "{endpoint}".'
        if status_code:
            message = f' status_code - {status_code}.'
        super().__init__(message)
        self.status_code = status_code
        self.endpoint = endpoint

    def __str__(self):
        """Сообщение исключения."""
        message = ''
        if self.endpoint:
            message += f'При соединении с {self.endpoint} '
        message = 'произошла ошибка.'
        if self.status_code:
            message += f' status_code - {self.status_code}.'
        return (message)


class APIResponseNotMatchError(Exception):
    """Класс исключений API не соответствует с документации."""

    def __init__(self):
        """Начальная установка исключения."""
        super().__init__('Strange API response')

    def __str__(self):
        """Сообщение исключения."""
        return ('Ответ API не соответствует с документации')
