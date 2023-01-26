class TokenError(Exception):
    """Класс исключений из-за неверного токена."""

    def __init__(self, training_type: str) -> None:
        """Начальная установка исключения."""
        super().__init__(f'{type(self).__name__}: '
                         f'Unknown type - "{training_type}"')
        self.training_type = training_type

    def __str__(self):
        """Сообщение исключения."""
        return (f'"{self.training_type}" - '
                'не определён тип тренировки.')
