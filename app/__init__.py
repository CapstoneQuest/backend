from flask import Flask

from app.routes import docs

def create_app():
    app = Flask(__name__)

    app.register_blueprint(docs)

    return app
