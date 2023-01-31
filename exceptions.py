class _Exception(Exception):
    """Общий класс пользовательских исключений."""

    def __init__(self, *args):
        """Начальная установка исключения."""
        super().__init__(*args)

    def __str__(self):
        """Сообщение исключения."""
        return self.__doc__ + '\n' + super().__str__()


class TokenError(_Exception):
    """Произошла ошибка связанная с токеном."""


class PracticumTokenError(TokenError):
    """Отсутствует токен Яндекс.Практикума."""


class TelegramTokenError(TokenError):
    """Отсутствует токен Телеграмма."""


class TelegramChatIdError(TokenError):
    """Отсутствует ID чата телеграмма."""


class RequestException(_Exception):
    """Произошло неоднозначное исключение при обработке вашего запрос."""


class StatusCodeNot200RequestsError(_Exception):
    """Исключение при неудачи при связи с эндпоинтом."""


class APIResponseNotMatchError(_Exception):
    """Класс исключений API не соответствует с документации."""


class ParseStatusError(_Exception):
    """Ошибка при разборе данных."""
