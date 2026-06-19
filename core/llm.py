import os
from groq import Groq
import logging

logger = logging.getLogger("LLM")

# System persona prompt
SYSTEM_PROMPT = {
    "role": "system",
    "content": (
        "You are a friendly, polite, and helpful AI customer support assistant for Flipkart. "
        "Your goal is to serve customers by answering their queries about products, orders, returns, and FAQs. "
        "Keep your answers concise, helpful, and in character. Always remain polite and professional. "
        "Greet the user warmly."
    )
}

def get_chat_response(chat_history):
    """
    Sends the chat history to the Groq API using Llama3-8b-8192 and returns the assistant response.
    
    Args:
        chat_history (list): List of dicts representing message history: [{"role": "...", "content": "..."}]
        
    Returns:
        str: Assistant response.
    """
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        logger.error("GROQ_API_KEY environment variable is not set.")
        return "⚠️ Groq API key is missing. Please set your GROQ_API_KEY in the .env file."
        
    try:
        client = Groq(api_key=api_key)
        
        # Prepend system prompt to user history
        messages = [SYSTEM_PROMPT] + [
            {"role": msg["role"], "content": msg["content"]} 
            for msg in chat_history
        ]
        
        response = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=messages,
            temperature=0.7,
            max_tokens=1024
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        logger.error(f"Error calling Groq API: {e}")
        return "Sorry, I am currently unable to process your request due to an API connectivity issue. Please try again in a moment."
