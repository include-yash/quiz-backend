import os
from flask import Flask, request
from routes.routes import init_routes
from db.db import init_app
from flask_cors import CORS
from werkzeug.middleware.proxy_fix import ProxyFix  # Handle proxy issues

# Initialize Flask app
app = Flask(__name__)

# Enable CORS for all routes, allowing requests from frontend URLs
CORS(
    app,
    supports_credentials=True,
    origins=["http://localhost:5173", "https://quiz-frontend-git-main-include-yashs-projects.vercel.app", "https://quiz-frontend-five-alpha.vercel.app/"],  # Allow requests from your frontend
    methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],  # Allow these HTTP methods
    allow_headers=["Content-Type", "Authorization", "Access-Control-Allow-Credentials"],  # Allow these headers
)

# Ensure Flask trusts proxies (important for Render, Vercel, etc.)
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

# Initialize database functions
init_app(app)

# Initialize routes
init_routes(app)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))  # Use PORT from Render or default to 10000
    app.run(host="0.0.0.0", port=port, debug=True)