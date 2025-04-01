from flask import Flask, request, jsonify, render_template
import requests
import pymupdf   # PyMuPDF for extracting text from PDFs
import os

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
    return jsonify({"message": "PDF uploaded and processed successfully"})

@app.route("/ask", methods=["POST"])
def ask():
    user_input = request.json.get("question", "")
    
    keywords = ["suman", "linkedin", "github", "skills", "company", "work", "previous", "current"]
    if any(keyword in user_input.lower() for keyword in keywords) and pdf_text:
        context_text = f"Context from PDF:\n{pdf_text[:2000]}\n"
    else:
        context_text = "(General knowledge response, not using PDF)"
    
    prompt = f"{context_text}\nUser's question: {user_input}"
    
    data = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False
    }
    
    response = requests.post(OLLAMA_API_URL, json=data)
    
    if response.status_code == 200:
        return jsonify(response.json())
    else:
        return jsonify({"error": "Failed to get response"}), 500

def extract_text_from_pdf(pdf_path):
    """Extract text from a PDF file."""
    text = ""
    with pymupdf.open(pdf_path) as doc:
        for page in doc:
            text += page.get_text("text") + "\n"
    return text

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
