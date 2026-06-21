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
    """
    Single function used by both assistants.
    Sends system_prompt + user_message to Groq LLaMA and returns text reply.
    """
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


if __name__ == "__main__":
    reply = get_llm_response(
        system_prompt="You are a helpful assistant.",
        user_message="Say hello in one sentence."
    )
    print(reply)