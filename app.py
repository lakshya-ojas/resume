from flask import Flask, request, jsonify, send_file
from werkzeug.utils import secure_filename
import os
from DB.db import insert_data, search_text
from main import convert_file_to_text  # Assuming convert_file_to_text function is defined in main.py
from flask_cors import CORS
# Install Flask with 'async' extra: pip install Flask[async]

app = Flask(__name__)
CORS(app)

# Configure upload folder
app.config['UPLOAD_FOLDER'] = 'uploads'

# Configure SQLAlchemy database URI (not used in the current routes)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///example.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Function to check allowed file types
def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'pdf', 'docx', 'txt','doc'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Route for file upload
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
        print("File uploaded successfully to the upload folder")

        pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        output_directory = './output'  # Replace with desired output directory
        if not os.path.exists(output_directory):
            os.makedirs(output_directory)

        # Example function call assuming convert_file_to_text returns text, summarized_text, entities
        text, summarized_text, entities = convert_file_to_text(pdf_path, output_directory)

        # Insert summarized text into MongoDB asynchronously
        insert_data(summarized_text)
        print("Data inserted into the MongoDB database")

        return jsonify({'message': 'File uploaded successfully', 'filename': filename}), 200
    else:
        return jsonify({'error': 'File type not allowed'}), 400


# Route for searching text in MongoDB
@app.route('/search', methods=['GET', 'POST'])
async def search_text_in_mongodb_lakshya():
    try:
        if request.method == 'POST':
            # Example: Get query from JSON body
            data = request.get_json()
            query = data.get('query')
            # query = "hello"
            print(query)
            if not query:
                return jsonify({'error': 'Missing query parameter'}), 400

            # Perform search in MongoDB asynchronously
            results = await search_text(query)


            if results is None:
                return jsonify({'message': 'An error occurred during search'}), 500
            
            # Convert ObjectId to string for JSON serialization
            for result in results:
                result['_id'] = str(result['_id'])  # Convert ObjectId to string


            return jsonify(results), 200

        elif request.method == 'GET':
            return jsonify({'message': 'Send a POST request with JSON body {`query`: `search text`}'}), 200

    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    app.run(debug=True)
