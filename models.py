"""Models for Flask-Feedback App."""
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def connect_db(app):
    """Connect this database to the provided Flask App."""
    db.app = app
    db.init_app(app)
