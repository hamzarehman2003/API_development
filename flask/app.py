from flask import Flask
from flask import request
from flask import jsonify
import os
from dotenv import load_dotenv
import json
import uuid
from flask_cors import CORS
from config import create_app, db
from models import Student, Subject


load_dotenv()


app = create_app()
CORS(app)


with app.app_context():
    db.create_all()


@app.route('/Home_Route', methods=['GET'])
def hello():
    return "Hello, World!"


@app.route('/user_info')
def user_info():
    content = open("users.json").read()
    return content


@app.route('/add_session', methods=['POST'])
def add_session():
    try:
        api_key = os.getenv('API')

        received_api_key = request.headers.get('x-api-key')

        if not received_api_key:
            return "need api key", 401
        if received_api_key != api_key:
            return "Unauthorized access", 403

        data = request.get_json()
        name = data.get("name")
        age = data.get("age")
        gender = data.get("gender")

        if not all([name, age, gender]):
            return "Missing user fields", 400

        session_id = uuid.uuid4().hex

        session_file_path = 'db/sessions/session.json'
        if os.path.exists(session_file_path):
            with open(session_file_path, 'r') as file:
                sessions = json.load(file)
        else:
            sessions = {}

        sessions[session_id] = {
            "name": name,
            "age": age,
            "gender": gender
        }

        with open(session_file_path, 'w') as file:
            json.dump(sessions, file, indent=4)

        return jsonify({"session_id": session_id}), 200

    except Exception as e:
        return jsonify({"error": "Error occurred", "details": str(e)}), 500


@app.route('/get_session_user', methods=['POST'])
def get_session_user():
    try:
        expected_api_key = os.getenv('API')

        received_api_key = request.headers.get('x-api-key')

        if not received_api_key:
            return jsonify({"error": "API key needed"}), 401
        if received_api_key != expected_api_key:
            return jsonify({"error": "Unauthorized access"}), 403

        data = request.get_json()
        session_id = data.get("session_id")

        if not session_id:
            return jsonify({"error": "Session ID is required"}), 400

        session_file_path = 'db/sessions/session.json'
        if os.path.exists(session_file_path):
            with open(session_file_path, 'r') as file:
                sessions = json.load(file)
        else:
            sessions = {}

        if session_id not in sessions:
            return jsonify({"error": "Session ID not found"}), 404

        user_info = sessions[session_id]
        return jsonify(user_info), 200

    except Exception as e:
        return jsonify({"error": "Error occurred", "details": str(e)}), 500


@app.route("/add_subject", methods=['POST'])
def add_subject():
    try:
        data = request.get_json()
        name = data.get('name')
        if not name:
            return jsonify({"error": "subject name not found"}), 400    
        subject = Subject(name=name)
        db.session.add(subject)
        db.session.commit()
        return jsonify({"message": "subject added", "subject_id": subject.id}), 201
    except Exception as e:
        return jsonify({"error": "error occured", "details": str(e)}), 500


@app.route("/add_student", methods=['POST'])
def add_student():
    try:
        data = request.get_json()
        name = data.get("name")
        age = data.get("age")
        gender = data.get("gender")
        subject_id = data.get("subject_id")
        if not all([name, age, gender, subject_id]):
            return jsonify({"error": "All fields (name, age, gender, subject_id) are required"}), 400

        student = Student(
            encrypted_name=name,
            age=age,
            gender=gender,
            subject_id=subject_id
        )
        student.set_name(name)

        db.session.add(student)
        db.session.commit()
        return jsonify({"message": "Student added", "student_id": student.id}), 201
    except Exception as e:
        return jsonify({"error": "Something went wrong", "details": str(e)}), 500


@app.route("/get_all_students", methods=['POST'])
def get_all_students():
    try:    
        data = request.get_json()
        subject_id = data.get("subject_id")

        if not subject_id:
            return jsonify({"error": "subject_id is required"}), 400

        students = Student.query.filter_by(subject_id=subject_id).all()

        students_list = []
        for student in students:
            students_list.append({
                "name": student.get_name(),
                "age": student.age,
                "gender": student.gender
            })

        return jsonify({"students": students_list}), 200

    except Exception as e:
        # print("DEBUG str:", str)
        return jsonify({"error": "Something went wrong", "details": str(e)}), 500


@app.route("/update_student", methods=['POST'])
def update_student():
    try:
        data = request.get_json()
        student_id = data.get('student_id')

        if not student_id:
            return jsonify({"error": "student_id is required"}), 400

        student = Student.query.get(student_id)

        if not student:
            return jsonify({"error": "Student not found"}), 404

        if 'name' in data:
            student.set_name(data['name'])
        if 'age' in data:
            student.age = data['age']
        if 'gender' in data:
            student.gender = data['gender']
        if 'subject_id' in data:
            student.subject_id = data['subject_id']

        db.session.commit()

        return jsonify({"message": "Student updated successfully"}), 200

    except Exception as e:
        return jsonify({"error": "Something went wrong", "details": str(e)}), 500


@app.route("/get_student", methods=['POST'])
def get_student():
    try:
        data = request.get_json()
        id = data.get("student_id")

        students = Student.query.filter_by(id=id).all()

        student_list = []
        for student in students:
            student_list.append({
                "name":student.get_name(),
                "age" :student.age,
                "gender" :student.gender
            })
        return jsonify({"students": student_list}), 200

    except Exception as e:
        return jsonify({"error": "Something went wrong", "details": str(e)}), 500
if __name__ == '__main__':
    app.run(debug=True)
