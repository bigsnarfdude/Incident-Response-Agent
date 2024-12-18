from flask import Flask, request, jsonify
import openai
import os
import time

openai.api_key = 'sk-proj-90tQhbUeQA'

app = Flask(__name__)

UPLOAD_DIR = "./uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)  # Ensure the directory exists

def upload_file_to_openai(file_path):
    with open(file_path, 'rb') as file:
        response = openai.files.create(
            file=file,
            purpose='assistants'
        )
    return response.id  # File ID

# Function to create an assistant
def create_assistant(file_ids):
    assistant = openai.beta.assistants.create(
        name="File Search Assistant",
        instructions="You are an assistant capable of searching through uploaded files.",
        tools=[{"type": "file_search"}],
        model="gpt-4-turbo",
        file_ids=file_ids
    )
    return assistant.id  # Assistant ID

# Function to create a thread
def create_thread():
    thread = openai.beta.threads.create()
    return thread.id  # Thread ID

# Function to send a message
def send_message(thread_id, message_content):
    message = openai.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=message_content
    )
    return message.id  # Message ID

# Function to run the assistant
def run_assistant(thread_id, assistant_id):
    run = openai.beta.threads.runs.create(
        thread_id=thread_id,
        assistant_id=assistant_id
    )
    return run.id  # Run ID

# Function to poll and get the assistant's response
def get_run_response(thread_id, run_id):
    while True:
        run = openai.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run_id)
        if run.status == "completed":
            break
        time.sleep(1)  # Poll every second

    # Retrieve messages from the thread
    messages = openai.beta.threads.messages.list(thread_id=thread_id)
    return [
        {"role": message.role, "content": message.content[0].text.value}
        for message in messages.data
    ]

# Flask API Routes
@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    uploaded_file = request.files['file']
    file_path = os.path.join(UPLOAD_DIR, uploaded_file.filename)
    uploaded_file.save(file_path)

    try:
        file_id = upload_file_to_openai(file_path)
        os.remove(file_path)  # Delete local file after uploading
        return jsonify({"file_id": file_id}), 200
    except Exception as e:
        os.remove(file_path)
        return jsonify({"error": str(e)}), 500

@app.route('/create-assistant', methods=['POST'])
def create():
    data = request.get_json()
    file_id = data.get('file_id')

    if not file_id:
        return jsonify({"error": "file_id is required"}), 400

    try:
        assistant_id = create_assistant([file_id])
        return jsonify({"assistant_id": assistant_id}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/create-thread', methods=['GET'])
def thread():
    try:
        thread_id = create_thread()
        return jsonify({"thread_id": thread_id}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/send-message', methods=['POST'])
def send():
    data = request.get_json()
    thread_id = data.get('thread_id')
    message_content = data.get('message_content')

    if not thread_id or not message_content:
        return jsonify({"error": "thread_id and message_content are required"}), 400

    try:
        message_id = send_message(thread_id, message_content)
        return jsonify({"message_id": message_id}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/run-assistant', methods=['POST'])
def run():
    data = request.get_json()
    thread_id = data.get('thread_id')
    assistant_id = data.get('assistant_id')

    if not thread_id or not assistant_id:
        return jsonify({"error": "thread_id and assistant_id are required"}), 400

    try:
        run_id = run_assistant(thread_id, assistant_id)
        return jsonify({"run_id": run_id}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/get-response', methods=['POST'])
def response():
    data = request.get_json()
    thread_id = data.get('thread_id')
    run_id = data.get('run_id')

    if not thread_id or not run_id:
        return jsonify({"error": "thread_id and run_id are required"}), 400

    try:
        messages = get_run_response(thread_id, run_id)
        return jsonify({"messages": messages}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Main entry point
if __name__ == '__main__':
    app.run(debug=True)
