from flask import request, jsonify
from models.models import Quiz, TabSwitchEvent, UnreleasedQuiz
from utils.decode import decode_token
from datetime import datetime, timezone
import json

def get_quizzes_by_teacher():
    try:
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({"error": "No token provided"}), 401
        
        teacher_data = decode_token(token)
        if not teacher_data or 'id' not in teacher_data:
            return jsonify({"error": "Invalid or expired token"}), 401
        
        teacher_id = teacher_data['id']
        
        unreleased_quizzes = UnreleasedQuiz.get_by_teacher(teacher_id)
        released_quizzes = Quiz.get_by_teacher(teacher_id)
        
        return jsonify({
            "unreleased_quizzes": unreleased_quizzes,
            "released_quizzes": released_quizzes
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
def add_tab_switch_event():
    try:
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({"error": "No token provided"}), 401
        
        student_data = decode_token(token)
        if not student_data or 'id' not in student_data:
            return jsonify({"error": "Invalid or expired student token"}), 401
        
        student_id = student_data['id']
        student_name = student_data['name']
        student_usn = student_data['usn']
        
        data = request.get_json()
        if not data or 'quiz_id' not in data:
            return jsonify({"error": "Missing quiz_id in the request body"}), 400

        quiz_id = data['quiz_id']
        
        timestamp = datetime.now(timezone.utc)
        
        event = TabSwitchEvent(
            quiz_id=quiz_id,
            student_id=student_id,
            student_name=student_name,
            usn=student_usn,
            timestamp=timestamp
        )
        event.save()
        
        return jsonify({"message": "Tab switch event added successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def get_tab_switch_events_by_quiz_id(quiz_id):
    try:
        if not quiz_id:
            return jsonify({"error": "Missing quiz_id in the request"}), 400

        events = TabSwitchEvent.get_by_quiz_id(quiz_id)
        if not events:
            return jsonify({"tab_switch_events": []}), 200

        return jsonify({"tab_switch_events": [event.__dict__ for event in events]}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def release_quiz():
    try:
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({"error": "No token provided"}), 401
        
        teacher_data = decode_token(token)
        if not teacher_data or 'id' not in teacher_data:
            return jsonify({"error": "Invalid or expired token"}), 401
        
        data = request.get_json()
        quiz_id = data.get('quiz_id')
        if not quiz_id:
            return jsonify({"error": "Missing quiz_id"}), 400

        unreleased_quiz = UnreleasedQuiz.get_by_id(quiz_id)
        if not unreleased_quiz:
            return jsonify({"error": "Quiz not found in unreleased tests"}), 404

        # Pass questions as-is (it’s already a JSON string from the database or a dict to be serialized in Quiz.save())
        released_quiz = Quiz(
            quiz_name=unreleased_quiz['quiz_name'],
            section=unreleased_quiz['section'],
            batch_year=unreleased_quiz['batch_year'],
            department=unreleased_quiz['department'],
            teacher_id=unreleased_quiz['teacher_id'],
            questions=unreleased_quiz['questions'],  # Let Quiz.save() handle serialization
            timer=unreleased_quiz['timer']
        )
        released_quiz.save()

        UnreleasedQuiz.delete_by_id(quiz_id)

        return jsonify({"message": "Quiz released successfully", "quiz_id": released_quiz.id}), 200
    except Exception as e:
        return jsonify({"error": f"Failed to release quiz: {str(e)}"}), 500