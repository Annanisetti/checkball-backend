from flask import Flask
from app.extensions import db
from app.config import Config
from app.routes import main as main_blueprint


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)

    # Register blueprints
    app.register_blueprint(main_blueprint)

    return app
