import os

from flask import Flask

from routes.file_routes import file_routes
from routes.dashboard_routes import dashboard_routes
from routes.auth_routes import auth_routes
from routes.transfer_routes import transfer_routes

from database.database import initialize_database


# ==========================================
# FLASK APPLICATION
# ==========================================

app = Flask(__name__)


# ==========================================
# SECRET KEY
# ==========================================

app.secret_key = os.environ.get(
    "SECRET_KEY",
    "dev-secret-key-change-this"
)


# ==========================================
# SESSION SECURITY
# ==========================================

app.config["SESSION_COOKIE_HTTPONLY"] = True

app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

# False for local HTTP development.
# Change to True when deployed with HTTPS.

app.config["SESSION_COOKIE_SECURE"] = true


# ==========================================
# FILE UPLOAD LIMIT
# ==========================================

app.config["MAX_CONTENT_LENGTH"] = (
    50 * 1024 * 1024
)


# ==========================================
# DATABASE
# ==========================================

initialize_database()


# ==========================================
# BLUEPRINTS
# ==========================================

app.register_blueprint(
    auth_routes
)

app.register_blueprint(
    file_routes
)

app.register_blueprint(
    dashboard_routes
)

app.register_blueprint(
    transfer_routes
)


# ==========================================
# RUN APPLICATION
# ==========================================

if __name__ == "__main__":

    app.run(
        debug=True
    )