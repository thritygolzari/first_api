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