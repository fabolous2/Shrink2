from sqlalchemy.orm import DeclarativeBase

# DeclarativeBase - класс который надо унаследовать нашей базовой моделью

class Base(DeclarativeBase):
    pass

# все, этого достаточно

# теперь создаем модель пользователя