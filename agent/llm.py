import os

from google import genai
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

client = genai.Client(
    api_key=api_key
) if api_key else None


def ask_llm(question, context):
    if not client:
        return "Error: GEMINI_API_KEY is not configured in the environment variables."

    prompt = f"""
    Answer ONLY using the provided context.

    Context:
    {context}

    Question:
    {question}

    If the answer is not in the context,
    say "No relevant information found."
    """

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    return response.text