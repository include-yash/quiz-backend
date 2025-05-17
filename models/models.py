import time
from db.db import get_db
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Student:
    def __init__(self, usn, name, email, section, department, batch_year, password, id=None):
        self.id = id 
        self.usn = usn
        self.name = name
        self.email = email
        self.section = section
        self.department = department
        self.batch_year = batch_year
        self.password = password

    def save(self):
        db = get_db()
        cursor = db.cursor()
        try:
            cursor.execute(
                'INSERT INTO students (usn, name, email, section, department, batch_year, password) VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id',
                (self.usn, self.name, self.email, self.section, self.department, self.batch_year, self.password)
            )
            self.id = cursor.fetchone()[0]
            logger.info(f"Saved student with ID {self.id}")
        except Exception as e:
            logger.error(f"Error saving student: {str(e)}")
            raise

    @classmethod
    def get_by_email(cls, email):
        db = get_db()
        cursor = db.cursor()
        try:
            cursor.execute(
                'SELECT id, usn, name, email, section, department, batch_year, password FROM students WHERE email = %s', 
                (email,)
            )
            student = cursor.fetchone()
            if not student:
                logger.debug(f"No student found with email {email}")
                return None
            if len(student) < 8:
                raise ValueError("Invalid student data structure from database")
            logger.debug(f"Retrieved student with email {email}")
            return cls(
                id=student[0], usn=student[1], name=student[2], email=student[3],
                section=student[4], department=student[5], batch_year=student[6], password=student[7]
            )
        except Exception as e:
            logger.error(f"Error fetching student by email {email}: {str(e)}")
            raise

class Teacher:
    def __init__(self, name, email, department, password, id=None):
        self.id = id
        self.name = name
        self.email = email
        self.department = department
        self.password = password

    def save(self):
        db = get_db()
        cursor = db.cursor()
        try:
            cursor.execute(
                'INSERT INTO teachers (name, email, department, password) VALUES (%s, %s, %s, %s) RETURNING id',
                (self.name, self.email, self.department, self.password)
            )
            self.id = cursor.fetchone()[0]
            logger.info(f"Saved teacher with ID {self.id}")
        except Exception as e:
            logger.error(f"Error saving teacher: {str(e)}")
            raise

    @classmethod
    def get_by_email(cls, email):
        db = get_db()
        cursor = db.cursor()
        try:
            cursor.execute('SELECT * FROM teachers WHERE email = %s', (email,))
            teacher = cursor.fetchone()
            if teacher:
                logger.debug(f"Retrieved teacher with email {email}")
                return cls(id=teacher[0], name=teacher[1], email=teacher[2], department=teacher[3], password=teacher[4])
            logger.debug(f"No teacher found with email {email}")
            return None
        except Exception as e:
            logger.error(f"Error fetching teacher by email {email}: {str(e)}")
            raise

