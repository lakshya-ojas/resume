from flask import Flask, request, jsonify, send_file
from werkzeug.utils import secure_filename
import os
import sqlite3
import subprocess

app = Flask(__name__)
#it will create the upload folder in where we will storing the resume
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///example.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

def create_connection():
    conn = sqlite3.connect('example.db')
    return conn

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'pdf', 'docx','txt'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))



        # Assuming 'main.py' is in the same directory as 'app.py'
        main_script = os.path.join(os.path.dirname(__file__), 'main.py')
        pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        output_directory = './output'  # Replace with desired output directory
        if not os.path.exists(output_directory):
            os.makedirs(output_directory)
        # Run main.py as a subprocess
        subprocess.Popen(['python', main_script, pdf_path, output_directory])




        return jsonify({'message': 'File uploaded successfully', 'filename': filename}), 200
    else:
        return jsonify({'error': 'File type not allowed'}), 400



@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    try:
        return send_file(os.path.join(app.config['UPLOAD_FOLDER'], filename), as_attachment=True)
    except FileNotFoundError:
        return jsonify({'error': 'File not found'}), 404

@app.route('/data', methods=['GET'])
def get_data():
    conn = create_connection()
    c = conn.cursor()
    c.execute('SELECT * FROM data')
    data = c.fetchall()
    conn.close()
    return jsonify(data)

if __name__ == '__main__':
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    app.run(debug=True)
    # app.run(debug=True, port=8080)

