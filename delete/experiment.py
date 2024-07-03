import PyPDF2
import docx
import spacy
from spacy.lang.en.stop_words import STOP_WORDS
from spacy.matcher import Matcher, PhraseMatcher
from spacy.lang.en import English
import re
import json

# Load spaCy model
nlp = spacy.load('en_core_web_lg')
# sentencizer = English().create_pipe("sentencizer")
# nlp.add_pipe("sentencizer")

def convert_pdf_to_text(pdf_path):
    # Open the PDF file
    with open(pdf_path, 'rb') as pdf_file:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        num_pages = len(pdf_reader.pages)
        
        text = ''

        for page_num in range(num_pages):
            page = pdf_reader.pages[page_num]
            text += page.extract_text()

    return text
    
def convert_docx_to_text(docx_path):
    doc = docx.Document(docx_path)
    docx_text = '\n'.join([para.text for para in doc.paragraphs])
    return docx_text

def convert_txt_to_text(txt_path):
    with open(txt_path, 'r', encoding='utf-8') as txt_file:
        txt_text = txt_file.read()
    return txt_text 

#saving the file 
def save_text_to_file(text, output_path):
    with open(output_path, 'w', encoding='utf-8') as output_file:
        output_file.write(text)

def text_summarizer(text):
    # Process the text with spaCy
    doc = nlp(text)
    
    # Create a list of stopwords
    stopwords = list(STOP_WORDS)

    # Create word frequency table
    word_freq = {}
    for word in doc:
        if word.text.lower() not in stopwords:
            if word.text.lower() not in word_freq.keys():
                word_freq[word.text.lower()] = 1
            else:
                word_freq[word.text.lower()] += 1

    # Maximum frequency
    max_freq = max(word_freq.values())
    for word in word_freq.keys():
        word_freq[word] = (word_freq[word]/max_freq)

    # Sentence list
    sentence_list = [sentence for sentence in doc.sents]

    # Calculate sentence scores
    sentence_scores = {}
    for sent in sentence_list:
        for word in sent:
            if word.text.lower() in word_freq.keys():
                if sent not in sentence_scores.keys():
                    sentence_scores[sent] = word_freq[word.text.lower()]
                else:
                    sentence_scores[sent] += word_freq[word.text.lower()]

    # Find top N sentences
    from heapq import nlargest
    summarized_sentences = nlargest(3, sentence_scores, key=sentence_scores.get)
    summarized_sentences = [w.text for w in summarized_sentences]
    summarized_sentences = ' '.join(summarized_sentences)

    return summarized_sentences


phone_pattern = r'\b(?:0|\+?91)?[789]\d{9}\b'  # Matches Indian mobile numbers
email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'

def extract_entities(text):
    doc = nlp(text)
    
    # Extract entities
    entities = {
        "persons": [ent.text for ent in doc.ents if ent.label_ == "PERSON"],
        "phone_numbers": re.findall(phone_pattern, text),
        "emails": re.findall(email_pattern, text)
    }
    
    return entities





def convert_file_to_text(input_path, output_path):
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
    # Summarize the extracted text
    summarized_text = text_summarizer(text)

    save_text_to_file(summarized_text,"summarize_text.txt")

    entities = extract_entities(text)
    global contact_detail
    contact_detail = json.dumps(entities)
    print(entities)


contact_detail = ""
summary = ""
# Usage example
pdf_path = r'./Resume.pdf'  # Replace with your PDF file path
txt_path = 'TextExtract.txt'   # Replace with your desired output text file path

convert_file_to_text(pdf_path, txt_path)





from database_handler import create_table, insert_data
# Create the table if it doesn't exist (you can call this just once when setting up your application)
create_table()

def insertingData_to_database():

    insert_data(contact_detail,summary,pdf_path)
    print("Data is inserted into the database")