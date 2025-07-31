from flask import request, jsonify
from models.models import Quiz, TabSwitchEvent, UnreleasedQuiz
from utils.decode import decode_token
from datetime import datetime, timezone
import json
import logging

# Configure logging
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
        
        logger.info(f"Retrieved {len(unreleased_quizzes)} unreleased and {len(released_quizzes)} released quizzes for teacher {teacher_id}")
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
        student_name = student_data.get('name', 'Unknown')
        student_usn = student_data.get('usn', 'Unknown')
        
        data = request.get_json()
        if not data or 'quiz_id' not in data:
            logger.warning("Missing quiz_id in request body")
            return jsonify({"error": "Missing quiz_id in the request body"}), 400

        quiz_id = data['quiz_id']
        try:
            quiz_id = int(quiz_id)
        except (ValueError, TypeError):
            logger.warning(f"Invalid quiz_id value: {quiz_id}")
            return jsonify({"error": "quiz_id must be an integer"}), 400
        
        timestamp = datetime.now(timezone.utc)
        logger.debug(f"Adding tab switch event for student {student_id}, quiz {quiz_id}")
        
        event = TabSwitchEvent(
            quiz_id=quiz_id,
            student_id=student_id,
            student_name=student_name,
            usn=student_usn,
            timestamp=timestamp
        )
        event.save()
        
        logger.info(f"Tab switch event added for student {student_id}, quiz {quiz_id}")
        return jsonify({"message": "Tab switch event added successfully"}), 201
    except Exception as e:
        logger.error(f"Error in add_tab_switch_event: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500

def get_tab_switch_events_by_quiz_id(quiz_id):
    try:
        if not quiz_id:
            logger.warning("Missing quiz_id in request")
            return jsonify({"error": "Missing quiz_id in the request"}), 400

        try:
            quiz_id = int(quiz_id)
        except (ValueError, TypeError):
            logger.warning(f"Invalid quiz_id value: {quiz_id}")
            return jsonify({"error": "quiz_id must be an integer"}), 400

        logger.debug(f"Fetching tab switch events for quiz {quiz_id}")
        events = TabSwitchEvent.get_by_quiz_id(quiz_id)

        
        events_data = [
            {
                "id": event.id,
                "student_name": getattr(event, "student_name", "Unknown"),
                "usn": getattr(event, "usn", "N/A"),
                "timestamp": event.timestamp.isoformat() if hasattr(event.timestamp, "isoformat") else str(event.timestamp),
            }
            for event in events
        ]

        logger.info(f"Retrieved {len(events_data)} tab switch events for quiz {quiz_id}")
        return jsonify({"tab_switch_events": events_data}), 200

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
        if not data or 'quiz_id' not in data:
            logger.warning("Missing quiz_id in request body")
            return jsonify({"error": "Missing quiz_id"}), 400
        
        quiz_id = data.get('quiz_id')
        try:
            quiz_id = int(quiz_id)
        except (ValueError, TypeError):
            logger.warning(f"Invalid quiz_id value: {quiz_id}")
            return jsonify({"error": "quiz_id must be an integer"}), 400

        logger.debug(f"Releasing quiz with ID {quiz_id}")
        unreleased_quiz = UnreleasedQuiz.get_by_id(quiz_id)
        if not unreleased_quiz:
            logger.warning(f"Quiz not found with ID {quiz_id}")
            return jsonify({"error": "Quiz not found in unreleased tests"}), 404

        released_quiz = Quiz(
            quiz_name=unreleased_quiz['quiz_name'],
            section=unreleased_quiz['section'],
            batch_year=unreleased_quiz['batch_year'],
            department=unreleased_quiz['department'],
            teacher_id=unreleased_quiz['teacher_id'],
            questions=unreleased_quiz['questions'],
            timer=unreleased_quiz['timer'],
            number_of_questions=unreleased_quiz['number_of_questions']
        )
        released_quiz.save()

        UnreleasedQuiz.delete_by_id(quiz_id)
        
        logger.info(f"Quiz released with ID {released_quiz.id}")
        return jsonify({"message": "Quiz released successfully", "quiz_id": released_quiz.id}), 200
    except Exception as e:
        logger.error(f"Error in release_quiz: {str(e)}", exc_info=True)
        return jsonify({"error": f"Failed to release quiz: {str(e)}"}), 500
