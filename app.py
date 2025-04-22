import os
from flask import Flask, request
from routes.routes import init_routes
from db.db import init_app
from flask_cors import CORS
from werkzeug.middleware.proxy_fix import ProxyFix

# Initialize Flask app
app = Flask(__name__)

# Enhanced CORS configuration
CORS(
    app,
    supports_credentials=True,
    resources={
        r"/*": {
            "origins": [  # Fixed typo from "origins" to "origins"
                "http://localhost:5173",
                "https://quiz-frontend-git-main-include-yashs-projects.vercel.app",
                "https://quiz-frontend-five-alpha.vercel.app",
                "https://www.quizzer.site"
            ],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],  # Fixed "OPTIONS" typo
            "allow_headers": [
                "Content-Type",
                "Authorization",
                "Access-Control-Allow-Credentials",
                "X-Requested-With"
            ],
            "expose_headers": [
                "Content-Disposition",
                "Access-Control-Allow-Origin"
            ],
            "max_age": 86400  # 24 hours
        }
    }
)

# Security headers middleware
@app.after_request
def set_security_headers(response):
    # Required for Google Auth to work
    response.headers['Cross-Origin-Opener-Policy'] = 'same-origin-allow-popups'
    response.headers['Cross-Origin-Embedder-Policy'] = 'unsafe-none'
    response.headers['Cross-Origin-Resource-Policy'] = 'cross-origin'
    
    # Dynamic CORS headers
    allowed_origins = [
        "http://localhost:5173",
        "https://quiz-frontend-git-main-include-yashs-projects.vercel.app",
        "https://quiz-frontend-five-alpha.vercel.app",
        "https://www.quizzer.site"
    ]
    
    origin = request.headers.get('Origin')
    if origin in allowed_origins:
        response.headers['Access-Control-Allow-Origin'] = origin
        response.headers['Access-Control-Allow-Credentials'] = 'true'
    
    return response

# Proxy configuration
app.wsgi_app = ProxyFix(app.wsgi_app, 
    x_for=1, x_proto=1, x_host=1, x_prefix=1)

# Initialize database and routes
init_app(app)
init_routes(app)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=True)
