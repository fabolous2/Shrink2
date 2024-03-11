from sqlalchemy import Column, Integer, String
from app.data.models.base import Base

class Admin(Base):
    __tablename__ = "admins"

    admin_id = Column('admin_id', Integer, unique=True, primary_key=True)
    username = Column('username', String) 
    real_name = Column('real_name', String)
    admin_status = Column('admin_status', String)