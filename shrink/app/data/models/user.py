from .base import Base

from sqlalchemy import Column, Integer, String, Boolean, Time

# унаследовали базовую модель конкретной моделью

class User(Base):
    __tablename__ = "user_info" # указываешь имя таблицы в самой базе данных

    """
    на первое место указываешь имя поля в бд
    на второе тип, так как я id - первичный ключ, то так
    и пишем, primary_key=True
    """
    id = Column("id", Integer, primary_key=True)
    user_id = Column("user_id", Integer, unique=True)  
    personal_email = Column("personal_email", String)
    password = Column("password", String)
    premium = Column("premium", Boolean, default=False)
    schedule_time = Column("schedule_time", Time)
    quentity = Column("quantity", Integer)