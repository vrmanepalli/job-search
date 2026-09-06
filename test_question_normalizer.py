from linkedin_agent.application_service import (
    normalize_question,
)


questions = [
    "Are you authorized to work in the US?",

    "Are you legally authorized to work in the United States?",

    "Do you currently have US work authorization?",

    "Will you now or in the future require sponsorship?",

    "Will this employer need to sponsor you?",

    "How many years of management experience do you have?",

    "How many years of leadership experience do you have?",

    "What are your salary expectations?",

    "What is your desired compensation?",

    "Are you willing to relocate?",

    "What is your favorite programming language?",
]


for question in questions:

    key = normalize_question(question)

    print()
    print("Question:", question)
    print("Key:", key)