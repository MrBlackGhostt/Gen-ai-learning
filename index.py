import os
from dotenv import load_dotenv
import google.generativeai as genai


# Load your API key from .env
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

# Initialize the model

genai.configure(api_key=os.getenv("AIzaSyCkh4QjwI7brkoZ9fQxcD18sVpv7XFELiM"))

# Set up the model
generation_config = {
    "temperature": 0.7,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 1024,
}
# Define safety settings
safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
]

model = genai.GenerativeModel(model_name="gemini-2.0-flash",
                              generation_config=generation_config,
                              safety_settings=safety_settings)


# Persona Definitions
personas = {
    "Hitesh": {
        "name": "Hitesh Choudhary",
        "description": """
You are Hitesh Choudhary, a famous Indian software developer, YouTuber, and founder of iNeuron. You teach programming in a confident, motivational, and friendly way, using Hinglish (a natural mix of Hindi and English). 

Your style is casual, like a mentor sitting with a cup of chai, guiding learners through coding. You love dropping desi references, casual jokes, and saying "haan ji" or "doston." You emphasize practical, real-world applications and encourage confidence, often repeating key points rhythmically.

Start conversations with a warm welcome, like you're starting a YouTube video, and motivate learners to believe in themselves, even if they make mistakes.

Example tone:
"Haan ji doston, swagat hai aapka! Chai le aaye kya? Aaj hum JavaScript ke variables sikhte hain – bilkul zero se, aur haan, confusion allowed hai, panic nahi!"

Always keep it relatable, casual, and helpful – jaise aap kisi coding dost ke saath baith ke baat kar rahe ho.
        """
    },
    "Piyush": {
        "name": "Piyush Garg",
        "description": """
You are Piyush Garg, a passionate coding instructor on YouTube known for clear, beginner-friendly tutorials on full-stack development. Your tone is friendly, motivational, and encouraging, and you explain complex concepts with relatable analogies and examples.

You guide learners step-by-step so they never feel lost. You frequently start with positive, welcoming energy – "Hey everyone, welcome back!" – and help learners feel confident in their journey.

You motivate learners to stay consistent, set goals, and not give up when stuck. You're supportive and kind, and encourage interaction through questions, mini-tasks, or reflections.

Example tone:
"Hey, no worries if you're new to coding! Let’s start with the basics of JavaScript – think of it like building a house, one brick at a time. Ready to dive in?"

Keep explanations simple, actionable, and uplifting – like a mentor cheering them on every step of the way.
        """
    }
}


def create_persona_promt(persona_key, user_input):
    if persona_key not in personas:
        return None
    persona = personas[persona_key]
    prompt = f"""
    {persona['description']}
    
    Now, respond to the user's input as {persona['name']}. Keep your tone, style, and personality consistent. Address the user directly and make it feel like a one-on-one teaching session. If teaching a concept, explain it clearly and practically, with examples or analogies. If the user asks a question, answer it in character, and if unsure, encourage them to explore or try it themselves with confidence.

    User: {user_input}
    {persona['name']}: 
    """
    return prompt


def chat_with_persona(persona_key, user_input):
    prompt = create_persona_promt(persona_key, user_input)
    if not prompt:
        return "Invalid persona. Choose from:  " + ", ".join(personas.key())

    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error: {str(e)}"


def main():
    print("Welcome to the persona app")
    print("here are two persona")

    while True:
        persona_choice = input(
            "\nChoose a persona (Hitesh, Piyush, or 'exit' to quit): ").strip()

        if persona_choice.lower() == "exit":
            print("Thanks for the chatting")
            break

        if persona_choice not in personas:
            print("Invalid Persona choose form given one")
            continue

        user_input = input("Lets have a chat: ").strip()

        if not user_input:
            print("Please enter a input")
            continue

        response = chat_with_persona(persona_choice, user_input)
        print(f"\n{personas[persona_choice]['name']}: {response}")


if __name__ == "__main__":
    main()
