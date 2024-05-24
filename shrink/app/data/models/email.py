from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from .base import Base


class ArtistEmail(Base):
    __tablename__ = 'user_emails'

    id = Column("id", Integer, primary_key=True)
    email_id = Column('email_id', Integer, default=0)
    user_id = Column('user_id', Integer, ForeignKey('user.user_id'))
    email_address = Column('email_address', String)
    last_sent_index = Column('last_sent_index', Integer, default=0)
    available_is = Column('available_is', Integer, default=1)
    
    user = relationship('User', back_populates='user_emails')
