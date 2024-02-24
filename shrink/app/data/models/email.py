from sqlalchemy import Column, Integer, String, ForeignKey

from .base import Base


class UserEmail(Base):
    __tablename__ = "user_emails"

    id = Column("id", Integer, primary_key=True)
    to = Column("email_address_to", String, unique=True)
    user_id = Column("user_id", ForeignKey("users.user_id"))
