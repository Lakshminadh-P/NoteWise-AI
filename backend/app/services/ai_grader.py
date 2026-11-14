"""
AI-powered grading service for free-text quiz responses.
"""

import json
from google import genai
from google.genai import types

from app.config import get_settings


async def grade_free_text(
    question: str,
    reference_answer: str,
    user_answer: str,
) -> dict:
    """
    Grade a free-text answer using Gemini.

    Returns:
        Dict with "score" (0.0-5.0) and "feedback" (str).
    """
    prompt = f"""You are an expert academic grader. Grade the student's answer on a scale of 0 to 5.

Question: {question}

Reference Answer: {reference_answer}

Student's Answer: {user_answer}

Grading Scale:
5 - Perfect answer, demonstrates complete understanding
4 - Mostly correct, minor omissions
3 - Partially correct, shows basic understanding
2 - Mostly incorrect, but shows some relevant knowledge
1 - Largely wrong, only tangentially related
0 - Completely wrong or blank

Respond ONLY with a JSON object:
{{"score": <float 0.0-5.0>, "feedback": "<brief constructive feedback>"}}
"""

    settings = get_settings()
    client = genai.Client(api_key=settings.GEMINI_API_KEY)

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            temperature=0.3,
        ),
    )

    try:
        result = json.loads(response.text)
        return {
            "score": max(0.0, min(5.0, float(result.get("score", 0)))),
            "feedback": result.get("feedback", ""),
        }
    except (json.JSONDecodeError, ValueError):
        return {"score": 0.0, "feedback": "Grading failed. Please try again."}
