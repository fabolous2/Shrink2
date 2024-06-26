from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from .base import Base

class AudioFile(Base):
    __tablename__ = 'audio_files'

    id = Column("id", Integer, primary_key=True)
    audio_id = Column('audio_id', String, unique=True)
    user_id = Column('user_id', Integer, ForeignKey('user.user_id'))
    audio_name = Column('filename', String)
    audio_size = Column('size', String)
    audio_index = Column('audio_index', Integer)
    is_extra = Column('is_extra', Integer, default=0)
    available_is_for_audio = Column('available_is_for_audio', Integer, default=1)
    
    user = relationship('User', back_populates='audio_files')