from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
# SQLAlchemy is a python library that talks to the DB
DATABASE_URL = "sqlite:///./notes.db" # store data here

# check_same_thread=False is needed for SQLite with FastAPI
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread":False}) # engine is core db manager, prevents threading issues 

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine) # a session is a connection to the db

Base = declarative_base() # like blueprint for db table