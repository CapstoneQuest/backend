from app import create_app
from config import Config
from flask import g

app = create_app(Config)

@app.before_request
def before_request():
    g.variables_dict = {}

if __name__ == '__main__':
    app.run(debug=True)
    