from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
# SQLAlchemy is a python library that talks ot the DB
DATABASE_URL = "sqlite:///./notes.db"

# check_same_thread=False is needed for SQLite with FastAPI
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread":False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()