import os

from flask import Response, Blueprint, render_template, jsonify, abort

docs = Blueprint('main', __name__)
info = Blueprint('info', __name__)

@docs.route('/')
def home():
    return render_template('index.html')

@info.route('/about', methods=['GET'])
def get_about():
    return jsonify({
        'version': float(1.0),
        'homepage': 'http://127.0.0.1:5000', #todo: update URL
        'source_code': 'https://github.com/CapstoneQuest/backend'
    })

@info.route('/license', methods=['GET'])
def get_license():
   try:
        with open('LICENSE', 'r') as license_file:
           license_content = license_file.read()

        return Response(license_content, mimetype='text/plain')
   except:
        abort(404, description="License file not found.")

@info.route('/statuses', methods=['GET'])
def get_statuses():
    return jsonify([{'id': 0, 'description': 'Success'},
                    {'id': 1, 'description': 'Compilation Error'},
                    {'id': 2, 'description': 'Runtime Error'},
                    {'id': 3, 'description': 'Time Limit Exceeded'}])
