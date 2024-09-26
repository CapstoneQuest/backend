from flask import Flask
from config import Config

from app.routes import docs, info, process_code

def create_app(config_class = Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    app.register_blueprint(docs)
    app.register_blueprint(info)
    app.register_blueprint(process_code)

    return app
