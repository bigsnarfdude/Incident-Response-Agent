# logging_chat_by_person_for_monitoring.py

import json
import logging
from dotenv import load_dotenv
import os

import google.generativeai as genai
from google.ai.generativelanguage_v1beta.types import content

# Load environment variables from .env file
load_dotenv()

# Configure API key
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Model configuration
GENERATION_CONFIG = {
    "temperature": 0,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 8192,
}

system_instruction = "You are an expert at teaching science to kids. Your task is to engage in conversations about science and answer questions. Explain scientific concepts so that they are easily understandable. Use analogies and examples that are relatable. Use humor and make the conversation both educational and interesting. Ask questions so that you can better understand the user and improve the educational experience. Suggest ways that these concepts can be related to the real world with observations and experiments."

def create_chat_session(model_name="gemini-1.5-flash-8b", generation_config=GENERATION_CONFIG, system_instruction=system_instruction):
    """Creates a chat session with the specified model, configuration, and system instruction."""
    model = genai.GenerativeModel(
        model_name=model_name,
        generation_config=generation_config,
        system_instruction=system_instruction
    )
    return model.start_chat()

def send_message(chat_session, message, history):
    """Sends a message to the chat session, updates history, and returns the response."""
    response = chat_session.send_message(message)
    history.append({"role": "human", "content": message})
    history.append({"role": "ai", "content": response.text})
    return response.text

if __name__ == "__main__":
    first_name = input("Please enter your first name: ")

    # Configure logging with the student's first name
    log_filename = f"chat_history_{first_name}.log"
    logging.basicConfig(filename=log_filename, level=logging.INFO, format='%(message)s')

    chat_history = []
    chat_session = create_chat_session()

    while True:
        user_message = input("You: ")
        if user_message.lower() in ["bye", "quit"]:
            break

        response = send_message(chat_session, user_message, chat_history)
        print(f"Assistant: {response}")

    # Log the chat history as JSON
    logging.info(json.dumps(chat_history, indent=2))
