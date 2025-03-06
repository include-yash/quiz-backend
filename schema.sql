CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    section TEXT NOT NULL,
    department TEXT NOT NULL,
    batch_year TEXT NOT NULL,
    password TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS teachers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    department TEXT NOT NULL,
    password TEXT NOT NULL
);

-- Create the quiz table
CREATE TABLE IF NOT EXISTS quizzes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,  -- Auto-incrementing ID for each quiz
    quiz_name TEXT NOT NULL,                -- Name of the quiz
    section TEXT NOT NULL, 
    batch_year TEXT NOT NULL,
    department TEXT NOT NULL,               -- Department for which the quiz is intended
    teacher_id INTEGER NOT NULL,            -- ID of the teacher who created the quiz (Foreign Key)
    questions TEXT NOT NULL,                -- Stringified JSON of quiz questions
    timer INTEGER NOT NULL,                 -- Timer for the quiz (in minutes, for example)
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,  -- Timestamp when the quiz was created
    FOREIGN KEY (teacher_id) REFERENCES teachers(id)  -- Foreign key relationship to the teachers table
);

CREATE TABLE IF NOT EXISTS scores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_name TEXT NOT NULL,
    student_id INTEGER NOT NULL,
    quiz_id INTEGER NOT NULL,
    score INTEGER NOT NULL,
    section TEXT NOT NULL,
    department TEXT NOT NULL,
    submitted_at DATETIME DEFAULT CURRENT_TIMESTAMP, -- New column to store the submission time
    FOREIGN KEY(student_id) REFERENCES students(id),
    FOREIGN KEY(quiz_id) REFERENCES quizzes(id)
);


CREATE TABLE QuizAttempts (
    quiz_id INTEGER NOT NULL,
    student_id INTEGER NOT NULL,
    attempted BOOLEAN NOT NULL DEFAULT 0,
    PRIMARY KEY (quiz_id, student_id)
);


