CREATE TABLE IF NOT EXISTS students (
    id SERIAL PRIMARY KEY,
    usn TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    section TEXT NOT NULL,
    department TEXT NOT NULL,
    batch_year TEXT NOT NULL,
    password TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS teachers (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    department TEXT NOT NULL,
    password TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS unreleasedTests (
    id SERIAL PRIMARY KEY,
    quiz_name TEXT NOT NULL,
    section TEXT NOT NULL,
    batch_year TEXT NOT NULL,
    department TEXT NOT NULL,
    teacher_id INTEGER NOT NULL,
    questions JSONB NOT NULL,
    timer INTEGER NOT NULL,
    number_of_questions INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (teacher_id) REFERENCES teachers(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS quizzes (
    id SERIAL PRIMARY KEY,
    quiz_name TEXT NOT NULL,
    section TEXT NOT NULL,
    batch_year TEXT NOT NULL,
    department TEXT NOT NULL,
    teacher_id INTEGER NOT NULL,
    questions JSONB NOT NULL,
    timer INTEGER NOT NULL,
    number_of_questions INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (teacher_id) REFERENCES teachers(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS scores (
    id SERIAL PRIMARY KEY,
    student_name TEXT NOT NULL,
    student_id INTEGER NOT NULL,
    quiz_id INTEGER NOT NULL,
    usn TEXT NOT NULL,
    score INTEGER NOT NULL,
    section TEXT NOT NULL,
    department TEXT NOT NULL,
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(student_id) REFERENCES students(id) ON DELETE CASCADE,
    FOREIGN KEY(quiz_id) REFERENCES quizzes(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS quiz_attempts (
    quiz_id INTEGER NOT NULL,
    student_id INTEGER NOT NULL,
    attempted BOOLEAN NOT NULL DEFAULT FALSE,
    PRIMARY KEY (quiz_id, student_id),
    FOREIGN KEY (quiz_id) REFERENCES quizzes(id) ON DELETE CASCADE,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS tab_switch_events (
    id SERIAL PRIMARY KEY,
    quiz_id INTEGER NOT NULL,
    student_id INTEGER NOT NULL,
    student_name TEXT,
    usn TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_quiz FOREIGN KEY (quiz_id) REFERENCES quizzes(id),
    CONSTRAINT fk_student FOREIGN KEY (student_id) REFERENCES students(id)
);