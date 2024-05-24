from sqlalchemy import Column, Integer, String, Enum
from sqlalchemy.orm import relationship

from app.data.models.base import Base
from app.models.user import UserSubscription

class User(Base):
    __tablename__ = "user"

    user_id = Column("user_id", Integer, unique=True, primary_key=True)  
    personal_email = Column('personal_email', String)
    password = Column("password", String)
    email_limit = Column("email_limit", Integer, default=200)
    audio_limit = Column('audio_limit', Integer, default=20)
    subscription = Column("subscription", Enum(UserSubscription), default=UserSubscription.NOT_SUBSCRIBED)
    sub_duration = Column('sub_duration', Integer)
 
    user_emails = relationship('ArtistEmail', back_populates='user')
    audio_files = relationship('AudioFile', back_populates='user')