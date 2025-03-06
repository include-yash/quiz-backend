import os
from flask import Flask
from routes.routes import init_routes
from db.db import init_app
from flask_cors import CORS  # Import CORS

# Initialize Flask app
app = Flask(__name__)

# Enable CORS for all routes, allowing requests from http://localhost:5173
CORS(app, resources={
    r"/*": {
        "origins": ["http://localhost:5173", "https://quiz-frontend-five-alpha.vercel.app"],
        "supports_credentials": True,
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization", "Access-Control-Allow-Credentials"]
    }
})


# Initialize database functions
init_app(app)

# Initialize routes
init_routes(app)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))  # Use PORT from Render or default to 10000
    app.run(host="0.0.0.0", port=port, debug=True)