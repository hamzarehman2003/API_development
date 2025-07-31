from fastapi import FastAPI, Request, Depends, HTTPException
import os
from dotenv import load_dotenv
import uuid
import json
from database import SessionLocal, engine
from models import Base, Subject, Student
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List
from fastapi import Path


load_dotenv()
app = FastAPI()
sessions = {}
api_key = os.getenv("API")


Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class SubjectCreate(BaseModel):
    name: str


class StudentCreate(BaseModel):
    name: str
    age: int
    gender: str
    subject_id: int


class student_by_subject(BaseModel):
    subject_id: int


class updateStudent(BaseModel):
    name: str | None = None
    age: int | None = None
    gender: str | None = None
    subject_id: int | None = None
    student_id: int


class get_student(BaseModel):
    id: int


@app.get("/")
async def root():
    return "Home Route"


@app.get("/user_info")
async def user_info():
    content = open("user.json").read()
    return content


@app.post("/add_session")
async def add_session(request: Request):
    try:
        received_key = request.headers.get("API-Key")
        if not api_key:
            return "api key needed"
        if api_key != received_key:
            return "Invalid api key"
        # if api_key == received_key:
        #     return "siuuu"

        data = await request.json()
        name = data.get("name")
        age = data.get("age")
        gender = data.get("gender")
        if not name or not age or not gender:
            return "missing fields"    
        session_id = str(uuid.uuid4())

        session_file_path = 'db/sessions.json'
        if os.path.exists(session_file_path):
            with open(session_file_path, 'r') as file:
                sessions = json.load(file)
        else:
            sessions = {}

        sessions[session_id] = {
            "name": name,
            "gender": gender,
            "age": age
        }
        with open(session_file_path, 'w') as file:
            json.dump(sessions, file, indent=4)

        return session_id

    except Exception as e:
        return str(e)


@app.post("/get_user")
async def get_user(request: Request):
    try:
        recieved_key = request.headers.get("API-Key")
        if api_key != recieved_key:
            return "invalid api key"
        data = await request.json()
        session_id = data.get("session_id")
        if not session_id:
            return "session id not found"

        session_file_path = 'db/sessions.json'
        if os.path.exists(session_file_path):
            with open(session_file_path, 'r') as file:
                sessions = json.load(file)
        else:
            sessions = {}
        user_info = sessions[session_id]
        return {"user_info": user_info}
    except Exception as e:
        return e


@app.post("/add_subject")
def add_subject(subject: SubjectCreate, db: Session = Depends(get_db)):
    try:  
        new_subject = Subject(name=subject.name)
        db.add(new_subject)
        db.commit()
        db.refresh(new_subject)
        return {"message": "Subject added successfully", "subject_id": new_subject.id}
    except Exception as e:
        return {"error": str(e)}


@app.post("/add_student")
def add_student(student: StudentCreate, db: Session = Depends(get_db)):
    try:
        new_student = Student(
            age=student.age,
            gender=student.gender,
            subject_id=student.subject_id
        )
        new_student.set_name(student.name)
        db.add(new_student)
        db.commit()
        db.refresh(new_student)

        return {"message": "Student added", "student_id": new_student.id}
    except Exception as e:
        return {"error": str(e)}


@app.post("/students_by_subject")
def students_by_subject(by_subject: student_by_subject, db: Session = Depends(get_db)):
    try:
        students = db.query(Student).filter_by(subject_id=by_subject.subject_id).all()
        result = []
        for student in students:
            result.append({
                "name": student.get_name(),
                "age": student.age,
                "gender": student.gender
            })

        return result
    except Exception as e:
        return {"error": str(e)}


@app.post("/update_student")
def update_student(new_student: updateStudent, db: Session = Depends(get_db)):
    try:
        student_id = new_student.student_id
        student = db.query(Student).get(student_id)
        if not student:
            return {"error": "student not found"}

        if new_student.name:
            student.set_name(new_student.name)
        if new_student.age:
            student.age = new_student.age
        if new_student.gender:
            student.age = new_student.gender
        if new_student.subject_id:
            student.subject_id = new_student.subject_id
        
        db.commit()
        db.refresh(student)

        return {"message": "Student updated", "student_id": student.id}

    except Exception as e:
        return {"error": str(e)}


@app.post("/get_student")
def get_student(get_student: get_student, db: Session = Depends(get_db)):
    id = get_student.id
    student = db.query(Student).get(id)
    result = []
    result.append({
        "name": student.get_name(),
        "age": student.age,
        "gender": student.gender,
        "subject_id": student.subject_id 
    })
    return result