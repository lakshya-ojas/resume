import PyPDF2
import docx
import spacy
from spacy.lang.en.stop_words import STOP_WORDS
from spacy.matcher import Matcher, PhraseMatcher
from spacy.lang.en import English
import re
import json
import os
import sys
from database_handler import create_table, insert_data

# Load spaCy model
nlp = spacy.load('en_core_web_lg')

def convert_pdf_to_text(pdf_path):
    """Converts a PDF file to text."""
    with open(pdf_path, 'rb') as pdf_file:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        num_pages = len(pdf_reader.pages)
        text = ''
        for page_num in range(num_pages):
            page = pdf_reader.pages[page_num]
            text += page.extract_text()
    return text

def convert_docx_to_text(docx_path):
    """Converts a DOCX file to text."""
    doc = docx.Document(docx_path)
    docx_text = '\n'.join([para.text for para in doc.paragraphs])
    return docx_text

def convert_txt_to_text(txt_path):
    """Converts a TXT file to text."""
    with open(txt_path, 'r', encoding='utf-8') as txt_file:
        txt_text = txt_file.read()
    return txt_text 

def save_text_to_file(text, output_path):
    """Saves text to a file."""
    with open(output_path, 'w', encoding='utf-8') as output_file:
        output_file.write(text)

def text_summarizer(text):
    """Summarizes text."""
    doc = nlp(text)
    stopwords = list(STOP_WORDS)
    word_freq = {}
    for word in doc:
        if word.text.lower() not in stopwords:
            if word.text.lower() not in word_freq:
                word_freq[word.text.lower()] = 1
            else:
                word_freq[word.text.lower()] += 1

    max_freq = max(word_freq.values())
    for word in word_freq:
        word_freq[word] = (word_freq[word] / max_freq)

    sentence_list = [sentence for sentence in doc.sents]
    sentence_scores = {}
    for sent in sentence_list:
        for word in sent:
            if word.text.lower() in word_freq:
                if sent not in sentence_scores:
                    sentence_scores[sent] = word_freq[word.text.lower()]
                else:
                    sentence_scores[sent] += word_freq[word.text.lower()]

    from heapq import nlargest
    summarized_sentences = nlargest(3, sentence_scores, key=sentence_scores.get)
    summarized_text = ' '.join([w.text for w in summarized_sentences])
    return summarized_text

def extract_entities(text):
    """Extracts entities (persons, phone numbers, emails) from text."""
    phone_pattern = r'\b(?:0|\+?91)?[789]\d{9}\b'  # Matches Indian mobile numbers
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    doc = nlp(text)
    
    entities = {
        "persons": [ent.text for ent in doc.ents if ent.label_ == "PERSON"],
        "phone_numbers": re.findall(phone_pattern, text),
        "emails": re.findall(email_pattern, text)
    }
    return entities

def convert_file_to_text(input_path, output_path):
    """Converts various file formats to text."""
    text = ""
    if input_path.endswith('.pdf'):
        text = convert_pdf_to_text(input_path)
    elif input_path.endswith('.docx'):
        text = convert_docx_to_text(input_path)
    elif input_path.endswith('.txt'):
        text = convert_txt_to_text(input_path)
    else:
        raise ValueError("Unsupported file type. Only PDF, DOCX, and TXT files are supported.")
    
    save_text_to_file(text, output_path)
    summarized_text = text_summarizer(text)
    save_text_to_file(summarized_text, "./output/summarize_text.txt")
    
    entities = extract_entities(text)
    return text, summarized_text, entities

def main():
    if len(sys.argv) != 3:
        print("Usage: python main.py <pdf_path> <output_directory>")
        return
    
    input_path = sys.argv[1]
    output_dir = sys.argv[2]
    # pdf_path = r'./Resume.pdf'  # Replace with your PDF file path
    # txt_path = 'TextExtract.txt'   # Replace with your desired output text file path

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Generate output paths
    filename = os.path.basename('TextExtract')
    output_path = os.path.join(output_dir, filename + ".txt")


    text, summarized_text, entities = convert_file_to_text(input_path, output_path)
    
    create_table()  # Create the table if it doesn't exist
    
    # Insert data into the database
    insert_data(json.dumps(entities), summarized_text, input_path)
    print("Data is inserted into the database")

if __name__ == "__main__":
    main()
