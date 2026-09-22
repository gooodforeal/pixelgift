class BaseException(Exception):
    """Базовый класс для всех ошибок бизнес-логики приложения."""

    status_code: int = 400

    @property
    def message(self) -> str:
        return str(self.args[0]) if self.args else self.__class__.__name__
