from flask import Flask, request, jsonify, send_file
import ollama
import logging
from functools import lru_cache
import tempfile
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Configure logging
def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s: %(message)s',
        handlers=[
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

logger = setup_logging()

@lru_cache(maxsize=1000)
def classify_with_model(text, model_name):
    """
    Classifies text using a specific Ollama model.
    """
    try:
        response = ollama.chat(model=model_name, messages=[
            {
                'role': 'system', 
                'content': 'You are a language classification assistant. Respond ONLY with "English" or "French".'
            },
            {
                'role': 'user', 
                'content': f'Classify the language of this text: "{text}"'
            }
        ])
        
        classification = response['message']['content'].strip()
        
        if classification not in ["English", "French"]:
            return "Unclassified"
        
        return classification
    
    except Exception as e:
        logger.error(f"Classification error with model {model_name}: {e}")
        return "Unclassified"

def classify_language(text):
    """
    Classifies text using a two-model approach.
    """
    primary_result = classify_with_model(text, 'llama3.2:latest')
    
    if primary_result != "Unclassified":
        return primary_result, "llama32"
    
    secondary_result = classify_with_model(text, 'vanilj/Phi-4:latest')
    return secondary_result, "Phi-4"

def process_file(input_file_path):
    """
    Process the uploaded file and return English lines.
    """
    stats = {
        'total_lines': 0,
        'english_lines': 0,
        'unclassified_lines': 0,
        'llama2_classifications': 0,
        'phi4_classifications': 0
    }
    
    english_lines = []
    unclassified_lines = []
    
    try:
        with open(input_file_path, 'r', encoding='utf-8') as infile:
            for line in infile:
                stats['total_lines'] += 1
                line = line.strip()
                
                if not line:
                    continue
                
                classification, model_used = classify_language(line)
                
                if model_used == "llama2":
                    stats['llama2_classifications'] += 1
                else:
                    stats['phi4_classifications'] += 1
                
                if classification == "English":
                    english_lines.append(line)
                    stats['english_lines'] += 1
                elif classification == "Unclassified":
                    unclassified_lines.append(line)
                    stats['unclassified_lines'] += 1
                
        return {
            'english_lines': english_lines,
            'unclassified_lines': unclassified_lines,
            'stats': stats
        }
    
    except Exception as e:
        logger.error(f"Error processing file: {e}")
        raise

@app.route('/classify', methods=['POST'])
def classify_file():
    """
    Endpoint to handle file upload and classification.
    """
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    try:
        # Create a temporary file to store the upload
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            file.save(temp_file.name)
            
            # Process the file
            result = process_file(temp_file.name)
            
            # Clean up the temporary file
            os.unlink(temp_file.name)
            
            return jsonify({
                'status': 'success',
                'english_lines': result['english_lines'],
                'unclassified_lines': result['unclassified_lines'],
                'statistics': result['stats']
            })
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
