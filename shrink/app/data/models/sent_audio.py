from sqlalchemy import Column, Integer, ForeignKey, Date
from sqlalchemy.orm import relationship

from .base import Base


class SentAudio(Base):
    __tablename__ = 'sent_audios'

    sent_audio_id = Column('sent_audio_id', Integer, primary_key=True)
    user_id = Column('user_id', Integer, ForeignKey('user.user_id'))
    email_id = Column('email_id', Integer, ForeignKey('user_emails.email_id'))
    audio_id = Column('audio_id', Integer, ForeignKey('audio_files.audio_id'))
    send_date = Column('send_date', Date)

    user = relationship('User', back_populates='sent_audios')
    user_emails = relationship('ArtistEmail', back_populates='sent_audios')
    audio_files = relationship('AudioFile', back_populates='sent_audios')