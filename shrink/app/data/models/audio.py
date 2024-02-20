from sqlalchemy import Column, Integer, String, ForeignKey, Boolean

from .base import Base

class UserAudio(Base):
    __tablename__ = "user_audios"

    id = Column("id", Integer, primary_key=True)
    file_id = Column("file_id", String)
    name = Column("name", String)
    size = Column("size", Integer)
    is_sent = Column("is_sent", Boolean, default=False)
    user_id = Column("user_id", ForeignKey('users.user_id'))
