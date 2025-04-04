from flask import request, jsonify
from models.models import Quiz, TabSwitchEvent, UnreleasedQuiz
from utils.decode import decode_token
from datetime import datetime, timezone
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_quizzes_by_teacher():
    try:
        token = request.headers.get('Authorization')
        if not token:
            logger.warning("No token provided in request")
            return jsonify({"error": "No token provided"}), 401
        
        teacher_data = decode_token(token)
        if not teacher_data or 'id' not in teacher_data:
            logger.warning(f"Invalid or expired token: {token}")
            return jsonify({"error": "Invalid or expired token"}), 401
        
        teacher_id = teacher_data['id']
        logger.debug(f"Fetching quizzes for teacher ID {teacher_id}")
        
        unreleased_quizzes = UnreleasedQuiz.get_by_teacher(teacher_id)
        released_quizzes = Quiz.get_by_teacher(teacher_id)
        
        return jsonify({
            "unreleased_quizzes": unreleased_quizzes,
            "released_quizzes": released_quizzes
        }), 200
    except Exception as e:
        logger.error(f"Error in get_quizzes_by_teacher: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500

def add_tab_switch_event():
    try:
        token = request.headers.get('Authorization')
        if not token:
            logger.warning("No token provided in request")
            return jsonify({"error": "No token provided"}), 401
        
        student_data = decode_token(token)
        if not student_data or 'id' not in student_data:
            logger.warning(f"Invalid or expired student token: {token}")
            return jsonify({"error": "Invalid or expired student token"}), 401
        
        student_id = student_data['id']
        student_name = student_data['name']
        student_usn = student_data['usn']
        
        data = request.get_json()
        if not data or 'quiz_id' not in data:
            logger.warning("Missing quiz_id in request body")
            return jsonify({"error": "Missing quiz_id in the request body"}), 400

        quiz_id = data['quiz_id']
        timestamp = datetime.now(timezone.utc)
        logger.debug(f"Adding tab switch event for student {student_id}, quiz {quiz_id}")
        
        event = TabSwitchEvent(
            quiz_id=quiz_id, student_id=student_id, student_name=student_name,
            usn=student_usn, timestamp=timestamp
        )
        event.save()
        
        return jsonify({"message": "Tab switch event added successfully"}), 201
    except Exception as e:
        logger.error(f"Error in add_tab_switch_event: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500

def get_tab_switch_events_by_quiz_id(quiz_id):
    try:
        if not quiz_id:
            logger.warning("Missing quiz_id in request")
            return jsonify({"error": "Missing quiz_id in the request"}), 400

        logger.debug(f"Fetching tab switch events for quiz {quiz_id}")
        events = TabSwitchEvent.get_by_quiz_id(quiz_id)
        return jsonify({"tab_switch_events": [event.__dict__ for event in events]}), 200
    except Exception as e:
        logger.error(f"Error in get_tab_switch_events_by_quiz_id: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500

def release_quiz():
    try:
        token = request.headers.get('Authorization')
        if not token:
            logger.warning("No token provided in request")
            return jsonify({"error": "No token provided"}), 401
        
        teacher_data = decode_token(token)
        if not teacher_data or 'id' not in teacher_data:
            logger.warning(f"Invalid or expired token: {token}")
            return jsonify({"error": "Invalid or expired token"}), 401
        
        data = request.get_json()
        quiz_id = data.get('quiz_id')
        if not quiz_id:
            logger.warning("Missing quiz_id in request body")
            return jsonify({"error": "Missing quiz_id"}), 400

        logger.debug(f"Releasing quiz with ID {quiz_id}")
        unreleased_quiz = UnreleasedQuiz.get_by_id(quiz_id)
        if not unreleased_quiz:
            logger.warning(f"Quiz not found with ID {quiz_id}")
            return jsonify({"error": "Quiz not found in unreleased tests"}), 404

        released_quiz = Quiz(
            quiz_name=unreleased_quiz['quiz_name'], section=unreleased_quiz['section'],
            batch_year=unreleased_quiz['batch_year'], department=unreleased_quiz['department'],
            teacher_id=unreleased_quiz['teacher_id'], questions=unreleased_quiz['questions'],
            timer=unreleased_quiz['timer'], number_of_questions=unreleased_quiz['number_of_questions']
        )
        released_quiz.save()
        UnreleasedQuiz.delete_by_id(quiz_id)

        logger.info(f"Quiz released with ID {released_quiz.id}")
        return jsonify({"message": "Quiz released successfully", "quiz_id": released_quiz.id}), 200
    except Exception as e:
        logger.error(f"Error in release_quiz: {str(e)}", exc_info=True)
        return jsonify({"error": f"Failed to release quiz: {str(e)}"}), 500

def create_quiz():
    try:
        data = request.get_json()
        token = request.headers.get('Authorization')
        logger.debug(f"Received quiz creation request: {data}")
        
        if not token:
            logger.warning("No token provided in request")
            return jsonify({"error": "No token provided"}), 401
        
        if not data or not all(key in data for key in ['quizDetails', 'questions']):
            logger.warning("Missing required fields in request body")
            return jsonify({"error": "Missing required fields"}), 400
        
        quiz_details = data['quizDetails']
        questions = data['questions']
        required_fields = ['department', 'batch', 'section', 'testID', 'testName', 'timer', 'numberOfQuestions']
        
        if not all(key in quiz_details for key in required_fields):
            missing = [key for key in required_fields if key not in quiz_details]
            logger.warning(f"Invalid quiz details, missing: {missing}")
            return jsonify({"error": f"Invalid quiz details, missing: {missing}"}), 400

        teacher_details = decode_token(token)
        if not teacher_details or 'id' not in teacher_details:
            logger.warning(f"Invalid or expired token: {token}")
            return jsonify({"error": "Invalid or expired token"}), 401
        
        try:
            number_of_questions = int(quiz_details['numberOfQuestions'])
            if number_of_questions < 0:
                logger.warning("numberOfQuestions cannot be negative")
                return jsonify({"error": "numberOfQuestions cannot be negative"}), 400
        except ValueError:
            logger.warning("Invalid numberOfQuestions value")
            return jsonify({"error": "numberOfQuestions must be an integer"}), 400

        try:
            parsed_questions = json.loads(questions) if isinstance(questions, str) else questions
            if number_of_questions > len(parsed_questions):
                logger.warning(f"numberOfQuestions ({number_of_questions}) exceeds total questions ({len(parsed_questions)})")
                return jsonify({"error": "numberOfQuestions exceeds total questions"}), 400
        except json.JSONDecodeError:
            logger.error("Failed to parse questions JSON")
            return jsonify({"error": "Invalid questions JSON format"}), 400

        logger.debug(f"Creating quiz for teacher ID {teacher_details['id']}")
        new_quiz = UnreleasedQuiz(
            quiz_name=quiz_details['testName'], section=quiz_details['section'],
            batch_year=quiz_details['batch'], department=quiz_details['department'],
            teacher_id=teacher_details['id'], questions=questions,
            timer=quiz_details['timer'], number_of_questions=number_of_questions
        )
        new_quiz.save()

        logger.info(f"Quiz created with ID {new_quiz.id}")
        return jsonify({"message": "Quiz created and saved as unreleased", "quiz_id": new_quiz.id}), 201
    except Exception as e:
        logger.error(f"Error in create_quiz: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500