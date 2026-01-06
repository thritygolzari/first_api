from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Hello from my first API"} # acts like a welcome message

@app.get("/hello") # retrieving endpoint
def hello(name: str = "world"):
    return {"greeting": f"Hello {name}"}

class Note(BaseModel): # define a note
    title:str
    content:str

@app.post("/notes") # sending data securely endpoint
def create_note(note: Note):
    return {
        "message": "Note created",
        "note": note
} # post endpoint can use JSON input as param
#JSON acts like a python object, think of the class you made