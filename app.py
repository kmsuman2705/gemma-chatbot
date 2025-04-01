from flask import Flask, request, jsonify, render_template
import requests
import pymupdf  # PyMuPDF for extracting text from PDFs
import os
import pytesseract  # For OCR (Optical Character Recognition)
from PIL import Image

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
OLLAMA_API_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "mario"
pdf_text = ""  # Store extracted PDF text globally

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload_pdf():
    global pdf_text
    
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    
    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400
    
    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)
    
    # Extract text from the uploaded PDF
    pdf_text = extract_text_from_pdf(filepath)
    
    # Log extracted text to verify content
    print(f"Extracted PDF Text (first 500 characters): {pdf_text[:500]}")  # Log for debugging
    
    return jsonify({"message": "PDF uploaded and processed successfully"})

@app.route("/ask", methods=["POST"])
def ask():
    user_input = request.json.get("question", "")
    
    # Check if pdf_text is empty or not extracted
    if not pdf_text or len(pdf_text.strip()) == 0:
        return jsonify({"error": "No PDF content available. Please upload a PDF first."}), 400
    
    # Keywords to detect questions related to the PDF
    keywords = ["suman", "linkedin", "github", "skills", "company", "work", "previous", "current"]
    
    # Check if any keyword is in the user input (case-insensitive)
    if any(keyword in user_input.lower() for keyword in keywords):
        context_text = f"Context from PDF:\n{pdf_text[:2000]}\n"  # Only include part of the PDF text for context
    else:
        # If no relevant keywords, indicate that no relevant PDF content is being used
        context_text = "This question does not seem related to the PDF content. Please ask something relevant."

    # Create the prompt for the model
    prompt = f"{context_text}\nUser's question: {user_input}\n\nAnswer only based on the PDF content. Do not provide any other information."

    data = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False
    }
    
    response = requests.post(OLLAMA_API_URL, json=data)
    
    if response.status_code == 200:
        return jsonify(response.json())
    else:
        return jsonify({"error": "Failed to get response from model"}), 500

def extract_text_from_pdf(pdf_path):
    """Extract text from a PDF file, with fallback to OCR if no text is found."""
    text = ""
    
    try:
        with pymupdf.open(pdf_path) as doc:
            for page in doc:
                page_text = page.get_text("text")
                text += page_text + "\n"
                
                # If no text found in the page, use OCR as a fallback
                if not page_text.strip():
                    print(f"Warning: No text found on page {page.number + 1}, using OCR.")
                    image = page.get_image()
                    ocr_text = pytesseract.image_to_string(Image.open(image))
                    text += ocr_text + "\n"
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
    
    return text

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
