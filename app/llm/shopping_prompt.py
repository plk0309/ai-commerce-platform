from app.llm.groq_client import get_llm_response, get_llm_response_with_history

SHOPPING_SYSTEM_PROMPT = """You are a friendly AI Shopping Assistant for an Indian e-commerce platform.

STRICT RULES — follow these exactly:

1. VAGUE queries (no specific product category confirmed yet):
   - Ask ONE short question only. Nothing else. No product suggestions at all.
   - Ask about the specific category or interest first.
   - If you know it is a gift, ask what the person's interest is.
   - Examples:
     "What kind of product are you looking for — electronics, clothing, accessories, or something else?"
     "What are her interests — art, tech, fashion, fitness, or something else?"
   - NEVER suggest products before the category is confirmed.

2. CLEAR queries (specific product category confirmed):
   - Recommend the products provided. Max 3-4 sentences total.
   - Mention product name, price, and one key reason it fits.
   - Confirm budget fit if budget was mentioned.
   - Do NOT use markdown like **bold** or asterisks.
   - Do NOT number products like "1." "2." "3."

3. Always use Indian Rupee (Rs.) for prices.
4. Never make up products — only use what is provided.
5. If no products match, say so in one sentence and suggest relaxing filters.
6. Keep every reply short. Never exceed 4 sentences.
7. NEVER suggest products when you are still in clarification mode.
8. If the products provided do not match the customer's requested category at all, 
   be honest — say that category is not available and mention what we do have 
   (electronics, stationery, art supplies, home items, kitchen appliances).
   Never recommend an unrelated product as if it matches.
"""

VAGUE_PATTERNS = [
    "suggest me something",
    "suggest something",
    "what should i buy",
    "what can i buy",
    "recommend something",
    "recommend me something",
    "help me choose",
    "don't know what to buy",
    "not sure what to buy",
    "anything good",
    "something good",
    "good product",
    "best product",
    "what to buy",
    "help me find something",
    "suggest me",
    "something to buy",
    "what do you suggest",
    "what would you recommend",
    "give me suggestions",
    "give me recommendations",
    "what should i get",
    "what can you suggest",
    "any suggestions",
    "any recommendations",
    # gift-related vague patterns
    "something for my",
    "suggest for my",
    "gift for my",
    "recommend for my",
    "buy for my",
    "get for my",
    "suggest me something for",
    "what to gift",
    "what should i gift",
]

CLEAR_SIGNALS = [
    "earbuds", "headphone", "laptop", "keyboard", "mouse", "speaker",
    "phone", "tablet", "charger", "camera", "monitor", "printer",
    "router", "ssd", "pen drive", "cable", "watch", "tv", "fan",
    "cooler", "mixer", "iron", "trimmer", "bag", "shoes", "shirt",
    "dress", "notebook", "calculator", "pen", "bottle", "backpack",
    "electronics", "clothing", "home", "kitchen", "stationery",
    "gaming", "wireless", "bluetooth", "appliance",
    "art", "craft", "beauty", "makeup", "jewellery", "jewelry",
    "book", "toy", "sport", "fitness", "music", "perfume", "drawing",
]


def is_vague_query(message: str) -> bool:
    msg = message.lower()
    has_vague = any(p in msg for p in VAGUE_PATTERNS)
    has_clear = any(s in msg for s in CLEAR_SIGNALS)
    return has_vague and not has_clear


def format_products_for_prompt(products: list) -> str:
    if not products:
        return "No products found."
    lines = []
    for p in products[:5]:
        lines.append(
            f"- {p.get('product_name', '')[:80]} | "
            f"Rs.{p.get('discounted_price', 0):,.0f} | "
            f"Rating: {p.get('rating', 0)}"
        )
    return "\n".join(lines)


def get_clarifying_reply(history: list) -> str:
    return get_llm_response_with_history(
        system_prompt=SHOPPING_SYSTEM_PROMPT,
        history=history,
        max_tokens=80,
    )


def get_shopping_reply(
    user_query: str,
    products: list,
    intent: str,
    entities: dict,
    history: list = None,
) -> str:
    products_text = format_products_for_prompt(products)

    context_parts = []
    if entities.get("budget"):
        context_parts.append(f"Budget: Rs.{entities['budget']:,.0f}")
    if entities.get("brand"):
        context_parts.append(f"Brand: {entities['brand']}")
    if entities.get("category"):
        context_parts.append(f"Category: {entities['category']}")
    context = " | ".join(context_parts) if context_parts else "No specific filters"

    product_context_message = f"""Customer query: "{user_query}"
Filters: {context}

Top matching products:
{products_text}

IMPORTANT: Check if the products actually match the customer's request.
- If they match well → give a short helpful recommendation in max 3 sentences. No markdown, no bold, no numbered lists.
- If they do NOT match the category requested → honestly say this category is not available in our inventory. Mention what we do have: electronics, stationery, art supplies, home items, kitchen appliances. Do NOT recommend unrelated products as if they match.
Max 3 sentences total."""

    if history:
        enriched_history = history[:-1] + [{"role": "user", "content": product_context_message}]
        return get_llm_response_with_history(
            system_prompt=SHOPPING_SYSTEM_PROMPT,
            history=enriched_history,
            max_tokens=300,
        )
    else:
        return get_llm_response(SHOPPING_SYSTEM_PROMPT, product_context_message, max_tokens=300)