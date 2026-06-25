from app.llm.groq_client import get_llm_response, get_llm_response_with_history

# ── System prompt for conversational shopping assistant ──────────────────────
SHOPPING_SYSTEM_PROMPT = """You are a friendly AI Shopping Assistant for an Indian e-commerce platform.

Your behavior depends on what the user asks:

1. VAGUE / BUDGET-ONLY queries (e.g. "what should I buy under 5000", "suggest something"):
   - Ask 1-2 short clarifying questions to understand their need.
   - Example: "Sure! What are you looking for — electronics, clothing, home items, or something else? And is this for yourself or a gift?"
   - Keep it conversational and warm.

2. CLEAR queries (e.g. "wireless earbuds under 2000", "gaming keyboard"):
   - Recommend the products provided. Mention name, price, rating.
   - Explain briefly WHY each product fits their request.
   - Confirm the product fits their budget if one was mentioned.

Rules:
- Always use Indian Rupee (₹) for prices.
- Be concise — 3-5 sentences for recommendations, 1-2 for clarifying questions.
- Never make up products — only use what's provided in the context.
- If no products match, suggest relaxing filters.
- Remember previous messages in the conversation.
"""

# ── Intent check: is this query too vague to search directly? ────────────────
VAGUE_PATTERNS = [
    "what should i buy",
    "what can i buy",
    "suggest something",
    "recommend something",
    "good product",
    "best product",
    "something good",
    "anything good",
    "help me choose",
    "don't know what to buy",
    "not sure what",
]

CLEAR_SIGNALS = [
    # category keywords that make the query specific enough
    "earbuds", "headphone", "laptop", "keyboard", "mouse", "speaker",
    "phone", "tablet", "charger", "camera", "monitor", "printer",
    "router", "ssd", "pen drive", "cable", "watch", "tv", "fan",
    "cooler", "mixer", "iron", "trimmer", "bag", "shoes", "shirt",
]


def is_vague_query(message: str) -> bool:
    """
    Returns True if the query is too vague to search directly.
    A query is vague if it matches a vague pattern AND has no clear category signal.
    """
    msg = message.lower()
    has_vague_pattern = any(p in msg for p in VAGUE_PATTERNS)
    has_clear_signal  = any(s in msg for s in CLEAR_SIGNALS)
    return has_vague_pattern and not has_clear_signal


def format_products_for_prompt(products: list) -> str:
    """Convert product list to readable text for the LLM."""
    if not products:
        return "No products found."
    lines = []
    for p in products[:5]:
        lines.append(
            f"- {p.get('product_name', '')[:80]} | "
            f"₹{p.get('discounted_price', 0):,.0f} | "
            f"⭐{p.get('rating', 0)} | "
            f"Score: {p.get('final_score', p.get('similarity_score', 0))}"
        )
    return "\n".join(lines)


def get_clarifying_reply(history: list) -> str:
    """
    Called when the query is vague. LLM uses conversation history
    to ask a smart clarifying question.
    """
    return get_llm_response_with_history(
        system_prompt=SHOPPING_SYSTEM_PROMPT,
        history=history,
        max_tokens=150,
    )


def get_shopping_reply(
    user_query: str,
    products: list,
    intent: str,
    entities: dict,
    history: list = None,
) -> str:
    """
    Generate a natural language shopping recommendation reply.
    Passes full conversation history so the LLM has context.
    """
    products_text = format_products_for_prompt(products)

    context_parts = []
    if entities.get("budget"):
        context_parts.append(f"Budget: ₹{entities['budget']:,.0f}")
    if entities.get("brand"):
        context_parts.append(f"Brand preference: {entities['brand']}")
    if entities.get("category"):
        context_parts.append(f"Category: {entities['category']}")
    context = " | ".join(context_parts) if context_parts else "No specific filters"

    # Build the final user message with product context injected
    product_context_message = f"""Customer query: "{user_query}"
Intent: {intent}
Filters: {context}

Top matching products:
{products_text}

Please provide a helpful shopping recommendation response."""

    # Use history if available, otherwise fall back to single-turn
    if history:
        # Replace last user message with enriched version (includes product data)
        enriched_history = history[:-1] + [{"role": "user", "content": product_context_message}]
        return get_llm_response_with_history(
            system_prompt=SHOPPING_SYSTEM_PROMPT,
            history=enriched_history,
            max_tokens=400,
        )
    else:
        return get_llm_response(SHOPPING_SYSTEM_PROMPT, product_context_message, max_tokens=400)