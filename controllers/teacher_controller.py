from flask import request, jsonify
from models.models import Quiz, TabSwitchEvent
from utils.decode import decode_token
from datetime import datetime,timezone
def get_quizzes_by_teacher():
    try:
        # Extract the teacher_id from the token
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({"error": "No token provided"}), 401
        
        teacher_data = decode_token(token)
        if not teacher_data or 'id' not in teacher_data:
            return jsonify({"error": "Invalid or expired token"}), 401
        
        teacher_id = teacher_data['id']
        
        # Fetch quizzes created by this teacher
        quizzes = Quiz.get_by_teacher(teacher_id)
        if not quizzes:
            return jsonify({"message": "No quizzes found"}), 200
        
        # Serialize quizzes to JSON
        
        
        return jsonify({"quizzes": quizzes}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
def add_tab_switch_event():
    try:
        # Get the student token from the Authorization header
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({"error": "No token provided"}), 401
        
        # Parse the token
        student_data = decode_token(token)
        if not student_data or 'id' not in student_data:
            return jsonify({"error": "Invalid or expired student token"}), 401
        
        student_id = student_data['id']
        student_name = student_data['name']
        # Parse the request body to get the quiz_id
        data = request.get_json()
        if not data or 'quiz_id' not in data:
            return jsonify({"error": "Missing quiz_id in the request body"}), 400

        quiz_id = data['quiz_id']

        # Ensure the quiz exists
        
        # Get the current timestamp for the tab switch event
        timestamp = datetime.now(timezone.utc)   # Current timestamp
        
        # Create a new tab switch event
        event = TabSwitchEvent(quiz_id=quiz_id, student_id=student_id,student_name=student_name, timestamp=timestamp)
        event.save()  # Save the event in the database
        
        return jsonify({"message": "Tab switch event added successfully"}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500

def get_tab_switch_events_by_quiz_id(quiz_id):
    try:
        # Parse the request to get quiz_id

        if not quiz_id:
            return jsonify({"error": "Missing quiz_id in the request"}), 400

        # Fetch the tab switch events for the given quiz_id
        events = TabSwitchEvent.get_by_quiz_id(quiz_id)
        if not events:
            return jsonify({"tab_switch_events": []}), 200

        # Return the list of events as JSON
        return jsonify({"tab_switch_events": [event.__dict__ for event in events]}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500