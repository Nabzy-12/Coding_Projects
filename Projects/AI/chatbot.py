from transformers import pipeline

chatbot = pipeline("text-generation", model="distilgpt2")

while True:
    user_input = input("You: ")
    if user_input.lower() in ["exit", "quit", "bye"]:
        break
    bot_response = chatbot(user_input, max_length=150, num_return_sequences=1)[0]["generated_text"]
    print("Bot: " + bot_response)