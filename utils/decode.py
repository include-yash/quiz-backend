from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature

SECRET_KEY = "123455"  # Replace this with a strong secret key
serializer = URLSafeTimedSerializer(SECRET_KEY)

def generate_token(teacher):
    """
    Generate a secure token containing teacher information.
    """
    return serializer.dumps(
        {
            'id': teacher.id,
            'name': teacher.name,
            'department': teacher.department
        }
    )

def decode_token(token):
    """
    Decode the secure token to extract teacher information.
    """
    try:
        data = serializer.loads(token, max_age=36000)  # Token expires in 1 hour
        return data
    except SignatureExpired:
        return None  # Token has expired
    except BadSignature:
        return None  # Token is invalid

def generate_token_student(student):
    """
    Generate a secure token containing student information.
    """
    return serializer.dumps(
        {
            'id': student.id,
            'name': student.name,
            'department': student.department,
            'section': student.section,
            'batch_year': student.batch_year
        }
    )

def decode_token_student(token):
    """
    Decode the secure token to extract student information.
    """
    try:
        data = serializer.loads(token, max_age=36000)  # Token expires in 10 hours
        return data
    except SignatureExpired:
        return None  # Token has expired
    except BadSignature:
        return None  # Token is invalid