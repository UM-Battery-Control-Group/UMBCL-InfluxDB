from flask import Flask
from .config import DevelopmentConfig
from src.routes import raw_blueprint

def create_app(config=DevelopmentConfig):
    app = Flask(__name__)
    app.config.from_object(config)
    app.register_blueprint(raw_blueprint, url_prefix='/raw')

    return app

