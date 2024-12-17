# experiment 1 re-serving ollama local phi-4
#
from flask import Flask, request, jsonify
import requests
import json
import os

app = Flask(__name__)

OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434")
OLLAMA_GENERATE_URL = f"{OLLAMA_URL}/api/generate"

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
            "stream": False # For this simple example, we're not streaming
        }

        response = requests.post(OLLAMA_GENERATE_URL, json=ollama_data)
        response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
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

if __name__ == '__main__':
    app.run(debug=True)
