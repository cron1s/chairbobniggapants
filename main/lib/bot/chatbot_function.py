import openai
from collections import deque  # For storing shared conversation history

openai.api_key = "hehehhahaha"  # Replace with your actual API key

# Shared conversation history
shared_conversation_history = deque(maxlen=20)  # Store up to 20 previous messages

# Default temperature for OpenAI API
temperature = 0.7

# Function to chat with GPT using the shared conversation history
def chat_with_gpt(prompt):
    # Add the user's message to the shared history
    shared_conversation_history.append({"role": "user", "content": prompt})

    # Prepare the messages to send to GPT-3.5
    messages = [
        {"role": "system", "content": (
            "You are a fun and chatty cleaning lady from South Tyrol who loves gossip. "
            "Your name is Putzfrau, and you always speak in the South Tyrolean dialect. "
            "You enjoy complaining about your old friend 'Saily', and you love to spread rumors and gossip. "
            "Whenever you can, you talk about Saily in a negative way and spread local gossip. "
            "Answer all questions like a typical South Tyrolean cleaning lady."
        )}
    ]

    # Add the shared conversation history to the messages
    messages.extend(shared_conversation_history)

    try:
        # Send the entire conversation history to GPT with the default temperature
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=temperature  # Use the fixed temperature of 0.7
        )

        # Add the assistant's response to the shared history
        bot_response = response.choices[0].message['content'].strip()
        shared_conversation_history.append({"role": "assistant", "content": bot_response})

        return bot_response
    except Exception as e:
        print(f"Error: {e}")
        return "Entschuldigung, i honn des net ganz verstan'n."
