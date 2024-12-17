# experiment 2 - added document markdown conversion endpoint

from flask import Flask, request, jsonify
import requests
import json
import os
from markitdown import MarkItDown

app = Flask(__name__)
markitdown = MarkItDown()

# Ollama Configuration
OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434")
OLLAMA_GENERATE_URL = f"{OLLAMA_URL}/api/generate"

# File Upload Configuration
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'xlsx', 'xls', 'csv', 'pdf'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# curl -X POST -H "Content-Type: application/json" -d '{"question": "What is the capital of France?"}' http://127.0.0.1:5000/ask
@app.route('/ask', methods=['POST'])
def ask_ollama():
    try:
        data = request.get_json()
        if not data or 'question' not in data:
            return jsonify({"error": "Missing 'question' in request body"}), 400

        question = data['question']
        model = data.get('model', 'vanilj/Phi-4')

        ollama_data = {
            "model": model,
            "prompt": question,
            "stream": False
        }

        response = requests.post(OLLAMA_GENERATE_URL, json=ollama_data)
        response.raise_for_status()
        ollama_response = response.json()

        if 'response' in ollama_response:
            answer = ollama_response['response']
            return jsonify({"answer": answer})
        elif 'error' in ollama_response:
            return jsonify({"error": ollama_response['error']}), 500
        else:
            return jsonify({"error": "Unexpected response from Ollama"}), 500

    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Error communicating with Ollama: {e}"}), 500
    except json.JSONDecodeError as e:
        return jsonify({"error": f"Error decoding Ollama JSON response: {e}"}), 500
    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {e}"}), 500


# curl -X POST -F "file=@Microsoft-Incident-Response-Customer-Datasheet-FEB2024.pdf" http://127.0.0.1:5000/convert_to_markdown
@app.route('/convert_to_markdown', methods=['POST'])
def convert_to_markdown():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    if not allowed_file(file.filename):
        return jsonify({"error": "File type not allowed. Allowed types: xlsx, xls, csv"}), 400

    try:
        filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filename)

        result = markitdown.convert(filename)
        os.remove(filename)

        if hasattr(result, 'text_content'):
            return jsonify({"markdown": result.text_content})
        else:
            return jsonify({"error": "Conversion did not produce text content"}), 500

    except Exception as e:
        return jsonify({"error": f"Error during conversion: {e}"}), 500


if __name__ == '__main__':
    app.run(debug=True)
