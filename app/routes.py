import os
import time
import subprocess

from flask import Response, Blueprint, render_template, jsonify, abort, request, current_app, send_file

from .services.gcc_compiler import compile_code

info = Blueprint('info', __name__)
process_code = Blueprint('process', __name__)
files = Blueprint('files', __name__)

@info.route('/')
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
    return jsonify([{'id': current_app.config['SUCCESS'], 'description': 'Success'},
                    {'id': current_app.config['COMPILATION_ERROR'], 'description': 'Compilation Error'},
                    {'id': current_app.config['RUNTIME_ERROR'], 'description': 'Runtime Error'},
                    {'id': current_app.config['TIME_LIMIT_EXCEEDED'], 'description': 'Time Limit Exceeded'}])

@process_code.route('/compile', methods=['POST'])
def compile_run():
    source_code = request.json.get('sourceCode')
    stdin = request.json.get('stdin')
    cpu_time_limit = request.json.get('cpu_time_limit', current_app.config['TIMEOUT_SECONDS'])

    response = {'stdout': None, 'stderr': None, 'exit_code': None, 'status': None, 'time': None}

    compilation_result = compile_code(source_code, 
                                      current_app.config['SOURCE_FILE'], 
                                      current_app.config['EXECUTABLE'],
                                      current_app.config['CXX'],
                                      current_app.config['DIALECT'])
    
    # If compilation fails
    if compilation_result.returncode != 0:
        response.update({'status': current_app.config['COMPILATION_ERROR'],
                         'exit_code': compilation_result.returncode,
                         'stderr': compilation_result.stderr})
    # Run executable
    else:
        run_command = './' + current_app.config['EXECUTABLE']
        try:
            start_time = time.time()
            execution_result = subprocess.run(run_command, 
                                              input=stdin, 
                                              capture_output=True, 
                                              text=True, 
                                              check=True, 
                                              timeout=cpu_time_limit)
            end_time = time.time()

            if execution_result.returncode == 0:
                response.update({'status': current_app.config['SUCCESS'],
                                 'exit_code': execution_result.returncode,
                                 'stdout': execution_result.stdout,
                                 'time': round((end_time - start_time) * 1000, 2)})
        except subprocess.TimeoutExpired:
            response.update({'status': current_app.config['TIME_LIMIT_EXCEEDED'],
                             'stderr': f"Execution exceeded {current_app.config['TIMEOUT_SECONDS']} seconds and was terminated."})
        except subprocess.CalledProcessError as e:
            response.update({'status': current_app.config['RUNTIME_ERROR'],
                             'stderr': e.stdout})
        finally:
            if os.path.exists(current_app.config['EXECUTABLE']):
                os.remove(current_app.config['EXECUTABLE'])

    return jsonify(response)

@files.route('/download', methods=['POST'])
def download_file():
    source_code = request.json.get('sourceCode')

    file_name = current_app.config['SOURCE_FILE']
    file_path = os.path.join(os.getcwd(), file_name)
    try:
        with open(file_path, 'w') as file:
            file.write(source_code)
            
        return send_file(file_path, as_attachment=True, download_name=file_name)
    finally:
        if os.path.exists(file_name):
            os.remove(file_name)
