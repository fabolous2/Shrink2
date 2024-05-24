from sqlalchemy import Column, Integer, String, ForeignKey, Time, Boolean

from .base import Base


class UserEmailSettings(Base):
    __tablename__ = "email_settings"
 
    id = Column("id", Integer, primary_key=True)
    user_id = Column("user_id", ForeignKey("user.user_id"))  
    amount = Column('amount', Integer)
    schedule_time = Column('schedule_time', Time)
    frequency = Column('frequency', Integer, default=1)
    current_frequency = Column('current_frequency', Integer, default=1)
    email_subject = Column('subject', String)
    email_text = Column('text', String)
    is_turned_on = Column('is_turned_on', Boolean)
    email_limit_to_send = Column('email_limit_to_send', Integer, default=25)
    email_limit_to_send_for_extra = Column('email_limit_to_send_for_extra', Integer, default=50)
    advice_for_frequency = Column('advice_for_frequency', Integer, default=0)
    advice_for_quantity = Column('advice_for_quantity', Integer, default=0)

    def __str__(self) -> str:
        return self.email_text