class UnreleasedQuiz:
    def __init__(self, quiz_name, section, batch_year, department, teacher_id, questions, timer, number_of_questions=0, id=None):
        self.id = id
        self.quiz_name = quiz_name
        self.section = section
        self.batch_year = batch_year
        self.department = department
        self.teacher_id = teacher_id
        self.questions = questions
        self.timer = timer
        self.number_of_questions = number_of_questions

    def save(self):
        db = get_db()
        cursor = db.cursor()
        try:
            questions_json = self.questions if isinstance(self.questions, str) else json.dumps(self.questions)
            cursor.execute(
                'INSERT INTO unreleasedTests (quiz_name, section, batch_year, department, teacher_id, questions, timer, number_of_questions) '
                'VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING id',
                (self.quiz_name, self.section, self.batch_year, self.department, self.teacher_id, questions_json, self.timer, self.number_of_questions)
            )
            self.id = cursor.fetchone()[0]
            logger.info(f"Saved unreleased quiz with ID {self.id}")
        except Exception as e:
            logger.error(f"Error saving unreleased quiz: {str(e)}")
            raise

    @classmethod
    def get_by_teacher(cls, teacher_id):
        db = get_db()
        cursor = db.cursor()
        try:
            cursor.execute('SELECT * FROM unreleasedTests WHERE teacher_id = %s', (teacher_id,))
            quizzes = cursor.fetchall()
            logger.debug(f"Retrieved {len(quizzes)} unreleased quizzes for teacher {teacher_id}")
            return [
                {
                    "id": quiz[0], "quiz_name": quiz[1], "section": quiz[2], "batch_year": quiz[3],
                    "department": quiz[4], "teacher_id": quiz[5], "questions": quiz[6],
                    "timer": quiz[7], "number_of_questions": quiz[8]
                } for quiz in quizzes
            ] if quizzes else []
        except Exception as e:
            logger.error(f"Error fetching unreleased quizzes for teacher {teacher_id}: {str(e)}")
            raise

    @classmethod
    def get_by_id(cls, quiz_id):
        db = get_db()
        cursor = db.cursor()
        try:
            cursor.execute('SELECT * FROM unreleasedTests WHERE id = %s', (quiz_id,))
            quiz = cursor.fetchone()
            if quiz:
                logger.debug(f"Retrieved unreleased quiz with ID {quiz_id}")
                return {
                    "id": quiz[0], "quiz_name": quiz[1], "section": quiz[2], "batch_year": quiz[3],
                    "department": quiz[4], "teacher_id": quiz[5], "questions": quiz[6],
                    "timer": quiz[7], "number_of_questions": quiz[8]
                }
            logger.debug(f"No unreleased quiz found with ID {quiz_id}")
            return None
        except Exception as e:
            logger.error(f"Error fetching unreleased quiz by ID {quiz_id}: {str(e)}")
            raise

    @classmethod
    def delete_by_id(cls, quiz_id):
        db = get_db()
        cursor = db.cursor()
        try:
            cursor.execute('DELETE FROM unreleasedTests WHERE id = %s', (quiz_id,))
            logger.info(f"Deleted unreleased quiz with ID {quiz_id}")
        except Exception as e:
            logger.error(f"Error deleting unreleased quiz with ID {quiz_id}: {str(e)}")
            raise

