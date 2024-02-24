from sqlalchemy import Column, Integer, String, ForeignKey, Time

from .base import Base


class UserEmailSettings(Base):
    __tablename__ = "email_settings"

    id = Column("id", Integer, primary_key=True)

    quantity = Column("quantity", Integer)
    schedule_time = Column("schedule_time", Time)       
    email_text = Column("email_text", String)
    email_subject = Column("email_subject", String)
    user_id = Column("user_id", ForeignKey("users.user_id"))  

    def __str__(self) -> str:
        return self.email_text
