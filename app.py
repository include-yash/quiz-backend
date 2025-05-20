import os
import time
from flask import Flask, g, request
from routes.routes import init_routes
from db.db import init_app
from flask_cors import CORS
from werkzeug.middleware.proxy_fix import ProxyFix
from flask import Flask, jsonify, request


# Initialize Flask app
app = Flask(__name__)

# Enhanced CORS configuration
CORS(
    app,
    supports_credentials=True,
    resources={
        r"/*": {
            "origins": [
                "http://localhost:5173",
                "https://quiz-frontend-git-main-include-yashs-projects.vercel.app",
                "https://quiz-frontend-five-alpha.vercel.app",
                "https://www.quizzer.site"
            ],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
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

# Track request start time
@app.before_request
def start_timer():
    g.start = time.time()


# Handle preflight requests and log response time
@app.after_request
def after_request(response):
    # CORS headers
    response.headers.add(
        'Access-Control-Allow-Origin', request.headers.get('Origin', '*'))
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    response.headers.add('Access-Control-Allow-Headers',
                         'Content-Type,Authorization,Access-Control-Allow-Credentials')
    response.headers.add('Access-Control-Allow-Methods',
                         'GET,PUT,POST,DELETE,OPTIONS')
    response.headers["Cross-Origin-Opener-Policy"] = "same-origin-allow-popups"

    # Log request time
    if hasattr(g, 'start'):
        duration = time.time() - g.start
        print(f"[{request.method}] {request.path} took {duration:.4f} seconds")

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
