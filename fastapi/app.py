from fastapi import FastAPI, Request
import os
from dotenv import load_dotenv
import uuid
import json


load_dotenv()
app = FastAPI()
sessions = {}
api_key = os.getenv("API")


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
