from flask import Flask
from flask import request
from flask import jsonify
import os
from dotenv import load_dotenv
import json
import uuid
from flask_cors import CORS


load_dotenv()


app = Flask(__name__)
CORS(app)


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
        # 1. Get the expected API key from environment
        api_key = os.getenv('API')

        # 2. Get the provided API key from the request headers
        received_api_key = request.headers.get('x-api-key')

        # 3. Check for missing or invalid API key
        if not received_api_key:
            return "need api key", 401
        if received_api_key != api_key:
            return "Unauthorized access", 403

        # 4. Parse user data from request body
        data = request.get_json()
        name = data.get("name")
        age = data.get("age")
        gender = data.get("gender")

        if not all([name, age, gender]):
            return "Missing user fields", 400

        # 5. Generate session ID
        session_id = uuid.uuid4().hex

        # 6. Load existing sessions from file
        session_file_path = 'db/sessions/session.json'
        if os.path.exists(session_file_path):
            with open(session_file_path, 'r') as file:
                sessions = json.load(file)
        else:
            sessions = {}

        # 7. Store the new user data with session ID
        sessions[session_id] = {
            "name": name,
            "age": age,
            "gender": gender
        }

        # 8. Save updated session data back to file
        with open(session_file_path, 'w') as file:
            json.dump(sessions, file, indent=4)

        # 9. Return the session ID
        return jsonify({"session_id": session_id}), 200

    except Exception as e:
        return jsonify({"error": "Error occurred", "details": str(e)}), 500


@app.route('/get_session_user', methods=['POST'])
def get_session_user():
    try:
        # 1. Get the expected API key from environment
        expected_api_key = os.getenv('API')

        # 2. Get the provided API key from request headers
        received_api_key = request.headers.get('x-api-key')

        # 3. Check if the API key is missing or invalid
        if not received_api_key:
            return jsonify({"error": "API key needed"}), 401
        if received_api_key != expected_api_key:
            return jsonify({"error": "Unauthorized access"}), 403

        # 4. Get session ID from the request body
        data = request.get_json()
        session_id = data.get("session_id")

        # 5. Check if the session ID is provided
        if not session_id:
            return jsonify({"error": "Session ID is required"}), 400

        # 6. Load the sessions from session.json file
        session_file_path = 'db/sessions/session.json'
        if os.path.exists(session_file_path):
            with open(session_file_path, 'r') as file:
                sessions = json.load(file)
        else:
            sessions = {}

        # 7. Check if session ID exists in the session data
        if session_id not in sessions:
            return jsonify({"error": "Session ID not found"}), 404

        # 8. Return the user info associated with the session ID
        user_info = sessions[session_id]
        return jsonify(user_info), 200

    except Exception as e:
        return jsonify({"error": "Error occurred", "details": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
