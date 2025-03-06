from flask import request, jsonify
from models.models import Quiz
from utils.decode import decode_token
from datetime import datetime
import json

def create_quiz():
    try:
        # Get the data sent from the frontend in JSON format
        data = request.get_json()  # This extracts JSON data from the request
        token = request.headers.get('Authorization')
        print("token is",token)
        # Validate required fields
        if not all(key in data for key in [ 'quizDetails', 'questions']):
            return jsonify({"error": "Missing required fields"}), 400
        
        # Extract teacher details, token, quiz details, and questions from the data
        
        
        quiz_details = data['quizDetails']
        questions = data['questions']  # This will be a JSON string

        
        
        if not all(key in quiz_details for key in ['department', 'batch', 'section', 'testID', 'testName', 'timer']):
            return jsonify({"error": "Invalid quiz details"}), 400

        # Decode the teacher ID from the token
        teacher_details = decode_token(token)
        if not teacher_details:
            return jsonify({"error": "Invalid or expired token"}), 401
        
        # Check if the quiz already exists for the teacher
        existing_quiz = Quiz.get_by_name_and_teacher(quiz_details['testName'], teacher_details['id'])
        if existing_quiz:
            return jsonify({"error": "A quiz with this ID already exists for this teacher"}), 400
        
        # Store the questions as a JSON string
        quiz = Quiz(
            quiz_name=quiz_details['testName'],
            section=quiz_details['section'],
            batch_year=quiz_details['batch'],
            department=quiz_details['department'],
            id=quiz_details['testID'],
            timer=quiz_details['timer'],
            teacher_id=teacher_details['id'],  # Use teacher_id extracted from token
            questions=json.dumps(questions),  # Store the questions as a JSON string
             # Optionally, store the creation timestamp
        )
        
        quiz.save()  # Save the quiz to MongoDB or SQLite

        return jsonify({"message": "Quiz created successfully", "quiz_id": str(quiz.id)}), 201
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500
