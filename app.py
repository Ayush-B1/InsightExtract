from flask import Flask, request, jsonify, render_template, send_file, redirect
from transformers import BartForConditionalGeneration, BartTokenizer
import torch
import requests
from bs4 import BeautifulSoup
import PyPDF2
import re
from fpdf import FPDF

app = Flask(__name__)

# Load the pre-trained BART model and tokenizer
model = BartForConditionalGeneration.from_pretrained("facebook/bart-large-cnn")
tokenizer = BartTokenizer.from_pretrained("facebook/bart-large-cnn")

# Function to clean the text
def clean_text(text):
    """
    Clean the input text by removing unnecessary characters and spaces.
    """
    text = re.sub(r"http\S+", "", text)  # Remove URLs
    text = re.sub(r"\s+", " ", text)  # Remove extra spaces
    text = re.sub(r"[^a-zA-Z0-9 .,?!'\"-]", "", text)  # Remove special characters
    return text.strip()

# Function to preprocess data: Clean, tokenize and prepare text for summarization
def preprocess_data(text):
    """
    Preprocesses the text by cleaning and tokenizing it.
    """
    # Clean the text (remove special characters, URLs, etc.)
    cleaned_text = clean_text(text)
    
    # Tokenize the cleaned text
    inputs = tokenizer(cleaned_text, max_length=1024, padding="max_length", truncation=True, return_tensors="pt")
    
    return inputs

# Function to scrape and extract text from a website using URL
def extract_text_from_url(url):
    """
    Extracts the main content from a website using BeautifulSoup.
    """
    try:
        response = requests.get(url)
        if response.status_code != 200:
            return f"Error: Unable to fetch the page, status code {response.status_code}"

        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extracting text from <p> tags (or other relevant tags)
        paragraphs = soup.find_all('p')
        text = ' '.join([para.get_text() for para in paragraphs])
        
        if not text.strip():
            return "Error: No text found in the webpage."

        return clean_text(text)  # Clean the extracted text
    except requests.exceptions.RequestException as e:
        return f"Error: Failed to retrieve the webpage. {str(e)}"

# Function to extract text from a PDF
def extract_text_from_pdf(file):
    """
    Extract text from the uploaded PDF file.
    """
    try:
        pdf_reader = PyPDF2.PdfReader(file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        
        if not text.strip():
            return "Error: No text found in the PDF."
        
        return clean_text(text)
    except Exception as e:
        return f"Error: Failed to process the PDF. {str(e)}"

# Function to generate summary using the BART model
def generate_summary(text):
    """
    Generate a summary for the input text using BART.
    """
    inputs = preprocess_data(text)

    with torch.no_grad():
        summary_ids = model.generate(
            inputs["input_ids"], attention_mask=inputs["attention_mask"], max_length=128, min_length=40, 
            length_penalty=2.0, num_beams=4
        )

    summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
    return summary

# Function to create a PDF of the summary
def create_pdf(summary_text):
    """
    Creates a PDF document containing the summary text.
    """
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.multi_cell(0, 10, summary_text)
    
    pdf_output_path = "/tmp/summary.pdf"  # Temporary file location
    pdf.output(pdf_output_path)
    
    return pdf_output_path

# Route for the index page (main summarization page)
@app.route('/')
def index():
    return redirect('/summarize_page')

# Route to summarize text from direct input
@app.route('/summarize', methods=['POST'])
def summarize():
    text = request.get_json().get('text', '')

    if text:
        # Clean and generate summary
        cleaned_text = clean_text(text)
        summary = generate_summary(cleaned_text)
        
        return jsonify({"summary": summary}), 200
    else:
        return jsonify({"error": "No text provided"}), 400

# Route to summarize text from a website URL
@app.route('/summarize_url', methods=['POST'])
def summarize_url():
    url = request.get_json().get('url', '')
    
    if url:
        # Extract text from the website URL
        webpage_text = extract_text_from_url(url)
        
        if "Error" in webpage_text:
            return jsonify({"error": webpage_text}), 400
        
        # Generate summary
        summary = generate_summary(webpage_text)
        
        return jsonify({"summary": summary}), 200
    else:
        return jsonify({"error": "No URL provided"}), 400

# Route to summarize the uploaded PDF file
@app.route('/upload', methods=['POST'])
def upload_pdf():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if file and file.filename.endswith('.pdf'):
        pdf_text = extract_text_from_pdf(file)
        if "Error" in pdf_text:
            return jsonify({"error": pdf_text}), 400

        # Generate summary
        summary = generate_summary(pdf_text)

        return jsonify({"summary": summary}), 200
    else:
        return jsonify({"error": "Invalid file format. Please upload a PDF."}), 400

# Route to download the summary as PDF
@app.route('/download_summary', methods=['POST'])
def download_summary():
    summary_text = request.get_json().get('summary', '')

    if summary_text:
        # Create a PDF of the summary text
        pdf_path = create_pdf(summary_text)

        return send_file(pdf_path, as_attachment=True, download_name="summary.pdf")
    else:
        return jsonify({"error": "No summary text provided"}), 400

# Route to render the summarization page
@app.route('/summarize_page')
def summarize_page():
    return render_template('summarize.html')

if __name__ == "__main__":
    # Run the app
    app.run(debug=True)
