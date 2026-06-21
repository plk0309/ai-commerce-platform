from app.llm.groq_client import get_llm_response

SHOPPING_SYSTEM_PROMPT = """You are an AI Shopping Assistant for an e-commerce platform.
Your job is to help customers find the best products based on their needs.

Rules:
- Be helpful, friendly and concise (3-5 sentences max)
- Always mention product name, price, and rating
- Explain WHY each product matches the user's request
- If budget was mentioned, confirm the product fits it
- If no products found, suggest relaxing the filters
- Use Indian Rupee (₹) for prices
- Never make up products — only use what's provided
"""


def format_products_for_prompt(products: list) -> str:
    """Convert product list to readable text for the LLM."""
    if not products:
        return "No products found."
    lines = []
    for p in products[:5]:  # max 5 products to keep prompt small
        lines.append(
            f"- {p.get('product_name','')[:80]} | "
            f"₹{p.get('discounted_price',0):,.0f} | "
            f"⭐{p.get('rating',0)} | "
            f"Score: {p.get('final_score', p.get('similarity_score',0))}"
        )
    return "\n".join(lines)


def get_shopping_reply(
    user_query: str,
    products: list,
    intent: str,
    entities: dict,
) -> str:
    """
    Generate a natural language shopping recommendation reply.

    Args:
        user_query : original user query
        products   : ranked product list from recommender
        intent     : detected intent string
        entities   : extracted entities (budget, brand, category)
    """
    products_text = format_products_for_prompt(products)

    # Build context string from entities
    context_parts = []
    if entities.get("budget"):
        context_parts.append(f"Budget: ₹{entities['budget']:,.0f}")
    if entities.get("brand"):
        context_parts.append(f"Brand preference: {entities['brand']}")
    if entities.get("category"):
        context_parts.append(f"Category: {entities['category']}")
    context = " | ".join(context_parts) if context_parts else "No specific filters"

    user_message = f"""Customer query: "{user_query}"
Intent: {intent}
Filters: {context}

Top matching products:
{products_text}

Please provide a helpful shopping recommendation response."""

    return get_llm_response(SHOPPING_SYSTEM_PROMPT, user_message, max_tokens=400)


if __name__ == "__main__":
    # Quick test without needing the full search engine
    dummy_products = [
        {"product_name": "boAt Airdopes 141 TWS Earbuds", "discounted_price": 1299,
         "rating": 4.1, "final_score": 0.82},
        {"product_name": "Zebronics Zeb-Sound Bomb TWS", "discounted_price": 999,
         "rating": 3.8, "final_score": 0.76},
    ]
    reply = get_shopping_reply(
        user_query="wireless earbuds under 2000",
        products=dummy_products,
        intent="budget_filter",
        entities={"budget": 2000, "brand": None, "category": "Electronics"}
    )
    print(reply)