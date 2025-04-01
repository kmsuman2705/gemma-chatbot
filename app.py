from flask import Flask, request, jsonify, render_template
import requests

app = Flask(__name__)

OLLAMA_API_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "mario"

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/ask", methods=["POST"])
def ask():
    user_input = request.json.get("question", "")

    data = {
        "model": MODEL_NAME,
        "prompt": user_input,
        "stream": False
    }
    
    response = requests.post(OLLAMA_API_URL, json=data)
    
    if response.status_code == 200:
        return jsonify(response.json())
    else:
        return jsonify({"error": "Failed to get response"}), 500

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
