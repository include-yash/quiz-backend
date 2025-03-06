from controllers.home_controller import home_page
from controllers.auth_controller import teacher_login, student_login, teacher_signup, student_signup
from controllers.test_controller import create_quiz
from controllers.teacher_controller import add_tab_switch_event, get_quizzes_by_teacher, get_tab_switch_events_by_quiz_id
from controllers.student_controller import get_quizzes_by_student_id, get_quizzes_for_logged_in_student, leaderboard,save_score
from controllers.student_controller import get_questions_by_quiz_id
def init_routes(app):
    # Home route
    app.add_url_rule('/', 'home', home_page)
    
    # Teacher and Student login routes
    app.add_url_rule('/teacher-login', 'teacher_login', teacher_login, methods=['POST'])
    app.add_url_rule('/student-login', 'student_login', student_login, methods=['POST'])
    
    app.add_url_rule('/signup/teacher', 'teacher_signup', teacher_signup, methods=['POST'])
    app.add_url_rule('/signup/student', 'student_signup', student_signup, methods=['POST'])
    app.add_url_rule('/teacher/createquiz', 'quiz-creation', create_quiz, methods=['POST'])
    app.add_url_rule('/teacher/displayquiz', 'displayquiz', get_quizzes_by_teacher, methods=['GET'])
    app.add_url_rule('/student', 'displayquizstudent', get_quizzes_for_logged_in_student, methods=['GET'])
    app.add_url_rule('/student/savescore', 'save score', save_score, methods=['POST'])
    app.add_url_rule('/student/get-quiz-id', 'getting quiz id here',get_quizzes_by_student_id , methods=['GET'])
    app.add_url_rule('/student/leaderboard/<int:quiz_id>', 'getting quiz leaderboard',leaderboard , methods=['GET'])
    app.add_url_rule('/student/get-quiz-details', 'getting quiz details here', get_questions_by_quiz_id, methods=['GET'])
    app.add_url_rule('/student/add-tab-switch', 'adding tab switch', add_tab_switch_event, methods=['POST'])
    app.add_url_rule('/teacher/tab-switch/<int:quiz_id>', 'getting tab switch', get_tab_switch_events_by_quiz_id , methods=['GET'])


