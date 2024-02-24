from sqlalchemy import Column, Integer, String, Enum

from app.data.models.base import Base
from app.models.user import UserSubscription


class User(Base):
    __tablename__ = "users"

    id = Column("id", Integer, primary_key=True)
    user_id = Column("user_id", Integer, unique=True)  

    personal_email = Column("personal_email", String)
    password = Column("password", String)
    subscription = Column("subscription", Enum(UserSubscription), default=UserSubscription.NOT_SUBSCRIBED)
    email_limit = Column("email_limit", Integer, default=50)