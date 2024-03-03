from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from .base import Base

class AudioFile(Base):
    __tablename__ = 'audio_files'

    audio_id = Column('audio_id', Integer, primary_key=True)
    user_id = Column('user_id', Integer, ForeignKey('users.user_id'))
    audio_name = Column('filename', String)
    audio_size = Column('size', String)
    user = relationship('User', back_populates='audio_files')
    sent_audios = relationship('SentAudio', back_populates='audio_files')