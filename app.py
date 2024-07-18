from flask import Flask, request, jsonify, send_file, session, render_template
from werkzeug.utils import secure_filename
import os
from DB.db import insert_data, search_text, find_document
import uuid
from main import convert_file_to_text  # Assuming convert_file_to_text function is defined in main.py
from flask_cors import CORS
import uuid
from summarize_chatgpt import find_question_response
from flask_session import Session
# Install Flask with 'async' extra: pip install Flask[async]
#langChani

from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.llms import OpenAI
from langchain.chains.question_answering import load_qa_chain

# Set your OpenAI API key
os.environ['OPENAI_API_KEY'] = "sk-proj-0RYtolmsFYdFaJOVOAkET3BlbkFJHjVxlk4gERS8rwYg1urF"

chain = load_qa_chain(OpenAI(), chain_type="stuff")
embedding = OpenAIEmbeddings()

app = Flask(__name__)
CORS(app)

# Configure upload folder
app.config['UPLOAD_FOLDER'] = 'uploads'
# Configure secret key for session management
app.secret_key = 'your_secret_key_here'

# Function to check allowed file types
def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'pdf', 'docx', 'txt','doc'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def text_splitter():
    return CharacterTextSplitter(separator='\n', chunk_size=1000, chunk_overlap=200, length_function=len)


# Route for file upload
@app.route("/")
def index():
    return render_template('index.html')

@app.route("/abcd", methods=['GET'])
def text_pur():
    return "hello how are you"

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(pdf_path)
        print("File uploaded successfully to the upload folder")

        output_directory = './output'  # Replace with desired output directory
        if not os.path.exists(output_directory):
            os.makedirs(output_directory)

        # Example function call assuming convert_file_to_text returns text, summarized_text, entities
        Original_text, summarized_text, entities = convert_file_to_text(pdf_path, output_directory)

        preprocessed_text = Original_text.replace('\n\n', '\n').replace('---', '\n')

        #spliting the text into the chunks
        texts = text_splitter().split_text(preprocessed_text)

        # Insert summarized text into MongoDB asynchronously
        # global docsearch
        # docsearch = FAISS.from_texts(texts, embedding)
        # print("storing the vector in the docsearch")
        # print(docsearch)

        user_id = str(uuid.uuid4())

        document_id = insert_data(Original_text,preprocessed_text,pdf_path,user_id,texts)
        print("Data inserted into the MongoDB database")
        
        # docsearch = FAISS.from_texts(texts, embedding) 
        # docsearch.save_local("faiss_index")

        session['user_id'] = user_id

        return jsonify({'message': 'File uploaded successfully', 'filename': filename,'document_id':document_id}), 200
    else:
        return jsonify({'error': 'File type not allowed'}), 400


# Route for searching text in MongoDB
@app.route('/search', methods=['GET', 'POST'])
async def search_text_in_mongodb_lakshya():
    try:
        # print("This is the search api")
        if request.method == 'POST':
            # Example: Get query from JSON body
            data = request.get_json()

            user_id = session.get('user_id')
            if not user_id:
                return jsonify({'error': 'No document_id found in session'}), 400
            print("This is the search api and this is *document_id*", user_id)

            query = data.get('query')
            print(query)
            if not query:
                return jsonify({'error': 'Missing query parameter'}), 400


            data = await find_document(user_id)
            print("This is the data after the find document")
            # print(data)
            texts = data['texts']

            docsearch = FAISS.from_texts(texts, embedding) 

            # new_db = FAISS.load_local("faiss_index", embedding)
            # docs = new_db.similarity_search(query)

            print('*'*30) 
            print(docsearch)
            print('*'*30)

            docs = docsearch.similarity_search(query)
            print("This is the docs data after the similarity search")
            print(docs)

            answer = chain.run(input_documents=docs, question=query)

            print("This is the answer")
            print(answer)
            if answer is None:
                return jsonify({'message': 'An error occurred during search'}), 500
            
            return jsonify({'result': answer}),200

            # results = await find_document(user_id)
            # print(results)
            # context, question = results['Original_text'],query
            # print("This is the context and question")
            # print(context, question)

            # result = find_question_response(context,question)
            # if result is None:
            #     return jsonify({'message': 'An error occurred during search'}), 500
            
            # return jsonify({'result': result}), 200

        elif request.method == 'GET':
            return jsonify({'message': 'Send a POST request with JSON body {`query`: `search text`}'}), 200

    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({'error': 'Internal server error'}), 500


# Route for searching text in MongoDB
@app.route('/find_resume', methods=['GET', 'POST'])
async def search_resume_in_database():
    try:
        # print("This is the search api")
        if request.method == 'POST':
            # Example: Get query from JSON body
            data = request.get_json()

            # user_id = session.get('user_id')
            # if not user_id:
            #     return jsonify({'error': 'No document_id found in session'}), 400
            # print("This is the search api and this is *document_id*", user_id)

            query = data.get('query')
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
    app.run(host='0.0.0.0', port=8000, debug=True)
    # app.run(debug=True)
