from db.db import get_db
import json

class Student:
    def __init__(self, usn, name, email, section, department, batch_year, password, id=None):
        self.id = id 
        self.usn = usn  # USN is now a required field
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
            'INSERT INTO students (usn, name, email, section, department, batch_year, password) VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id',
            (self.usn, self.name, self.email, self.section, self.department, self.batch_year, self.password)
        )
        self.id = cursor.fetchone()[0]
        db.commit()

    @classmethod
    def get_by_email(cls, email):
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            'SELECT id, usn, name, email, section, department, batch_year, password FROM students WHERE email = %s', 
            (email,)
        )
        student = cursor.fetchone()
        
        if not student:
            return None
            
        # Verify we have all expected columns
        if len(student) < 8:
            raise ValueError("Invalid student data structure from database")
            
        return cls(
            id=student[0],
            usn=student[1],
            name=student[2],
            email=student[3],
            section=student[4],
            department=student[5],
            batch_year=student[6],
            password=student[7]
        )


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
            'INSERT INTO teachers (name, email, department, password) VALUES (%s, %s, %s, %s) RETURNING id',
            (self.name, self.email, self.department, self.password)
        )
        self.id = cursor.fetchone()[0]  # Retrieve the last inserted ID
        db.commit()

    @classmethod
    def get_by_email(cls, email):
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            'SELECT * FROM teachers WHERE email = %s', (email,)
        )
        teacher = cursor.fetchone()
        if teacher:
            return cls(
                id=teacher[0],
                name=teacher[1],
                email=teacher[2],
                department=teacher[3],
                password=teacher[4]
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
        # Convert questions to JSON string if it's a dictionary
        questions_json = json.dumps(self.questions) if isinstance(self.questions, dict) else self.questions
        cursor.execute(
            'INSERT INTO quizzes (quiz_name, section, batch_year, department, teacher_id, questions, timer) VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id',
            (self.quiz_name, self.section, self.batch_year, self.department, self.teacher_id, questions_json, self.timer)
        )
        self.id = cursor.fetchone()[0]  # Retrieve the last inserted ID
        db.commit()

    @classmethod
    def get_by_section(cls, section):
        """
        Retrieve quizzes from the database by section.
        """
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            'SELECT * FROM quizzes WHERE section = %s', (section,)
        )
        quizzes = cursor.fetchall()
        if quizzes:
            return [cls(
                id=quiz[0],
                quiz_name=quiz[1],
                section=quiz[2],
                batch_year=quiz[3],
                department=quiz[4],
                teacher_id=quiz[5],
                questions=quiz[6],  # Assuming questions are stored as JSON string
                timer=quiz[7]  # Deserialize the timer if needed
            ) for quiz in quizzes]
        return []

    @classmethod
    def get_by_teacher(cls, teacher_id):
        """
        Retrieve quizzes from the database by teacher_id.
        """
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            'SELECT * FROM quizzes WHERE teacher_id = %s', (teacher_id,)
        )
        quizzes = cursor.fetchall()
        if quizzes:
            return [
                {
                    "id": quiz[0],
                    "quiz_name": quiz[1],
                    "section": quiz[2],
                    "batch_year": quiz[3],
                    "department": quiz[4],
                    "teacher_id": quiz[5],
                    "questions": quiz[6],  # Assuming questions are stringified JSON
                    "timer": quiz[7]  # Adding timer here
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
        cursor = db.cursor()
        cursor.execute(
            'SELECT * FROM quizzes WHERE quiz_name = %s AND teacher_id = %s',
            (quiz_name, teacher_id)
        )
        quiz = cursor.fetchone()
        if quiz:
            return cls(
                id=quiz[0],
                quiz_name=quiz[1],
                section=quiz[2],
                batch_year=quiz[3],
                department=quiz[4],
                teacher_id=quiz[5],
                questions=quiz[6],  # Deserialize the JSON questions if needed
                timer=quiz[7]  # Return the timer value
            )
        return None

    @classmethod
    def get_by_section_batch_and_department(cls, section, batch_year, department):
        """
        Retrieve quizzes from the database by section, batch_year, and department.
        """
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            'SELECT * FROM quizzes WHERE section = %s AND batch_year = %s AND department = %s',
            (section, batch_year, department)
        )
        quizzes = cursor.fetchall()
        if quizzes:
            return [cls(
                id=quiz[0],
                quiz_name=quiz[1],
                section=quiz[2],
                batch_year=quiz[3],
                department=quiz[4],
                teacher_id=quiz[5],
                questions=quiz[6],  # Deserialize the JSON questions if needed
                timer=quiz[7]  # Include the timer
            ) for quiz in quizzes]
        return []
    
    @classmethod
    def get_by_name_and_id(cls, quiz_name, quiz_id):
        """
        Retrieve a quiz from the database by quiz_name and id.
        """
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            'SELECT * FROM quizzes WHERE quiz_name = %s AND id = %s',
            (quiz_name, quiz_id)
        )
        quiz = cursor.fetchone()
        if quiz:
            return {
                "id": quiz[0],
                "quiz_name": quiz[1],
                "section": quiz[2],
                "batch_year": quiz[3],
                "department": quiz[4],
                "teacher_id": quiz[5],
                "questions": quiz[6],  # Assuming questions are stored as JSON string
                "timer": quiz[7]  # Include the timer
            }
        return None


