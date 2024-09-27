from flask import Flask
from config import Config

from app.routes import info, process_code, files

def create_app(config_class = Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    app.register_blueprint(info)
    app.register_blueprint(process_code)
    app.register_blueprint(files)

    return app
