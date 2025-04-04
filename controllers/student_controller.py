import json
import random
from flask import request, jsonify
from models.models import Quiz, Score
from utils.decode import decode_token
from datetime import datetime, timezone

def get_quizzes_for_logged_in_student():
    try:
        token = request.headers.get('Authorization')
        
        student_data = decode_token(token)
        if not student_data or 'id' not in student_data:
            return jsonify({"error": "Invalid or expired token"}), 401
        
        student_id = student_data['id']
        department = student_data['department']
        section = student_data['section']
        batch_year = student_data['batch_year']
        
        quizzes = Quiz.get_by_section_batch_and_department(section, batch_year, department)
        
        if not quizzes:
            return jsonify({"message": "No quizzes found for your department, section, and batch year"}), 200
        
        quizzes_data = [
            {
                "id": quiz.id,
                "quiz_name": quiz.quiz_name,
                "section": quiz.section,
                "batch_year": quiz.batch_year,
                "department": quiz.department,
                "teacher_id": quiz.teacher_id,
                "timer": quiz.timer,
                "number_of_questions": quiz.number_of_questions  # New field
            }
            for quiz in quizzes
        ]
        
        return jsonify({"quizzes": quizzes_data}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

def save_score():
    try:
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({"error": "No token provided"}), 401

        student_data = decode_token(token)
        if not student_data or 'id' not in student_data:
            return jsonify({"error": "Invalid or expired token"}), 401

        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400

        print("Received submission:", data)

        quiz_id = data.get('quiz_id')
        score = data.get('score')

        if not quiz_id:
            return jsonify({"error": "quiz_id is required"}), 400
        if score is None:
            return jsonify({"error": "score is required"}), 400

        existing_score = Score.get_by_student_and_quiz(student_data['id'], quiz_id)
        if existing_score:
            return jsonify({
                "message": "Already submitted", 
                "score": existing_score['score']
            }), 200

        new_score = Score(
            student_id=student_data['id'],
            quiz_id=quiz_id,
            student_name=student_data.get('name', ''),
            usn=student_data.get('usn', ''),
            score=score,
            section=student_data.get('section', ''),
            department=student_data.get('department', ''),
            submission_time=datetime.now(timezone.utc)
        )
        new_score.save()

        print(f"Saved score: {score} for quiz {quiz_id}")
        return jsonify({
            "message": "Score saved successfully!",
            "score": score
        }), 201

    except Exception as e:
        print("Error in save_score:", str(e))
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

def get_questions_by_quiz_id():
    try:
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({"error": "No token provided"}), 401

        quiz_id = request.args.get('quiz_id')
        quiz_name = request.args.get('quiz_name')

        if not quiz_id or not quiz_name:
            return jsonify({"message": "quiz_id and quiz_name are required"}), 400

        quiz = Quiz.get_by_name_and_id(quiz_name, quiz_id)
        if not quiz:
            return jsonify({"message": "No quiz found with the provided name and ID"}), 404

        try:
            questions = json.loads(quiz["questions"]) if isinstance(quiz["questions"], str) else quiz["questions"]
        except json.JSONDecodeError:
            return jsonify({"error": "Failed to parse questions data"}), 500

        number_of_questions = quiz["number_of_questions"]
        if number_of_questions > 0 and len(questions) > number_of_questions:
            selected_questions = random.sample(questions, number_of_questions)
        else:
            selected_questions = questions.copy()

        for question in selected_questions:
            if question["type"] == "mcq":
                options = question["options"]
                correct_option = question["correctOption"]
                option_pairs = list(enumerate(options))
                random.shuffle(option_pairs)
                question["options"] = [opt for _, opt in option_pairs]
                question["correctOption"] = next(i for i, (_, opt) in enumerate(option_pairs) if opt == options[correct_option])

        quiz_data = {
            "id": quiz["id"],
            "quiz_name": quiz["quiz_name"],
            "section": quiz["section"],
            "batch_year": quiz["batch_year"],
            "department": quiz["department"],
            "teacher_id": quiz["teacher_id"],
            "timer": quiz["timer"],
            "number_of_questions": quiz["number_of_questions"],  # New field
            "questions": selected_questions
        }
        return jsonify({"quiz": quiz_data}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def get_quizzes_by_student_id():
    try:
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({"error": "No token provided"}), 401

        student_data = decode_token(token)
        if not student_data or 'id' not in student_data:
            return jsonify({"error": "Invalid or expired token"}), 401
        print("student data is", student_data)

        student_id = student_data['id']
        student_name = student_data['name']
        section = student_data['section']
        department = student_data['department']

        scores = Score.get_quizzes_by_student_id(student_id)
        print("scores are", scores)
        if not scores:
            return jsonify({"quiz_ids": []}), 200

        quiz_ids = list({score['quiz_id'] for score in scores})
        return jsonify({"quiz_ids": quiz_ids}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

def leaderboard(quiz_id):
    try:
        if not quiz_id:
            return jsonify({"error": "quiz_id is required"}), 400
        
        scores = Score.get_scores_by_quiz(quiz_id)
        
        if not scores:
            return jsonify({"leaderboard": []}), 200

        sorted_scores = sorted(
            scores,
            key=lambda x: (
                -x['score'],
                x['submission_time'] or "9999-12-31"
            )
        )
        print("sorted scores are", sorted_scores)

        leaderboard_data = []
        rank = 1
        previous_score = None
        previous_time = None

        for score in sorted_scores:
            current_score = score['score']
            current_time = score['submission_time']
            
            if (current_score, current_time) != (previous_score, previous_time):
                rank = len(leaderboard_data) + 1

            leaderboard_data.append({
                "rank": rank,
                "student_name": score['student_name'],
                "score": current_score,
                "submission_time": current_time or "Not submitted",
                "usn": score['usn']
            })
            
            previous_score = current_score
            previous_time = current_time

        return jsonify({"leaderboard": leaderboard_data}), 200

    except Exception as e:
        print(f"Error in leaderboard endpoint: {str(e)}")
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500
    try:
        if not quiz_id:
            return jsonify({"error": "quiz_id is required"}), 400
        
        # Fetch all scores for the given quiz
        scores = Score.get_scores_by_quiz(quiz_id)
        
        if not scores:
            return jsonify({"leaderboard": []}), 200

        # Sort scores by score (descending) and submission time (ascending)
        # Handle None submission times by putting them last
        sorted_scores = sorted(
            scores,
            key=lambda x: (
                -x['score'],
                x['submission_time'] or "9999-12-31"  # Push nulls to end
            )
        )
        print("sorted scores are",sorted_scores)

        # Assign ranks to the sorted scores
        leaderboard_data = []
        rank = 1
        previous_score = None
        previous_time = None

        for score in sorted_scores:
            current_score = score['score']
            current_time = score['submission_time']
            
            # Only increment rank if score or time changes
            if (current_score, current_time) != (previous_score, previous_time):
                rank = len(leaderboard_data) + 1

            leaderboard_data.append({
                "rank": rank,
                "student_name": score['student_name'],
                "score": current_score,
                "submission_time": current_time or "Not submitted",
                 "usn": score['usn']
            })
            
            previous_score = current_score
            previous_time = current_time

        return jsonify({"leaderboard": leaderboard_data}), 200

    except Exception as e:
        print(f"Error in leaderboard endpoint: {str(e)}")
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500