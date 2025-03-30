from flask import request, jsonify
from flask import make_response
from models.models import Student, Teacher
from werkzeug.security import generate_password_hash, check_password_hash  # Import password hashing utilities
from itsdangerous.serializer import Serializer
from itsdangerous.exc import BadSignature, SignatureExpired
from utils.decode import generate_token,generate_token_student

# Helper function to handle student email parsing
def parse_student_email(email):
    try:
        # Split the email into the local part and domain part
        local_part, domain_part = email.split('@')
        
        # Extract the name (everything before the first dot)
        name = local_part.split('.')[0]
        
        # Extract the department (letters before the first number)
        department = ''.join([char for char in local_part.split('.')[1] if char.isalpha()])
        
        # Extract the batch year (numbers before the '@')
        batch_year = ''.join([char for char in local_part.split('.')[1] if char.isdigit()])
        
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
    print("data is",data)
    name, department, batch_year = parse_student_email(data['email']) 

    # Check if student already exists
    if Student.get_by_email(data['email']):
        return jsonify({"error": "Email already in use"}), 400

    student = Student(
        name=name,
        email=data['email'],
        section=data['section'],
        department=department,
        batch_year=batch_year,
        password=generate_password_hash(data['password'])  # Hash the password
    )

    student.save()  # Save the student to MongoDB
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
            'name': student.name,
            'email': student.email,
            'section': student.section,
            'department': student.department,
            'batch_year': student.batch_year
        }
        print("Student Details:", student_details)

        # Create response with token and student details
        response = make_response(jsonify({
            'message': 'Login successful',
            'token': token,
            'student_details': student_details  # Include student details
        }))
        
        # Set token in cookie for secure access
        response.set_cookie(
            'student_info',          # Cookie name
            token,                   # Cookie value
            httponly=True,           # Protect cookie from JavaScript access
            secure=False,            # Use True in production (HTTPS), False for local dev
            samesite='None',         # Allow cross-origin requests (for different ports)
            max_age=3600,            # Set expiration time (1 hour)
            domain='.localhost',  
               # Set domain to 'localhost' to allow sharing across different ports
        )
        
        return response, 200

    return jsonify({'error': 'Invalid email or password'}), 401

# Teacher Login function
def teacher_login():
    data = request.json  # Get login credentials
    teacher = Teacher.get_by_email(data['email']) 
    print("teacher details are",teacher) # Find teacher by email
    teacher_details={
        'id':teacher.id,
        'name':teacher.name,
        'email':teacher.email,
        'department':teacher.department
    }
    print(teacher)
    if teacher and check_password_hash(teacher.password, data['password']):  # Verify the password
        # Generate token
        token = generate_token(teacher)

        # Create response with token and cookie
        response = make_response(jsonify({
            'message': 'Login successful',
            'token': token,  # Include the token in the response body
            'teacher_details':teacher_details
        }))
        response.set_cookie(
            'teacher_info',
            token,
            httponly=True,  # Protect cookie from JavaScript access
            secure=True,    # Use HTTPS (set to False for local testing)
            samesite='Strict'  # Prevent cross-site requests
        )
        return response, 200

    return jsonify({'error': 'Invalid email or password'}), 401

