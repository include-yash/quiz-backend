import time

from sqlalchemy import text
from db.db import get_db
import json
import logging
from db.db import get_db_engine

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
        engine = get_db_engine()
        try:
            with engine.connect() as conn:
                query = text(
                    'INSERT INTO students (usn, name, email, section, department, batch_year, password) '
                    'VALUES (:usn, :name, :email, :section, :department, :batch_year, :password) '
                    'RETURNING id'
                )
                result = conn.execute(query, {
                    'usn': self.usn,
                    'name': self.name,
                    'email': self.email,
                    'section': self.section,
                    'department': self.department,
                    'batch_year': self.batch_year,
                    'password': self.password
                })
                self.id = result.scalar_one()
                logger.info(f"✅ Saved student with ID {self.id}")
        except Exception as e:
            logger.error(f"❌ Error saving student: {str(e)}")
            raise

   
    @classmethod
    def get_by_email(cls, email):
        engine = get_db_engine()
        try:
            with engine.connect() as conn:
                query = text(
                    'SELECT id, usn, name, email, section, department, batch_year, password '
                    'FROM students WHERE email = :email'
                )
                result = conn.execute(query, {"email": email})
                student = result.fetchone()

                if not student:
                    logger.debug(f"No student found with email {email}")
                    return None

                if len(student) < 8:
                    raise ValueError("Invalid student data structure from database")

                logger.debug(f"Retrieved student with email {email}")
                return cls(
                    id=student.id,
                    usn=student.usn,
                    name=student.name,
                    email=student.email,
                    section=student.section,
                    department=student.department,
                    batch_year=student.batch_year,
                    password=student.password
                )
        except Exception as e:
            logger.error(f"Error fetching student by email {email}: {str(e)}", exc_info=True)
            raise

