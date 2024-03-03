from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from .base import Base


class ArtistEmail(Base):
    __tablename__ = 'user_emails'

    email_id = Column('email_id', Integer, primary_key=True)
    user_id = Column('user_id', Integer, ForeignKey('users.user_id'))
    email_address = Column('email_address', String)
    user = relationship('User', back_populates='user_emails')
    sent_audios = relationship('SentAudio', back_populates='user_emails')