class Quiz:
    def __init__(self, quiz_name, section, batch_year, department, teacher_id, questions, timer, number_of_questions=0, id=None):
        self.id = id
        self.quiz_name = quiz_name
        self.section = section
        self.batch_year = batch_year
        self.department = department
        self.teacher_id = teacher_id
        self.questions = questions
        self.timer = timer
        self.number_of_questions = number_of_questions

    def save(self):
        db = get_db()
        cursor = db.cursor()
        try:
            questions_json = self.questions if isinstance(self.questions, str) else json.dumps(self.questions)
            cursor.execute(
                'INSERT INTO quizzes (quiz_name, section, batch_year, department, teacher_id, questions, timer, number_of_questions) '
                'VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING id',
                (self.quiz_name, self.section, self.batch_year, self.department, self.teacher_id, questions_json, self.timer, self.number_of_questions)
            )
            self.id = cursor.fetchone()[0]
            logger.info(f"Saved quiz with ID {self.id}")
        except Exception as e:
            logger.error(f"Error saving quiz: {str(e)}")
            raise

    @classmethod
    def get_by_section(cls, section):
        db = get_db()
        cursor = db.cursor()
        try:
            cursor.execute('SELECT * FROM quizzes WHERE section = %s', (section,))
            quizzes = cursor.fetchall()
            logger.debug(f"Retrieved {len(quizzes)} quizzes for section {section}")
            return [cls(
                id=quiz[0], quiz_name=quiz[1], section=quiz[2], batch_year=quiz[3],
                department=quiz[4], teacher_id=quiz[5], questions=quiz[6],
                timer=quiz[7], number_of_questions=quiz[8]
            ) for quiz in quizzes] if quizzes else []
        except Exception as e:
            logger.error(f"Error fetching quizzes by section {section}: {str(e)}")
            raise

    @classmethod
    def get_by_teacher(cls, teacher_id):
        db = get_db()
        cursor = db.cursor()
        try:
            cursor.execute('SELECT * FROM quizzes WHERE teacher_id = %s', (teacher_id,))
            quizzes = cursor.fetchall()
            logger.debug(f"Retrieved {len(quizzes)} quizzes for teacher {teacher_id}")
            return [
                {
                    "id": quiz[0], "quiz_name": quiz[1], "section": quiz[2], "batch_year": quiz[3],
                    "department": quiz[4], "teacher_id": quiz[5], "questions": quiz[6],
                    "timer": quiz[7], "number_of_questions": quiz[8]
                } for quiz in quizzes
            ] if quizzes else []
        except Exception as e:
            logger.error(f"Error fetching quizzes for teacher {teacher_id}: {str(e)}")
            raise

    @classmethod
    def get_by_name_and_teacher(cls, quiz_name, teacher_id):
        db = get_db()
        cursor = db.cursor()
        try:
            cursor.execute(
                'SELECT * FROM quizzes WHERE quiz_name = %s AND teacher_id = %s',
                (quiz_name, teacher_id)
            )
            quiz = cursor.fetchone()
            if quiz:
                logger.debug(f"Retrieved quiz {quiz_name} for teacher {teacher_id}")
                return cls(
                    id=quiz[0], quiz_name=quiz[1], section=quiz[2], batch_year=quiz[3],
                    department=quiz[4], teacher_id=quiz[5], questions=quiz[6],
                    timer=quiz[7], number_of_questions=quiz[8]
                )
            logger.debug(f"No quiz found with name {quiz_name} for teacher {teacher_id}")
            return None
        except Exception as e:
            logger.error(f"Error fetching quiz by name {quiz_name} and teacher {teacher_id}: {str(e)}")
            raise

    @classmethod
    def get_by_section_batch_and_department(cls, section, batch_year, department):
        start = time.time()
        db = get_db()
        cursor = db.cursor()
        print(f"[Trace] DB connect + cursor: {time.time() - start:.4f} sec")

        try:
            cursor.execute(
                'SELECT * FROM quizzes WHERE section = %s AND batch_year = %s AND department = %s',
                (section, batch_year, department)
            )
            quizzes = cursor.fetchall()
            logger.debug(f"Retrieved {len(quizzes)} quizzes for section {section}, batch {batch_year}, dept {department}")
            return [cls(
                id=quiz[0], quiz_name=quiz[1], section=quiz[2], batch_year=quiz[3],
                department=quiz[4], teacher_id=quiz[5], questions=quiz[6],
                timer=quiz[7], number_of_questions=quiz[8]
            ) for quiz in quizzes] if quizzes else []
        except Exception as e:
            logger.error(f"Error fetching quizzes for section {section}, batch {batch_year}, dept {department}: {str(e)}")
            raise

    @classmethod
    def get_by_name_and_id(cls, quiz_name, quiz_id):
        db = get_db()
        cursor = db.cursor()
        try:
            cursor.execute(
                'SELECT * FROM quizzes WHERE quiz_name = %s AND id = %s',
                (quiz_name, quiz_id)
            )
            quiz = cursor.fetchone()
            if quiz:
                logger.debug(f"Retrieved quiz {quiz_name} with ID {quiz_id}")
                return {
                    "id": quiz[0], "quiz_name": quiz[1], "section": quiz[2], "batch_year": quiz[3],
                    "department": quiz[4], "teacher_id": quiz[5], "questions": quiz[6],
                    "timer": quiz[7], "number_of_questions": quiz[8]
                }
            logger.debug(f"No quiz found with name {quiz_name} and ID {quiz_id}")
            return None
        except Exception as e:
            logger.error(f"Error fetching quiz by name {quiz_name} and ID {quiz_id}: {str(e)}")
            raise

