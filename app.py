import os
from flask import Flask, request
from routes.routes import init_routes
from db.db import init_app
from flask_cors import CORS
from werkzeug.middleware.proxy_fix import ProxyFix  # Handle proxy issues

# Initialize Flask app
app = Flask(__name__)

# Enable CORS for all routes, allowing requests from frontend URLs
CORS(app, supports_credentials=True)

# Ensure Flask trusts proxies (important for Render, Vercel, etc.)
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

# Manually add CORS headers to every response
@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = request.headers.get("Origin", "*")
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization, Access-Control-Allow-Credentials"
    response.headers["Access-Control-Allow-Credentials"] = "true"
    return response

# Initialize database functions
init_app(app)

# Initialize routes
init_routes(app)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))  # Use PORT from Render or default to 10000
    app.run(host="0.0.0.0", port=port, debug=True)
