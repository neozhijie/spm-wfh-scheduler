from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from config import Config


# Initialize SQLAlchemy
db = SQLAlchemy()

def create_app():
    # Initialize Flask app
    app = Flask(__name__)
    app.config.from_object(Config)

    # Configure CORS
    CORS(app, resources={r'/*': {'origins': '*'}}, supports_credentials=True)

    # Initialize extensions
    db.init_app(app)

    @app.route('/')
    def test():
        return "Welcome to the WFH Scheduler API."

    return app
