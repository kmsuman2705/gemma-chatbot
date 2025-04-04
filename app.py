from flask import Flask, request, jsonify, render_template
import requests
import fitz  # PyMuPDF
import os

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

OLLAMA_API_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "mario"

pdf_text = ""  # Global variable to store PDF content

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

    pdf_text = extract_text_from_pdf(filepath)

    print("PDF Uploaded and text extracted.")
    return jsonify({"message": "PDF uploaded and processed successfully"})


@app.route("/ask", methods=["POST"])
def ask():
    user_input = request.json.get("question", "")

    if not pdf_text.strip():
        return jsonify({"error": "No PDF content available. Please upload a PDF first."}), 400

    prompt = f"""
You are a helpful assistant. Use ONLY the following PDF content to answer the user's question.

PDF Content:
\"\"\"
{pdf_text}
\"\"\"

If the answer is not clearly found in the above text, just respond with: "Sorry, I don't know based on the PDF."

Now answer this question:
{user_input}
"""

    data = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False
    }

    try:
        response = requests.post(OLLAMA_API_URL, json=data)
        if response.status_code == 200:
            return jsonify(response.json())
        else:
            return jsonify({"error": "Failed to get response from model"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def extract_text_from_pdf(pdf_path):
    text = ""
    try:
        with fitz.open(pdf_path) as doc:
            for page in doc:
                text += page.get_text("text") + "\n"
    except Exception as e:
        print(f"Error reading PDF: {e}")
    return text


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