class Teacher:
    def __init__(self, name, email, department, password, id=None):
        self.id = id
        self.name = name
        self.email = email
        self.department = department
        self.password = password

    def save(self):
        engine = get_db_engine()
        try:
            with engine.connect() as conn:
                query = text(
                    'INSERT INTO teachers (name, email, department, password) '
                    'VALUES (:name, :email, :department, :password) '
                    'RETURNING id'
                )
                result = conn.execute(query, {
                    'name': self.name,
                    'email': self.email,
                    'department': self.department,
                    'password': self.password
                })
                self.id = result.scalar_one()
                logger.info(f"✅ Saved teacher with ID {self.id}")
        except Exception as e:
            logger.error(f"❌ Error saving teacher: {str(e)}")
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
        engine = get_db_engine()
        try:
            with engine.connect() as conn:
                questions_json = self.questions if isinstance(self.questions, str) else json.dumps(self.questions)

                query = text(
                    'INSERT INTO unreleasedTests (quiz_name, section, batch_year, department, teacher_id, questions, timer, number_of_questions) '
                    'VALUES (:quiz_name, :section, :batch_year, :department, :teacher_id, :questions, :timer, :number_of_questions) '
                    'RETURNING id'
                )
                result = conn.execute(query, {
                    'quiz_name': self.quiz_name,
                    'section': self.section,
                    'batch_year': self.batch_year,
                    'department': self.department,
                    'teacher_id': self.teacher_id,
                    'questions': questions_json,
                    'timer': self.timer,
                    'number_of_questions': self.number_of_questions
                })
                self.id = result.scalar_one()
                logger.info(f"✅ Saved unreleased quiz with ID {self.id}")
        except Exception as e:
            logger.error(f"❌ Error saving unreleased quiz: {str(e)}")
            raise

    @classmethod
    def get_by_teacher(cls, teacher_id):
        engine = get_db_engine()
        try:
            with engine.connect() as conn:
                query = text('SELECT * FROM unreleasedTests WHERE teacher_id = :teacher_id')
                result = conn.execute(query, {'teacher_id': teacher_id})
                quizzes = result.fetchall()

                logger.debug(f"📋 Retrieved {len(quizzes)} unreleased quizzes for teacher {teacher_id}")

                return [
                    {
                        "id": row.id,
                        "quiz_name": row.quiz_name,
                        "section": row.section,
                        "batch_year": row.batch_year,
                        "department": row.department,
                        "teacher_id": row.teacher_id,
                        "questions": row.questions,
                        "timer": row.timer,
                        "number_of_questions": row.number_of_questions
                    } for row in quizzes
                ] if quizzes else []
        except Exception as e:
            logger.error(f"❌ Error fetching unreleased quizzes for teacher {teacher_id}: {str(e)}")
            raise

    @classmethod
    def get_by_id(cls, quiz_id):
        engine = get_db_engine()
        try:
            with engine.connect() as conn:
                query = text('SELECT * FROM unreleasedTests WHERE id = :quiz_id')
                result = conn.execute(query, {'quiz_id': quiz_id})
                row = result.fetchone()

                if row:
                    logger.debug(f"📋 Retrieved unreleased quiz with ID {quiz_id}")
                    return {
                        "id": row.id,
                        "quiz_name": row.quiz_name,
                        "section": row.section,
                        "batch_year": row.batch_year,
                        "department": row.department,
                        "teacher_id": row.teacher_id,
                        "questions": row.questions,
                        "timer": row.timer,
                        "number_of_questions": row.number_of_questions
                    }

                logger.debug(f"⚠️ No unreleased quiz found with ID {quiz_id}")
                return None

        except Exception as e:
            logger.error(f"❌ Error fetching unreleased quiz by ID {quiz_id}: {str(e)}")
            raise

    @classmethod
    def delete_by_id(cls, quiz_id):
        engine = get_db_engine()
        try:
            with engine.connect() as conn:
                query = text('DELETE FROM unreleasedTests WHERE id = :quiz_id')
                conn.execute(query, {'quiz_id': quiz_id})
                logger.info(f"🗑️ Deleted unreleased quiz with ID {quiz_id}")
        except Exception as e:
            logger.error(f"❌ Error deleting unreleased quiz with ID {quiz_id}: {str(e)}")
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
        engine = get_db_engine()
        try:
            questions_json = self.questions if isinstance(self.questions, str) else json.dumps(self.questions)

            with engine.connect() as conn:
                query = text(
                    'INSERT INTO quizzes (quiz_name, section, batch_year, department, teacher_id, questions, timer, number_of_questions) '
                    'VALUES (:quiz_name, :section, :batch_year, :department, :teacher_id, :questions, :timer, :number_of_questions) '
                    'RETURNING id'
                )

                result = conn.execute(query, {
                    'quiz_name': self.quiz_name,
                    'section': self.section,
                    'batch_year': self.batch_year,
                    'department': self.department,
                    'teacher_id': self.teacher_id,
                    'questions': questions_json,
                    'timer': self.timer,
                    'number_of_questions': self.number_of_questions
                })

                self.id = result.scalar_one()
                logger.info(f"✅ Saved quiz with ID {self.id}")

        except Exception as e:
            logger.error(f"❌ Error saving quiz: {str(e)}")
            raise

    @classmethod
    def get_by_section(cls, section):
        engine = get_db_engine()
        try:
            with engine.connect() as conn:
                query = text('SELECT * FROM quizzes WHERE section = :section')
                result = conn.execute(query, {'section': section})
                quizzes = result.fetchall()

                logger.debug(f"📚 Retrieved {len(quizzes)} quizzes for section {section}")

                return [
                    cls(
                        id=row.id,
                        quiz_name=row.quiz_name,
                        section=row.section,
                        batch_year=row.batch_year,
                        department=row.department,
                        teacher_id=row.teacher_id,
                        questions=row.questions,
                        timer=row.timer,
                        number_of_questions=row.number_of_questions
                    )
                    for row in quizzes
                ] if quizzes else []

        except Exception as e:
            logger.error(f"❌ Error fetching quizzes by section {section}: {str(e)}")
            raise

    @classmethod
    def get_by_teacher(cls, teacher_id):
        engine = get_db_engine()
        try:
            with engine.connect() as conn:
                query = text('SELECT * FROM quizzes WHERE teacher_id = :teacher_id')
                result = conn.execute(query, {'teacher_id': teacher_id})
                quizzes = result.fetchall()

                logger.debug(f"📋 Retrieved {len(quizzes)} quizzes for teacher {teacher_id}")

                return [
                    {
                        "id": row.id,
                        "quiz_name": row.quiz_name,
                        "section": row.section,
                        "batch_year": row.batch_year,
                        "department": row.department,
                        "teacher_id": row.teacher_id,
                        "questions": row.questions,
                        "timer": row.timer,
                        "number_of_questions": row.number_of_questions
                    }
                    for row in quizzes
                ] if quizzes else []

        except Exception as e:
            logger.error(f"❌ Error fetching quizzes for teacher {teacher_id}: {str(e)}")
            raise

    @classmethod
    def get_by_name_and_teacher(cls, quiz_name, teacher_id):
        engine = get_db_engine()
        try:
            with engine.connect() as conn:
                query = text(
                    'SELECT * FROM quizzes WHERE quiz_name = :quiz_name AND teacher_id = :teacher_id'
                )
                result = conn.execute(query, {'quiz_name': quiz_name, 'teacher_id': teacher_id})
                quiz = result.fetchone()

                if quiz:
                    logger.debug(f"🎯 Retrieved quiz {quiz_name} for teacher {teacher_id}")
                    return cls(
                        id=quiz.id,
                        quiz_name=quiz.quiz_name,
                        section=quiz.section,
                        batch_year=quiz.batch_year,
                        department=quiz.department,
                        teacher_id=quiz.teacher_id,
                        questions=quiz.questions,
                        timer=quiz.timer,
                        number_of_questions=quiz.number_of_questions
                    )

                logger.debug(f"⚠️ No quiz found with name {quiz_name} for teacher {teacher_id}")
                return None

        except Exception as e:
            logger.error(f"❌ Error fetching quiz by name {quiz_name} and teacher {teacher_id}: {str(e)}")
            raise
    
    
    @classmethod
    def get_by_name_and_id(cls, quiz_name, quiz_id):
        engine = get_db_engine()
        try:
            with engine.connect() as conn:
                query = text('SELECT * FROM quizzes WHERE quiz_name = :quiz_name AND id = :quiz_id')
                result = conn.execute(query, {"quiz_name": quiz_name, "quiz_id": quiz_id})
                quiz = result.fetchone()
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

    @classmethod
    def get_by_section_batch_and_department(cls, section, batch_year, department):
        start = time.time()
        engine = get_db_engine()

        try:
            with engine.connect() as conn:
                logger.debug(f"[Trace] DB connect + cursor: {time.time() - start:.4f} sec")

                query = text(
                    "SELECT id, quiz_name, section, batch_year, department, teacher_id, questions, timer, number_of_questions "
                    "FROM quizzes WHERE section = :section AND batch_year = :batch_year AND department = :department"
                )
                result = conn.execute(query, {"section": section, "batch_year": batch_year, "department": department})
                quizzes = result.fetchall()

                logger.info(f"📋 Retrieved {len(quizzes)} quizzes in {time.time() - start:.4f}s for section={section}, batch={batch_year}, dept={department}")

                return [
                    cls(
                        id=row.id,
                        quiz_name=row.quiz_name,
                        section=row.section,
                        batch_year=row.batch_year,
                        department=row.department,
                        teacher_id=row.teacher_id,
                        questions=row.questions,
                        timer=row.timer,
                        number_of_questions=row.number_of_questions
                    ) for row in quizzes
                ] if quizzes else []

        except Exception as e:
            logger.error(f"Error fetching quizzes for section {section}, batch {batch_year}, dept {department}: {str(e)}")
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
        engine = get_db_engine()
        try:
            with engine.connect() as conn:
                query = text(
                    'INSERT INTO scores (student_id, quiz_id, student_name, usn, score, section, department, submitted_at) '
                    'VALUES (:student_id, :quiz_id, :student_name, :usn, :score, :section, :department, :submitted_at) RETURNING id'
                )
                result = conn.execute(query, {
                    'student_id': self.student_id,
                    'quiz_id': self.quiz_id,
                    'student_name': self.student_name,
                    'usn': self.usn,
                    'score': self.score,
                    'section': self.section,
                    'department': self.department,
                    'submitted_at': self.submission_time
                })
                self.id = result.fetchone()[0]
                logger.info(f"💾 Saved score with ID {self.id} for student {self.student_id}, quiz {self.quiz_id}")
        except Exception as e:
            logger.error(f"❌ Error saving score for student {self.student_id}, quiz {self.quiz_id}: {str(e)}")
            raise

    @classmethod
    def get_by_student_and_quiz(cls, student_id, quiz_id):
        engine = get_db_engine()
        try:
            with engine.connect() as conn:
                query = text(
                    'SELECT * FROM scores WHERE student_id = :student_id AND quiz_id = :quiz_id'
                )
                result = conn.execute(query, {'student_id': student_id, 'quiz_id': quiz_id})
                score = result.fetchone()
                if score:
                    logger.debug(f"🎯 Retrieved score for student {student_id}, quiz {quiz_id}")
                    return {
                        "id": score.id,
                        "student_id": score.student_id,
                        "student_name": score.student_name,
                        "quiz_id": score.quiz_id,
                        "score": score.score,
                        "section": score.section,
                        "department": score.department,
                        "submission_time": score.submitted_at.isoformat() if score.submitted_at else None,
                        "usn": score.usn
                    }
                logger.debug(f"⚠️ No score found for student {student_id}, quiz {quiz_id}")
                return None
        except Exception as e:
            logger.error(f"❌ Error fetching score for student {student_id}, quiz {quiz_id}: {str(e)}")
            raise

    @classmethod
    def get_quizzes_by_student_id(cls, student_id):
        engine = get_db_engine()
        try:
            with engine.connect() as conn:
                query = text('SELECT DISTINCT quiz_id FROM scores WHERE student_id = :student_id')
                result = conn.execute(query, {"student_id": student_id})
                quizzes = result.fetchall()
                logger.debug(f"🎯 Retrieved {len(quizzes)} quiz IDs for student {student_id}")
                return [{"quiz_id": quiz.quiz_id} for quiz in quizzes] if quizzes else []
        except Exception as e:
            logger.error(f"❌ Error fetching quiz IDs for student {student_id}: {str(e)}")
            raise

    @classmethod
    def get_scores_by_quiz(cls, quiz_id):
        engine = get_db_engine()
        try:
            with engine.connect() as conn:
                query = text('''
                    SELECT 
                        s.id, s.student_id, s.student_name, s.quiz_id, s.score, s.section, 
                        s.department, s.submitted_at, s.usn
                    FROM scores s
                    WHERE s.quiz_id = :quiz_id
                    ORDER BY s.score DESC, s.submitted_at ASC
                ''')
                result = conn.execute(query, {"quiz_id": quiz_id})
                scores = result.fetchall()
                
                logger.debug(f"🎯 Retrieved {len(scores)} scores for quiz {quiz_id}")
                
                return [
                    {
                        "id": row.id,
                        "student_id": row.student_id,
                        "student_name": row.student_name,
                        "quiz_id": row.quiz_id,
                        "score": row.score,
                        "section": row.section,
                        "department": row.department,
                        "submission_time": row.submitted_at.isoformat() if row.submitted_at else None,
                        "usn": row.usn
                    }
                    for row in scores
                ] if scores else []
        except Exception as e:
            logger.error(f"❌ Error fetching scores for quiz {quiz_id}: {str(e)}")
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
        engine = get_db_engine()
        try:
            with engine.connect() as conn:
                query = text('''
                    INSERT INTO tab_switch_events 
                        (quiz_id, student_id, student_name, usn, timestamp) 
                    VALUES (:quiz_id, :student_id, :student_name, :usn, :timestamp)
                    RETURNING id
                ''')
                result = conn.execute(query, {
                    "quiz_id": self.quiz_id,
                    "student_id": self.student_id,
                    "student_name": self.student_name,
                    "usn": self.usn,
                    "timestamp": self.timestamp
                })
                self.id = result.fetchone()[0]
                logger.info(f"Saved tab switch event with ID {self.id} for student {self.student_id}, quiz {self.quiz_id}")
        except Exception as e:
            logger.error(f"Error saving tab switch event: {str(e)}")
            raise
    
    @classmethod
    def get_by_quiz_id(cls, quiz_id):
        engine = get_db_engine()
        try:
            with engine.connect() as conn:
                query = text('SELECT * FROM tab_switch_events WHERE quiz_id = :quiz_id')
                result = conn.execute(query, {"quiz_id": quiz_id})
                events = result.fetchall()
                logger.debug(f"Retrieved {len(events)} tab switch events for quiz {quiz_id}")
                return [
                    cls(id=event[0], quiz_id=event[1], student_id=event[2], student_name=event[3],
                        usn=event[4], timestamp=event[5])
                    for event in events
                ] if events else []
        except Exception as e:
            logger.error(f"Error fetching tab switch events for quiz {quiz_id}: {str(e)}")
            raise