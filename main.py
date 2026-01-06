from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import SessionLocal, engine
from models import NoteDB
from database import Base

app = FastAPI()

# Create tables on startup
Base.metadata.create_all(bind=engine)

# Pydantic schemas (what the API receives/returns)
class NoteCreate(BaseModel):
    title: str
    content: str

class NoteOut(BaseModel): # for returning a note
    id: int
    title: str
    content: str

    class Config:
        from_attributes = True # for SQLAlchemy instance -> pydantic conversion

# Dependency: get a DB session per request
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# basic endpoints
@app.get("/")
def root():
    return {"message": "Hello from my first API"} # acts like a welcome message

@app.get("/hello") # retrieving endpoint
def hello(name: str = "world"):
    return {"greeting": f"Hello {name}"}

# Notes endpoints
@app.post("/notes", response_model=NoteOut) # creates a note, format using NoteOut
def create_note(note: NoteCreate, db: Session = Depends(get_db)): # fastapi gives a db session for request
    new_note = NoteDB(title=note.title, content=note.content) # create SQLAlchemy object
    db.add(new_note)
    db.commit()
    db.refresh(new_note)
    return new_note # return SQLAlchemy object, FastAPI + Pydantic convert it to JSON with NoteOut

@app.get("/notes", response_model=list[NoteOut])
def list_notes(db: Session = Depends(get_db)):
    return db.query(NoteDB).all() # returns all notes from db

# find specific note
@app.get("/notes/{note_id}", response_model=NoteOut) 
def get_note(note_id: int, db: Session = Depends(get_db)):
    note = db.query(NoteDB).filter(NoteDB.id == note_id).first()
    if note is None: # error handling
        raise HTTPException(status_code=404, detail="Note not found")
    return note