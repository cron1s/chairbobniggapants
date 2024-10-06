import openai

openai.api_key = hehehe

def chat_with_gpt(prompt):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # Specify the model
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message['content'].strip()  # Return the chatbot's response
    except Exception as e:
        print(f"Error: {e}")
        return "Sorry, I couldn't process that."

if __name__ == "__main__":
    print("Welcome to the Chatbot! Type 'quit', 'exit', or 'bye' to end the conversation.")
    while True:
        user_input = input("You: ")
        if user_input.lower() in ["quit", "exit", "bye"]:
            print("Goodbye!")
            break

        response = chat_with_gpt(user_input)
        print("Chatbot:", response)