from sqlalchemy import Column, Integer, String, ForeignKey, Time

from .base import Base


class UserEmailSettings(Base):
    __tablename__ = "email_settings"

    id = Column("id", Integer, primary_key=True)
    user_id = Column("user_id", ForeignKey("users.user_id"))  
    amount = Column('amount', Integer)
    schedule_time = Column('schedule_time', Time)
    email_subject = Column('subject', String)
    email_text = Column('text', String)

    def __str__(self) -> str:
        return self.email_text
