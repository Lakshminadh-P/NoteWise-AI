"""
AI-powered flashcard and quiz generation using Google Gemini.
"""

import json
from google import genai
from google.genai import types

from app.config import get_settings


def _get_client() -> genai.Client:
    settings = get_settings()
    return genai.Client(api_key=settings.GEMINI_API_KEY)


async def generate_flashcards(text_chunk: str, topic_hint: str = "") -> list[dict]:
    """
    Generate flashcards from a text chunk using Gemini.

    Returns:
        List of dicts with "front", "back", and "topic_tag" keys.
    """
    prompt = f"""Analyze the following study material and generate flashcards for effective learning.

Study Material:
{text_chunk}

{"Topic: " + topic_hint if topic_hint else ""}

Generate 5-10 flashcards. Each flashcard should test a key concept, definition, or relationship.

Respond ONLY with a JSON array where each element has:
- "front": the question or term (concise, clear)
- "back": the answer or definition (complete but brief)
- "topic_tag": a short topic category (1-3 words)

Example format:
[{{"front": "What is photosynthesis?", "back": "The process by which plants convert sunlight, CO2, and water into glucose and oxygen.", "topic_tag": "Biology"}}]
"""

    client = _get_client()
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            temperature=0.7,
        ),
    )

    try:
        return json.loads(response.text)
    except json.JSONDecodeError:
        return []


async def generate_quiz_questions(text_chunk: str, num_questions: int = 5) -> list[dict]:
    """
    Generate quiz questions (MCQ and free-text) from a text chunk.

    Returns:
        List of dicts with question data.
    """
    prompt = f"""Analyze the following study material and create quiz questions to test understanding.

Study Material:
{text_chunk}

Generate {num_questions} questions — mix of multiple-choice and free-text.

Respond ONLY with a JSON array where each element has:
- "question_text": the question
- "question_type": "mcq" or "free_text"
- "reference_answer": the correct/ideal answer
- "options": for MCQ only, an object like {{"A": "...", "B": "...", "C": "...", "D": "..."}}; null for free_text
- "correct_option": for MCQ only, the letter ("A", "B", "C", or "D"); null for free_text
- "difficulty": 1-5 (1=easy, 5=hard)
"""

    client = _get_client()
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            temperature=0.7,
        ),
    )

    try:
        return json.loads(response.text)
    except json.JSONDecodeError:
        return []
