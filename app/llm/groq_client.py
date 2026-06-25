import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

_client = None

def _get_client() -> Groq:
    global _client
    if _client is None:
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY not found in .env file")
        _client = Groq(api_key=api_key)
    return _client


def get_llm_response(system_prompt: str, user_message: str, max_tokens: int = 500) -> str:
    """Single-turn: system prompt + one user message."""
    try:
        client = _get_client()
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user",   "content": user_message},
            ],
            max_tokens=max_tokens,
            temperature=0.7,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"LLM unavailable: {str(e)}"


def get_llm_response_with_history(
    system_prompt: str,
    history: list,
    max_tokens: int = 500,
) -> str:
    """
    Multi-turn: system prompt + full conversation history.
    history format: [{"role": "user"|"assistant", "content": "..."}]
    """
    try:
        client = _get_client()
        messages = [{"role": "system", "content": system_prompt}] + history
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=messages,
            max_tokens=max_tokens,
            temperature=0.7,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"LLM unavailable: {str(e)}"