class Score:
    def __init__(self, student_id, quiz_id, student_name, usn, score, section, department, submission_time, id=None):
        self.id = id
        self.student_id = student_id
        self.quiz_id = quiz_id
        self.student_name = student_name
        self.usn = usn  # Add USN field
        self.score = score
        self.section = section
        self.department = department
        self.submission_time = submission_time

    def save(self):
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            'INSERT INTO scores (student_id, quiz_id, student_name, usn, score, section, department, submitted_at) VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING id',
            (self.student_id, self.quiz_id, self.student_name, self.usn, self.score, self.section, self.department, self.submission_time)
        )
        self.id = cursor.fetchone()[0]
        db.commit()

    @classmethod
    def get_by_student_and_quiz(cls, student_id, quiz_id):
        """
        Retrieve a score for a specific student and quiz as a dictionary.
        """
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            'SELECT * FROM scores WHERE student_id = %s AND quiz_id = %s',
            (student_id, quiz_id)
        )
        score = cursor.fetchone()
        if score:
            return {
                "id": score[0],
                "student_id": score[1],
                "student_name": score[2],
                "quiz_id": score[3],
                "score": score[4],
                "section": score[5],
                "department": score[6],
                "submission_time": score[7].isoformat() if score[7] else None,
                "usn": score[8]  # Add USN to the dictionary
            }
        return None

    @classmethod
    def get_quizzes_by_student_id(cls, student_id):
        """
        Retrieve unique quiz IDs attempted by a specific student as a list of dictionaries.
        """
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            'SELECT DISTINCT quiz_id FROM scores WHERE student_id = %s',
            (student_id,)
        )
        quizzes = cursor.fetchall()
        return [{"quiz_id": quiz[0]} for quiz in quizzes] if quizzes else []

    @classmethod
    def get_scores_by_quiz(cls, quiz_id):
        """
        Retrieve all scores for a specific quiz as a list of dictionaries, including USN.
        Ensure submission_time is properly formatted as ISO string.
        """
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            '''
            SELECT 
                s.id,
                s.student_id,
                s.student_name,
                s.quiz_id,
                s.score,
                s.section,
                s.department,
                s.submitted_at AT TIME ZONE 'UTC' AS submission_time,
                st.usn
            FROM scores s
            JOIN students st ON s.student_id = st.id
            WHERE s.quiz_id = %s
            ORDER BY s.score DESC, s.submission_time ASC
            ''',
            (quiz_id,)
        )
        scores = cursor.fetchall()
        
        return [
            {
                "id": score[0],
                "student_id": score[1],
                "student_name": score[2],
                "quiz_id": score[3],
                "score": score[4],
                "section": score[5],
                "department": score[6],
                "submission_time": score[7].isoformat() if score[7] else None,
                "usn": score[8]  # Add USN to the dictionary
            }
            for score in scores
        ] if scores else []
class TabSwitchEvent:
    def __init__(self, quiz_id, student_id, student_name, usn, timestamp, id=None):
        self.id = id
        self.quiz_id = quiz_id
        self.student_id = student_id
        self.student_name = student_name
        self.usn = usn
        self.timestamp = timestamp

    def save(self):
        try:
            db = get_db()
            cursor = db.cursor()
            cursor.execute(
                '''INSERT INTO tab_switch_events 
                   (quiz_id, student_id, student_name, usn, timestamp) 
                   VALUES (%s, %s, %s, %s, %s) RETURNING id''',
                (self.quiz_id, self.student_id, self.student_name, 
                 self.usn, self.timestamp)
            )
            self.id = cursor.fetchone()[0]
            db.commit()
        except Exception as e:
            db.rollback()
            raise

    @classmethod
    def get_by_quiz_id(cls, quiz_id):
        """
        Retrieve all tab switch events for a specific quiz_id.
        """
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            'SELECT * FROM tab_switch_events WHERE quiz_id = %s',
            (quiz_id,)
        )
        events = cursor.fetchall()
        if events:
            return [
                cls(
                    id=event[0],
                    quiz_id=event[1],
                    student_id=event[2],
                    student_name=event[3],
                    usn=event[4],
                    timestamp=event[5],
                )
                for event in events
            ]
        return []