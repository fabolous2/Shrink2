from sqlalchemy import Column, Integer, String, ForeignKey

from .base import Base


class UserEmail(Base):
    __tablename__ = "email_list"

    id = Column("id", Integer, primary_key=True)
    to = Column("email_address_to", String, unique=True)
    email_limit = Column("email_limit", Integer, default=50)
    email_subject = Column("email_subject", String)
    email_text = Column("email_text", String)
    
    user_id = Column("user_id", ForeignKey("user_info.user_id"))