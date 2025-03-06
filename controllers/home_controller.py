from flask import render_template

# Home page route
def home_page():
    return '''
    <html>
        <body>
            <h1>Welcome to the Quiz App</h1>
            <p>Please choose your role:</p>
            <button onclick="window.location.href='/teacher-login'">Teacher</button>
            <button onclick="window.location.href='/student-login'">Student</button>
        </body>
    </html>
    '''
