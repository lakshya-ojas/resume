from flask import Flask, request, jsonify
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import sqlite3

app = Flask(__name__)

# Initialize TF-IDF Vectorizer
vectorizer = TfidfVectorizer()

# Function to connect to SQLite database
def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/store_vector', methods=['POST'])
def store_vector():
    data = request.json
    
    if 'id' not in data or 'text' not in data:
        return jsonify({'error': 'Invalid data format'}), 400
    
    text = data['text']
    vector = get_vector(text)
    
    conn = get_db_connection()
    conn.execute('INSERT INTO vectors (id, text, vector) VALUES (?, ?, ?)',
                 (data['id'], text, vector.tobytes()))
    conn.commit()
    conn.close()
    
    return jsonify({'message': 'Vector stored successfully'}), 201

@app.route('/get_vector/<id>', methods=['GET'])
def get_vector_by_id(id):
    conn = get_db_connection()
    vector_data = conn.execute('SELECT * FROM vectors WHERE id = ?', (id,)).fetchone()
    conn.close()
    
    if not vector_data:
        return jsonify({'error': 'Vector not found'}), 404
    
    return jsonify({
        'id': vector_data['id'],
        'text': vector_data['text'],
        'vector': np.frombuffer(vector_data['vector'], dtype=np.float64).tolist()
    })

@app.route('/search_similar', methods=['POST'])
def search_similar():
    data = request.json
    
    if 'query' not in data:
        return jsonify({'error': 'Invalid request format. Missing "query" parameter.'}), 400
    
    query_text = data['query']
    query_vector = get_vector(query_text)
    
    conn = get_db_connection()
    cursor = conn.execute('SELECT id, text, vector FROM vectors')
    
    results = []
    for row in cursor:
        stored_vector = np.frombuffer(row['vector'], dtype=np.float64)
        similarity = cosine_similarity([query_vector], [stored_vector])[0][0]
        results.append({
            'id': row['id'],
            'text': row['text'],
            'similarity': similarity
        })
    
    conn.close()
    
    # Sort results by similarity (highest to lowest)
    results.sort(key=lambda x: x['similarity'], reverse=True)
    
    return jsonify(results), 200

def get_vector(text):
    return vectorizer.fit_transform([text]).toarray().squeeze()

if __name__ == '__main__':
    app.run(debug=True)
