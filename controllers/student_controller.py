import json
from flask import request, jsonify
from models.models import Quiz, Score
from utils.decode import decode_token
from datetime import datetime,timezone

def get_quizzes_for_logged_in_student():
    try:
        # Extract the token from cookies
        token = request.headers.get('Authorization')
        
        # Decode the token to get student information
        student_data = decode_token(token)
        if not student_data or 'id' not in student_data:
            return jsonify({"error": "Invalid or expired token"}), 401
        
        # Extract necessary information from the token
        student_id = student_data['id']
        department = student_data['department']
        section = student_data['section']
        batch_year = student_data['batch_year']# You might need to add this if it's in the token
        
        # Fetch quizzes based on the department, section, and batch_year (from token)
        quizzes = Quiz.get_by_section_batch_and_department(section, batch_year, department)
        
        if not quizzes:
            return jsonify({"message": "No quizzes found for your department, section, and batch year"}), 200
        
        # Serialize quizzes to JSON
        quizzes_data = [
            {
                "id": quiz.id,
                "quiz_name": quiz.quiz_name,
                "section": quiz.section,
                "batch_year": quiz.batch_year,
                "department": quiz.department,
                "teacher_id": quiz.teacher_id,
                "timer": quiz.timer,
                 # Assuming questions are serialized as a string or text
            }
            for quiz in quizzes
        ]
        
        return jsonify({"quizzes": quizzes_data}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    



def save_score():
    try:
        # Extract the token from cookies
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({"error": "No token provided"}), 401

        # Decode the token to get student information
        student_data = decode_token(token)
        if not student_data or 'id' not in student_data:
            return jsonify({"error": "Invalid or expired token"}), 401
        print("student data is",student_data)
        # Extract necessary student information
        student_id = student_data['id']
        student_name = student_data['name']
        section = student_data['section']
        department = student_data['department']
        print("id is",student_id, student_name, section, department)
        # Validate request payload
        data = request.get_json()
        if not data:
            return jsonify({"error": "Request body is required"}), 400
        
        quiz_id = data['quiz_id']
        score = data['score']

        if not quiz_id:
            return jsonify({"error": "quiz_id is required"}), 400
        if score is None:
            return jsonify({"error": "score is required"}), 400
        
        # Check if the student already has a score for this quiz
        existing_score = Score.get_by_student_and_quiz(student_id, quiz_id)
        print("existing score is",existing_score)
        if existing_score:
            return jsonify({"message": "Score for this quiz has already been submitted."}), 400

        # Save the new score along with the timestamp
        submission_time = datetime.now(timezone.utc)  # Use UTC for consistency
        new_score = Score(
            student_id=student_id,
            quiz_id=quiz_id,
            student_name=student_name,
            score=score,
            section=section,
            department=department,
            submission_time=submission_time
        )
        new_score.save()

        return jsonify({"message": "Score saved successfully!"}), 201

    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500


# def get_questions_by_quiz_id():
#     try:
#         token = request.headers.get('Authorization')  # Extract token from headers

#         # Extract quiz_id and quiz_name from query parameters
#         quiz_id = request.args.get('quiz_id')
#         quiz_name = request.args.get('quiz_name')

#         if not quiz_id or not quiz_name:
#             return jsonify({"message": "quiz_id and quiz_name are required"}), 400

#         # Retrieve the quiz from the database
#         quiz = Quiz.get_by_name_and_id(quiz_name, quiz_id)

#         if not quiz:
#             return jsonify({"message": "No quiz found with the provided name and ID"}), 404

#         # Prepare quiz data
#         quiz_data = {
#             "id": quiz["id"],
#             "quiz_name": quiz["quiz_name"],
#             "section": quiz["section"],
#             "batch_year": quiz["batch_year"],
#             "department": quiz["department"],
#             "teacher_id": quiz["teacher_id"],
#             "questions": quiz["questions"],
#             "timer": quiz["timer"]
#         }
#         return jsonify({"quiz": quiz_data}), 200
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500


def get_questions_by_quiz_id():
    try:
        token = request.headers.get('Authorization')  # Extract token from headers

        # Extract quiz_id and quiz_name from query parameters
        quiz_id = request.args.get('quiz_id')
        quiz_name = request.args.get('quiz_name')

        if not quiz_id or not quiz_name:
            return jsonify({"message": "quiz_id and quiz_name are required"}), 400

        # Retrieve the quiz from the database
        quiz = Quiz.get_by_name_and_id(quiz_name, quiz_id)

        if not quiz:
            return jsonify({"message": "No quiz found with the provided name and ID"}), 404

        # Deserialize the questions field if it's stored as a JSON string
        try:
            questions = json.loads(quiz["questions"]) if isinstance(quiz["questions"], str) else quiz["questions"]
        except json.JSONDecodeError:
            return jsonify({"error": "Failed to parse questions data"}), 500

        # Prepare quiz data
        quiz_data = {
            "id": quiz["id"],
            "quiz_name": quiz["quiz_name"],
            "section": quiz["section"],
            "batch_year": quiz["batch_year"],
            "department": quiz["department"],
            "teacher_id": quiz["teacher_id"],
            "questions": questions,  # Properly parsed questions array
        }
        return jsonify({"quiz": quiz_data}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def get_quizzes_by_student_id():
    try:
        # Extract student_id from query parameters
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({"error": "No token provided"}), 401

        # Decode the token to get student information
        student_data = decode_token(token)
        if not student_data or 'id' not in student_data:
            return jsonify({"error": "Invalid or expired token"}), 401
        print("student data is",student_data)
        # Extract necessary student information
        student_id = student_data['id']
        student_name = student_data['name']
        section = student_data['section']
        department = student_data['department']

        # Fetch all quizzes attempted by the student
        scores = Score.get_quizzes_by_student_id(student_id)
        print("scores are",scores)
        if not scores:
            return jsonify({"quiz_ids": []}), 200



        # Extract unique quiz IDs
        quiz_ids = list({score['quiz_id'] for score in scores})

        return jsonify({"quiz_ids": quiz_ids}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
from datetime import datetime
from flask import jsonify

def leaderboard(quiz_id):
    try:
        # Validate quiz_id
        if not quiz_id:
            return jsonify({"error": "quiz_id is required"}), 400
        
        # Fetch all scores for the given quiz
        scores = Score.get_scores_by_quiz(quiz_id)
        
        # If no scores are found, return an empty leaderboard
        if not scores:
            return jsonify({"leaderboard": []}), 200

        # Sort scores by score (descending) and submission time (ascending)
        sorted_scores = sorted(
            scores,
            key=lambda x: (-x['score'], datetime.fromisoformat(x['submission_time']))
        )

        # Assign ranks to the sorted scores
        leaderboard_data = []
        rank = 1
        previous_score = None
        previous_time = None

        for score in sorted_scores:
            if (score['score'], score['submission_time']) != (previous_score, previous_time):
                rank = len(leaderboard_data) + 1  # Update rank only if score or time changes

            leaderboard_data.append({
                "rank": rank,
                "student_name": score['student_name'],
                "score": score['score'],
                "submission_time": score['submission_time']
            })
            previous_score = score['score']
            previous_time = score['submission_time']

        return jsonify({"leaderboard": leaderboard_data}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

