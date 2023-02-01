class RequestException(Exception):
    """Произошло неоднозначное исключение при обработке вашего запрос."""


class StatusCodeNot200RequestsError(Exception):
    """Исключение при неудачи при связи с эндпоинтом."""


class APIResponseNotMatchError(Exception):
    """Класс исключений API не соответствует с документации."""


class ParseStatusError(Exception):
    """Ошибка при разборе данных."""

    def __init__(self, *args: object,
                 problem_key=None,
                 array=None) -> None:
        """Начальная установка исключения."""
        message = args[0] if len(args) else ''
        if problem_key:
            message += f' Несоответствие с {problem_key}.'
        if array:
            message += f' Объект: {str(array)}'
        super().__init__(message)


class EmptyHomeworkArrayException(Exception):
    """Исключение отсутствие какой-либо домашней работы в их списке."""
