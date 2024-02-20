from sqlalchemy import Column, Integer, String, Boolean, Time, Enum

from app.data.models.base import Base
from app.models.user import UserSubscription


class User(Base):
    __tablename__ = "users"

    id = Column("id", Integer, primary_key=True)
    user_id = Column("user_id", Integer, unique=True)  

    password = Column("password", String)
    quantity = Column("quantity", Integer)
    schedule_time = Column("schedule_time", Time)
    personal_email = Column("personal_email", String)
    subscription = Column("subscription", Enum(UserSubscription), default=UserSubscription.NOT_SUBSCRIBED)
