import os
import fitz  # PyMuPDF
import re
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
from sklearn.feature_extraction.text import TfidfVectorizer
from collections import Counter
import numpy as np
from flask_cors import CORS  # Add this import

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
app.config['UPLOAD_FOLDER'] = 'uploads/'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def extract_text_from_pdf(pdf_path):
    """Extract text from a PDF file."""
    doc = fitz.open(pdf_path)
    text = "\n".join([page.get_text() for page in doc])
    print(f"Extracted text: {text}")  # Debugging statement
    return text

def preprocess_text(text):
    """Clean the extracted text."""
    text = text.lower()
    text = re.sub(r'[^a-zA-Z0-9\s]', '', text)  # Remove special characters
    return text.strip()  # Trim whitespace

def extract_keywords(text_list, top_n=10):
    """Extract top N keywords from a list of texts."""
    vectorizer = TfidfVectorizer(stop_words='english', max_features=1000)
    tfidf_matrix = vectorizer.fit_transform(text_list)
    feature_names = vectorizer.get_feature_names_out()
    
    word_scores = np.asarray(tfidf_matrix.sum(axis=0)).flatten()
    word_freq = dict(zip(feature_names, word_scores))
    
    # Return keywords and their scores
    return [(word, round(score, 4)) for word, score in Counter(word_freq).most_common(top_n)]

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle PDF upload and analyze topics."""
    print("Received request to upload files.")  # Debugging statement
    if 'files' not in request.files:
        print("No file part in the request.")  # Debugging statement
        return jsonify({"error": "No file part"}), 400
    
    files = request.files.getlist('files')  # Get list of files
    if not files:
        print("No files selected.")  # Debugging statement
        return jsonify({"error": "No selected files"}), 400
    
    all_topics = []  # To store topics from all files
    
    for file in files:
        if file.filename == '':
            print("One or more files have no filename.")  # Debugging statement
            return jsonify({"error": "One or more files have no filename."}), 400
        
        if file and file.filename.endswith('.pdf'):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            print(f"Saved file: {filename}")  # Debugging statement
            
            text = extract_text_from_pdf(filepath)
            print(f"Extracted text from {filename}: {text}")  # Debugging statement
            
            cleaned_text = preprocess_text(text)
            print(f"Cleaned text from {filename}: {cleaned_text}")  # Debugging statement
            
            if not cleaned_text:  # Check if cleaned text is empty
                continue  # Skip this file if no valid text is extracted
            
            topics = extract_keywords([cleaned_text])
            all_topics.extend(topics)  # Add topics from this file to the list
    
    if not all_topics:
        return jsonify({"error": "No valid topics extracted from the uploaded PDFs."}), 400
    
    # Remove duplicates
    unique_topics = list(set(all_topics))
    
    # Format the output for better readability
    formatted_topics = [f"Keyword: {topic[0]}, Score: {topic[1]}" for topic in unique_topics]
    return jsonify({"topics": formatted_topics})

if __name__ == "__main__":
    app.run(debug=True)
