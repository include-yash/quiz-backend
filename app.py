from flask import Flask
from routes.routes import init_routes
from db.db import init_app
from flask_cors import CORS  # Import CORS

# Initialize Flask app
app = Flask(__name__)

# Enable CORS for all routes, allowing requests from http://localhost:5173
CORS(app, resources={
    r"/*": {
        "origins": "http://localhost:5173",  # Frontend URL
        "supports_credentials": True,  # Allow sending cookies (if needed)
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],  # Allow all methods
        "allow_headers": ["Content-Type", "Authorization"]  # Allow necessary headers
    }
})

# Initialize database functions
init_app(app)

# Initialize routes
init_routes(app)

if __name__ == '__main__':
    app.run(debug=True)