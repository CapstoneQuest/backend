from flask import Blueprint, render_template

docs = Blueprint('main', __name__)

@docs.route('/')
def home():
    return render_template('index.html')
