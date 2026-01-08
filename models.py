# this file basically defines what columns are in your db table
# like sql format but with python classes
from sqlalchemy import Column, Integer, String
from database import Base

class NoteDB(Base):
    __tablename__ = "notes"

    #columns
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    content = Column(String, nullable=False)

class UserDB(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)

