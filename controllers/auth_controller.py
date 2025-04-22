import os
from flask import request, jsonify
from flask import make_response
from models.models import Student, Teacher
from werkzeug.security import generate_password_hash, check_password_hash  # Import password hashing utilities
from itsdangerous.serializer import Serializer
from itsdangerous.exc import BadSignature, SignatureExpired
from utils.decode import generate_token,generate_token_student
import google.auth
from google.auth.transport.requests import Request
from google.oauth2 import id_token
from dotenv import load_dotenv
load_dotenv()

def google_login():
    data = request.json  # Get the token from the frontend
    token = data.get('token')

    if not token:
        return jsonify({'error': 'Token is required'}), 400

    try:
        # Verify the Google token
        CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID")  # Replace with your actual Google Client ID
        idinfo = id_token.verify_oauth2_token(token, Request(), CLIENT_ID)

        # Extract the user's email from the token
        email = idinfo['email']

        # Check if student exists in the database
        student = Student.get_by_email(email)

        if student:
            # Student exists, return the token and student details
            student_details = {
                'id': student.id,
                'usn': student.usn,
                'name': student.name,
                'email': student.email,
                'section': student.section,
                'department': student.department,
                'batch_year': student.batch_year,
            }
            # Generate JWT for the student
            token = generate_token_student(student)

            return jsonify({
                'message': 'Login successful',
                'token': token,
                'student_details': student_details
            }), 200
        else:
            # Student does not exist, return a flag to frontend
            return jsonify({
                'new_user': True,
                'email': email
            }), 200

    except google.auth.exceptions.GoogleAuthError as e:
        return jsonify({'error': 'Invalid Google token', 'message': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Something went wrong', 'message': str(e)}), 500
    
def google_login_teacher():
    data = request.json
    token = data.get('token')

    if not token:
        return jsonify({'error': 'Token is required'}), 400

    try:
        CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID")
        idinfo = id_token.verify_oauth2_token(token, Request(), CLIENT_ID)

        email = idinfo['email']

        teacher = Teacher.get_by_email(email)
        if teacher:
            teacher_details = {
                'id': teacher.id,
                'name': teacher.name,
                'email': teacher.email,
                'department': teacher.department
            }

            token = generate_token(teacher)

            return jsonify({
                'message': 'Login successful',
                'token': token,
                'teacher_details': teacher_details
            }), 200
        else:
            return jsonify({
                'new_user': True,
                'email': email
            }), 200

    except ValueError:
        return jsonify({'error': 'Invalid Google token'}), 400
    except Exception as e:
        return jsonify({'error': 'Something went wrong', 'message': str(e)}), 500
# Helper function to handle student email parsing
def parse_student_email(email, isDiploma):
    try:
        # Split the email into the local part and domain part
        local_part, domain_part = email.split('@')
        
        # Extract the name (everything before the first dot)
        name = local_part.split('.')[0]
        
        # Extract the department (letters before the first number)
        department = ''.join([char for char in local_part.split('.')[1] if char.isalpha()])
        
        # Extract the batch year (numbers before the '@')
        batch_year = ''.join([char for char in local_part.split('.')[1] if char.isdigit()])
        batch_year = str(int(batch_year) - 1) if isDiploma else batch_year
        return name, department, batch_year
    except (ValueError, IndexError):
        return None, None, None


# Helper function to handle teacher email parsing
def parse_teacher_email(email):
    try:
        # Split the email into the local part and domain part
        local_part, domain_part = email.split('@')

        # Extract the username (everything before the '@')
        username,department = local_part.split('.')

        # Extract the department (the first part of the domain before '.')
        
        return username, department
    except (ValueError, IndexError):
        return None, None




# Student Sign-up function
def student_signup():
    data = request.json  # Get data from the frontend
    print("data is", data)
    name, department, batch_year = parse_student_email(data['email'],data["isDiploma"]) 

    # Check if student already exists
    if Student.get_by_email(data['email']):
        return jsonify({"error": "Email already in use"}), 400

    # Validate USN is provided
    if not data.get('usn'):
        return jsonify({"error": "USN is required"}), 400

    student = Student(
        usn=data['usn'],  # USN from frontend
        name=name,
        email=data['email'],
        section=data['section'],
        department=department,
        batch_year=batch_year,
        password=generate_password_hash(data['password'])
    )

    student.save()  
    return jsonify({"message": "Student signed up successfully"}), 201

# Teacher Sign-up function
def teacher_signup():
    data = request.json  # Get data from the frontend
    name, department = parse_teacher_email(data['email'])  # Parse teacher email

    if not name or not department:
        return jsonify({'error': 'Invalid email format for teacher'}), 400

    # Check if teacher already exists
    if Teacher.get_by_email(data['email']):
        return jsonify({'error': 'Email already in use'}), 400

    # Hash the password before storing it
    hashed_password = generate_password_hash(data['password'])

    teacher = Teacher(
        name=name,
        email=data['email'],
        department=department,
        password=hashed_password  # Store the hashed password
    )

    teacher.save()  # Save the teacher to MongoDB
    return jsonify({'message': 'Teacher signed up successfully'}), 201


# Student Login function
def student_login():
    data = request.json  # Get login credentials
    student = Student.get_by_email(data['email'])  # Find student by email
    
    if student and check_password_hash(student.password, data['password']):
        
        # Generate the token
        token = generate_token_student(student)
        
        # Prepare student details to return in the response
        student_details = {
            'id': student.id,
            'usn': student.usn,  # Include USN in the details
            'name': student.name,
            'email': student.email,
            'section': student.section,
            'department': student.department,
            'batch_year': student.batch_year,
        }
        print("Student Details:", student_details)

        # Create response with token and student details
        response = make_response(jsonify({
            'message': 'Login successful',
            'token': token,
            'student_details': student_details  # Include student details with USN
        }))
        
        # Set token in cookie for secure access
        response.set_cookie(
            'student_info',          # Cookie name
            token,                   # Cookie value
            httponly=True,           # Protect cookie from JavaScript access
            secure=False,            # Use True in production (HTTPS), False for local dev
            samesite='Lax',         # Allow cross-origin requests (for different ports)
            max_age=3600,            # Set expiration time (1 hour)
            # domain='.localhost',
              
        )
        
        return response, 200

    return jsonify({'error': 'Invalid email or password'}), 401

# Teacher Login function
def teacher_login():
    data = request.json  # Get login credentials
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'error': 'Email and password are required'}), 400

    teacher = Teacher.get_by_email(email)

    if teacher and check_password_hash(teacher.password, password):  # ✅ Only proceed if teacher exists and password matches
        teacher_details = {
            'id': teacher.id,
            'name': teacher.name,
            'email': teacher.email,
            'department': teacher.department
        }

        # Generate token
        token = generate_token(teacher)

        # Create response with token and cookie
        response = make_response(jsonify({
            'message': 'Login successful',
            'token': token,
            'teacher_details': teacher_details
        }))
        response.set_cookie(
            'teacher_info',
            token,
            httponly=True,
            secure=False,       # Use False for local testing if needed
            samesite='Strict'  # Prevent CSRF
        )
        return response, 200

    # ❗ Either the teacher doesn't exist or password is wrong
    return jsonify({'error': 'Invalid email or password'}), 401

