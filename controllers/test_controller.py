from flask import request, jsonify
from models.models import UnreleasedQuiz
from utils.decode import decode_token
import json

def create_quiz():
    try:
        data = request.get_json()
        token = request.headers.get('Authorization')
        
        if not all(key in data for key in ['quizDetails', 'questions']):
            return jsonify({"error": "Missing required fields"}), 400
        
        quiz_details = data['quizDetails']
        questions = data['questions']

        if not all(key in quiz_details for key in ['department', 'batch', 'section', 'testID', 'testName', 'timer']):
            return jsonify({"error": "Invalid quiz details"}), 400

        teacher_details = decode_token(token)
        if not teacher_details:
            return jsonify({"error": "Invalid or expired token"}), 401
        
        new_quiz = UnreleasedQuiz(
            quiz_name=quiz_details['testName'],
            section=quiz_details['section'],
            batch_year=quiz_details['batch'],
            department=quiz_details['department'],
            teacher_id=teacher_details['id'],
            questions=questions,
            timer=quiz_details['timer']
        )
        new_quiz.save()

        return jsonify({"message": "Quiz created and saved as unreleased", "quiz_id": new_quiz.id}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500