class Score:
    def __init__(self, student_id, quiz_id, student_name, usn, score, section, department, submission_time, id=None):
        self.id = id
        self.student_id = student_id
        self.quiz_id = quiz_id
        self.student_name = student_name
        self.usn = usn
        self.score = score
        self.section = section
        self.department = department
        self.submission_time = submission_time

    def save(self):
        db = get_db()
        cursor = db.cursor()
        try:
            cursor.execute(
                'INSERT INTO scores (student_id, quiz_id, student_name, usn, score, section, department, submitted_at) VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING id',
                (self.student_id, self.quiz_id, self.student_name, self.usn, self.score, self.section, self.department, self.submission_time)
            )
            self.id = cursor.fetchone()[0]
            logger.info(f"Saved score with ID {self.id} for student {self.student_id}, quiz {self.quiz_id}")
        except Exception as e:
            logger.error(f"Error saving score for student {self.student_id}, quiz {self.quiz_id}: {str(e)}")
            raise

    @classmethod
    def get_by_student_and_quiz(cls, student_id, quiz_id):
        db = get_db()
        cursor = db.cursor()
        try:
            cursor.execute(
                'SELECT * FROM scores WHERE student_id = %s AND quiz_id = %s',
                (student_id, quiz_id)
            )
            score = cursor.fetchone()
            if score:
                logger.debug(f"Retrieved score for student {student_id}, quiz {quiz_id}")
                return {
                    "id": score[0], "student_id": score[1], "student_name": score[2], "quiz_id": score[3],
                    "score": score[4], "section": score[5], "department": score[6],
                    "submission_time": score[7].isoformat() if score[7] else None, "usn": score[8]
                }
            logger.debug(f"No score found for student {student_id}, quiz {quiz_id}")
            return None
        except Exception as e:
            logger.error(f"Error fetching score for student {student_id}, quiz {quiz_id}: {str(e)}")
            raise

    @classmethod
    def get_quizzes_by_student_id(cls, student_id):
        db = get_db()
        cursor = db.cursor()
        try:
            cursor.execute(
                'SELECT DISTINCT quiz_id FROM scores WHERE student_id = %s',
                (student_id,)
            )
            quizzes = cursor.fetchall()
            logger.debug(f"Retrieved {len(quizzes)} quiz IDs for student {student_id}")
            return [{"quiz_id": quiz[0]} for quiz in quizzes] if quizzes else []
        except Exception as e:
            logger.error(f"Error fetching quiz IDs for student {student_id}: {str(e)}")
            raise
        finally:
            cursor.close()

    @classmethod
    def get_scores_by_quiz(cls, quiz_id):
        db = get_db()
        cursor = db.cursor()
        try:
            cursor.execute(
                '''
                SELECT 
                    s.id, s.student_id, s.student_name, s.quiz_id, s.score, s.section, 
                    s.department, s.submitted_at, s.usn
                FROM scores s
                WHERE s.quiz_id = %s
                ORDER BY s.score DESC, s.submitted_at ASC
                ''',
                (quiz_id,)
            )
            scores = cursor.fetchall()
            logger.debug(f"Retrieved {len(scores)} scores for quiz {quiz_id}")
            return [
                {
                    "id": score[0], "student_id": score[1], "student_name": score[2], "quiz_id": score[3],
                    "score": score[4], "section": score[5], "department": score[6],
                    "submission_time": score[7].isoformat() if score[7] else None, "usn": score[8]
                } for score in scores
            ] if scores else []
        except Exception as e:
            logger.error(f"Error fetching scores for quiz {quiz_id}: {str(e)}")
            raise

class TabSwitchEvent:
    def __init__(self, quiz_id, student_id, student_name, usn, timestamp, id=None):
        self.id = id
        self.quiz_id = quiz_id
        self.student_id = student_id
        self.student_name = student_name
        self.usn = usn
        self.timestamp = timestamp

    def save(self):
        db = get_db()
        cursor = db.cursor()
        try:
            cursor.execute(
                '''INSERT INTO tab_switch_events 
                   (quiz_id, student_id, student_name, usn, timestamp) 
                   VALUES (%s, %s, %s, %s, %s) RETURNING id''',
                (self.quiz_id, self.student_id, self.student_name, self.usn, self.timestamp)
            )
            self.id = cursor.fetchone()[0]
            logger.info(f"Saved tab switch event with ID {self.id} for student {self.student_id}, quiz {self.quiz_id}")
        except Exception as e:
            logger.error(f"Error saving tab switch event: {str(e)}")
            raise

    @classmethod
    def get_by_quiz_id(cls, quiz_id):
        db = get_db()
        cursor = db.cursor()
        try:
            cursor.execute('SELECT * FROM tab_switch_events WHERE quiz_id = %s', (quiz_id,))
            events = cursor.fetchall()
            logger.debug(f"Retrieved {len(events)} tab switch events for quiz {quiz_id}")
            return [
                cls(id=event[0], quiz_id=event[1], student_id=event[2], student_name=event[3],
                    usn=event[4], timestamp=event[5]) for event in events
            ] if events else []
        except Exception as e:
            logger.error(f"Error fetching tab switch events for quiz {quiz_id}: {str(e)}")
            raise