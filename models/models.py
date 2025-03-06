from db.db import get_db
import json

class Student:
    def __init__(self, name, email, section, department, batch_year, password, id=None):
        self.id = id  # Optional, as id will be auto-generated
        self.name = name
        self.email = email
        self.section = section
        self.department = department
        self.batch_year = batch_year
        self.password = password

    def save(self):
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            'INSERT INTO students (name, email, section, department, batch_year, password) VALUES (?, ?, ?, ?, ?, ?)',
            (self.name, self.email, self.section, self.department, self.batch_year, self.password)
        )
        db.commit()
        self.id = cursor.lastrowid  # Retrieve the last inserted ID

    @classmethod
    def get_by_email(cls, email):
        db = get_db()
        student = db.execute(
            'SELECT * FROM students WHERE email = ?', (email,)
        ).fetchone()
        if student:
            return cls(
                id=student['id'],
                name=student['name'],
                email=student['email'],
                section=student['section'],
                department=student['department'],
                batch_year=student['batch_year'],
                password=student['password']
            )
        return None


class Teacher:
    def __init__(self, name, email, department, password, id=None):
        self.id = id  # Optional, as id will be auto-generated
        self.name = name
        self.email = email
        self.department = department
        self.password = password

    def save(self):
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            'INSERT INTO teachers (name, email, department, password) VALUES (?, ?, ?, ?)',
            (self.name, self.email, self.department, self.password)
        )
        db.commit()
        self.id = cursor.lastrowid  # Retrieve the last inserted ID

    @classmethod
    def get_by_email(cls, email):
        db = get_db()
        teacher = db.execute(
            'SELECT * FROM teachers WHERE email = ?', (email,)
        ).fetchone()
        if teacher:
            return cls(
                id=teacher['id'],
                name=teacher['name'],
                email=teacher['email'],
                department=teacher['department'],
                password=teacher['password']
            )
        return None

class Quiz:
    def __init__(self, quiz_name, section, batch_year, department, teacher_id, questions, timer, id=None):
        self.id = id  # This allows id to be optional, especially for new quizzes
        self.quiz_name = quiz_name
        self.section = section
        self.batch_year = batch_year
        self.department = department
        self.teacher_id = teacher_id
        self.questions = questions
        self.timer = timer  # New field for storing timer

    def save(self):
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            'INSERT INTO quizzes (quiz_name, section, batch_year, department, teacher_id, questions, timer) VALUES (?, ?, ?, ?, ?, ?, ?)',
            (self.quiz_name, self.section, self.batch_year, self.department, self.teacher_id, self.questions, self.timer)
        )
        db.commit()
        self.id = cursor.lastrowid  # Retrieve the last inserted ID

    @classmethod
    def get_by_section(cls, section):
        """
        Retrieve quizzes from the database by section.
        """
        db = get_db()
        quizzes = db.execute(
            'SELECT * FROM quizzes WHERE section = ?', (section,)
        ).fetchall()

        if quizzes:
            return [cls(
                quiz_name=quiz['quiz_name'],
                section=quiz['section'],
                batch_year=quiz['batch_year'],
                department=quiz['department'],
                teacher_id=quiz['teacher_id'],
                questions=quiz['questions'],  # Assuming questions are stored as JSON string
                timer=quiz['timer']  # Deserialize the timer
            ) for quiz in quizzes]
        return []

    @classmethod
    def get_by_teacher(cls, teacher_id):
        """
        Retrieve quizzes from the database by teacher_id.
        """
        db = get_db()
        quizzes = db.execute(
            'SELECT * FROM quizzes WHERE teacher_id = ?', (teacher_id,)
        ).fetchall()

        if quizzes:
            return [
                {
                    "id": quiz["id"],
                    "quiz_name": quiz["quiz_name"],
                    "section": quiz["section"],
                    "batch_year": quiz["batch_year"],
                    "department": quiz["department"],
                    "teacher_id": quiz["teacher_id"],
                    "questions": quiz["questions"],  # Assuming questions are stringified JSON
                    "timer": quiz["timer"]  # Adding timer here
                }
                for quiz in quizzes
            ]
        return []

    @classmethod
    def get_by_name_and_teacher(cls, quiz_name, teacher_id):
        """
        Retrieve a quiz from the database by quiz_name and teacher_id.
        """
        db = get_db()
        quiz = db.execute(
            'SELECT * FROM quizzes WHERE quiz_name = ? AND teacher_id = ?',
            (quiz_name, teacher_id)
        ).fetchone()

        if quiz:
            return cls(
                quiz_name=quiz['quiz_name'],
                section=quiz['section'],
                batch_year=quiz['batch_year'],
                department=quiz['department'],
                teacher_id=quiz['teacher_id'],
                questions=quiz['questions'],  # Deserialize the JSON questions
                timer=quiz['timer']  # Return the timer value
            )
        return None

    @classmethod
    def get_by_section_batch_and_department(cls, section, batch_year, department):
        """
        Retrieve quizzes from the database by section, batch_year, and department.
        """
        db = get_db()
        quizzes = db.execute(
            'SELECT * FROM quizzes WHERE section = ? AND batch_year = ? AND department = ?',
            (section, batch_year, department)
        ).fetchall()

        if quizzes:
            return [cls(
                id=quiz['id'],
                quiz_name=quiz['quiz_name'],
                section=quiz['section'],
                batch_year=quiz['batch_year'],
                department=quiz['department'],
                teacher_id=quiz['teacher_id'],
                questions=quiz['questions'],  # Deserialize the JSON questions
                timer=quiz['timer']  # Include the timer
            ) for quiz in quizzes]
        return []
    
    @classmethod
    def get_by_name_and_id(cls, quiz_name, quiz_id):
        """
        Retrieve a quiz from the database by quiz_name and id.
        """
        db = get_db()
        quiz = db.execute(
            'SELECT * FROM quizzes WHERE quiz_name = ? AND id = ?',
            (quiz_name, quiz_id)
        ).fetchone()

        if quiz:
            return {
                "id": quiz['id'],
                "quiz_name": quiz['quiz_name'],
                "section": quiz['section'],
                "batch_year": quiz['batch_year'],
                "department": quiz['department'],
                "teacher_id": quiz['teacher_id'],
                "questions": quiz['questions'],  # Assuming questions are stored as JSON string
                "timer": quiz['timer']  # Include the timer
            }
        return None
