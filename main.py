from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session


from database import SessionLocal, engine
from models import NoteDB
from database import Base

from auth import hash_password, verify_password, create_access_token, get_current_user_id
from models import UserDB

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

# schemas for auth
class RegisterIn(BaseModel):
    email: str
    password: str

class LoginIn(BaseModel):
    email: str
    password: str

class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"

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
def create_note(note: NoteCreate, db: Session = Depends(get_db),
               user_id: int = Depends(get_current_user_id),): # fastapi gives a db session for request
    new_note = NoteDB(title=note.title, content=note.content) # create SQLAlchemy object
    db.add(new_note)
    db.commit()
    db.refresh(new_note)
    return new_note # return SQLAlchemy object, FastAPI + Pydantic convert it to JSON with NoteOut

@app.get("/notes", response_model=list[NoteOut])
def list_notes(db: Session = Depends(get_db),
               user_id: int = Depends(get_current_user_id),):
    return db.query(NoteDB).all() # returns all notes from db

# find specific note
@app.get("/notes/{note_id}", response_model=NoteOut) 
def get_note(note_id: int, db: Session = Depends(get_db),
               user_id: int = Depends(get_current_user_id),):
    note = db.query(NoteDB).filter(NoteDB.id == note_id).first()
    if note is None: # error handling
        raise HTTPException(status_code=404, detail="Note not found")
    return note

# update note title and/or content by id
@app.put("/notes/{note_id}", response_model=NoteOut)
def update_note(note_id: int, note: NoteCreate, db: Session = Depends(get_db),
               user_id: int = Depends(get_current_user_id),):
    db_note = db.query(NoteDB).filter(NoteDB.id == note_id).first()
    if db_note is None:
        raise HTTPException(status_code=404, detail="Note not found")
    
    db_note.title = note.title
    db_note.content = note.content
    db.commit()
    db.refresh(db_note)
    return db_note

# delete a note by id
@app.delete("/notes/{note_id}")
def delete_note(note_id: int, db: Session = Depends(get_db),
               user_id: int = Depends(get_current_user_id),):
    db_note = db.query(NoteDB).filter(NoteDB.id == note_id).first()
    if db_note is None:
        raise HTTPException(status_code=404, detail="Note not found")
    
    db.delete(db_note)
    db.commit()
    return {"deleted": True, "id": note_id}

# auth endpoints

# registration endpoint
@app.post("/auth/register")
def register(data: RegisterIn, db: Session = Depends(get_db)):
    existing = db.query(UserDB).filter(UserDB.email == data.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    user = UserDB(email=data.email, password_hash=hash_password(data.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    
    print("PW:", repr(data.password))
    print("PW bytes:", len(data.password.encode("utf-8")))

    return {"id": user.id, "email": user.email}

# user login endpoint
@app.post("/auth/login")
def login(data: LoginIn, db: Session = Depends(get_db)):
    user = db.query(UserDB).filter(UserDB.email == data.email).first()
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    # if account exists, create token
    token = create_access_token(user.id)
    return {"access_token": token, "token_type": "bearer"}