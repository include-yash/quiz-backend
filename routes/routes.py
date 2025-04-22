from controllers.home_controller import home_page
from controllers.auth_controller import teacher_signup, student_signup, student_login, teacher_login, google_login, google_login_teacher
from controllers.test_controller import create_quiz
from controllers.teacher_controller import add_tab_switch_event, get_quizzes_by_teacher, get_tab_switch_events_by_quiz_id, release_quiz
from controllers.student_controller import get_quizzes_by_student_id, get_quizzes_for_logged_in_student, leaderboard, save_score, get_questions_by_quiz_id

def init_routes(app):
    app.add_url_rule('/', 'home', home_page)

    app.add_url_rule('/auth/google', 'google_login', google_login, methods=['POST'])
    app.add_url_rule('/auth/google/teacher', 'google_login_teacher', google_login_teacher, methods=['POST'])
    
    app.add_url_rule('/signup/teacher', 'teacher_signup', teacher_signup, methods=['POST'])
    app.add_url_rule('/signup/student', 'student_signup', student_signup, methods=['POST'])
    app.add_url_rule('/student-login', 'student_login', student_login, methods=['POST'])
    app.add_url_rule('/teacher-login', 'teacher_login', teacher_login, methods=['POST'])
    app.add_url_rule('/teacher/createquiz', 'quiz-creation', create_quiz, methods=['POST'])
    app.add_url_rule('/teacher/displayquiz', 'displayquiz', get_quizzes_by_teacher, methods=['GET'])
    app.add_url_rule('/teacher/release-quiz', 'release_quiz', release_quiz, methods=['POST'])
    app.add_url_rule('/student', 'displayquizstudent', get_quizzes_for_logged_in_student, methods=['GET'])
    app.add_url_rule('/student/savescore', 'save_score', save_score, methods=['POST'])
    app.add_url_rule('/student/get-quiz-id', 'getting_quiz_id_here', get_quizzes_by_student_id, methods=['GET'])
    app.add_url_rule('/student/leaderboard/<int:quiz_id>', 'getting_quiz_leaderboard', leaderboard, methods=['GET'])
    app.add_url_rule('/student/get-quiz-details', 'getting_quiz_details_here', get_questions_by_quiz_id, methods=['GET'])
    app.add_url_rule('/student/add-tab-switch', 'adding_tab_switch', add_tab_switch_event, methods=['POST'])
    app.add_url_rule('/teacher/tab-switch/<int:quiz_id>', 'getting_tab_switch', get_tab_switch_events_by_quiz_id, methods=['GET'])