class Score:
    def __init__(self, student_id, quiz_id, student_name, score, section, department, submission_time, id=None):
        self.id = id  # Optional, as id will be auto-generated
        self.student_id = student_id
        self.quiz_id = quiz_id
        self.student_name = student_name
        self.score = score
        self.section = section
        self.department = department
        self.submission_time = submission_time

    def save(self):
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            'INSERT INTO scores (student_id, quiz_id, student_name, score, section, department, submitted_at) VALUES (?, ?, ?, ?, ?, ?, ?)',
            (self.student_id, self.quiz_id, self.student_name, self.score, self.section, self.department, self.submission_time)
        )
        db.commit()
        self.id = cursor.lastrowid  # Retrieve the last inserted ID

    @classmethod
    def get_by_student_and_quiz(cls, student_id, quiz_id):
        """
        Retrieve a score for a specific student and quiz as a dictionary.
        """
        db = get_db()
        score = db.execute(
            'SELECT * FROM scores WHERE student_id = ? AND quiz_id = ?',
            (student_id, quiz_id)
        ).fetchone()
        if score:
            return {
                "id": score['id'],
                "student_id": score['student_id'],
                "student_name": score['student_name'],
                "quiz_id": score['quiz_id'],
                "score": score['score'],
                "section": score['section'],
                "department": score['department'],
                "submission_time": score['submitted_at']
            }
        return None

    @classmethod
    def get_quizzes_by_student_id(cls, student_id):
        """
        Retrieve unique quiz IDs attempted by a specific student as a list of dictionaries.
        """
        db = get_db()
        quizzes = db.execute(
            'SELECT DISTINCT quiz_id FROM scores WHERE student_id = ?',
            (student_id,)
        ).fetchall()
        return [{"quiz_id": quiz["quiz_id"]} for quiz in quizzes] if quizzes else []

    @classmethod
    def get_scores_by_quiz(cls, quiz_id):
        """
        Retrieve all scores for a specific quiz as a list of dictionaries.
        """
        db = get_db()
        scores = db.execute(
            'SELECT * FROM scores WHERE quiz_id = ?',
            (quiz_id,)
        ).fetchall()
        return [
            {
                "id": score['id'],
                "student_id": score['student_id'],
                "student_name": score['student_name'],
                "quiz_id": score['quiz_id'],
                "score": score['score'],
                "section": score['section'],
                "department": score['department'],
                "submission_time": score['submitted_at']
            }
            for score in scores
        ] if scores else []

from db.db import get_db

class TabSwitchEvent:
    def __init__(self, quiz_id, student_id, student_name, timestamp, id=None):
        self.id = id  # Optional, as id will be auto-generated
        self.quiz_id = quiz_id
        self.student_id = student_id
        self.student_name = student_name
        self.timestamp = timestamp

    def save(self):
        """
        Save the TabSwitchEvent to the database.
        """
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            'INSERT INTO tab_switch_events (quiz_id, student_id, student_name, timestamp) VALUES (?, ?, ?, ?)',
            (self.quiz_id, self.student_id, self.student_name, self.timestamp)
        )
        db.commit()
        self.id = cursor.lastrowid  # Retrieve the last inserted ID

    @classmethod
    def get_by_quiz_id(cls, quiz_id):
        """
        Retrieve all tab switch events for a specific quiz_id.
        """
        db = get_db()
        events = db.execute(
            'SELECT * FROM tab_switch_events WHERE quiz_id = ?',
            (quiz_id,)
        ).fetchall()

        if events:
            return [
                cls(
                    id=event['id'],
                    quiz_id=event['quiz_id'],
                    student_id=event['student_id'],
                    student_name=event['student_name'],
                    timestamp=event['timestamp']
                )
                for event in events
            ]
        return []

@classmethod
def get_by_quiz_id(cls, quiz_id):
    """
    Retrieve all tab switch events for a specific quiz_id.
    """
    db = get_db()
    events = db.execute(
        'SELECT * FROM tab_switch_events WHERE quiz_id = ?', (quiz_id,)
    ).fetchall()

    if events:
        return [
            cls(
                id=event['id'],
                quiz_id=event['quiz_id'],
                student_id=event['student_id'],
                student_name=event['student_name'],
                timestamp=event['timestamp']
            )
            for event in events
        ]
    return []

