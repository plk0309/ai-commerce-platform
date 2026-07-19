import re
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.recommendation.recommender import recommend
from app.analytics.intent import detect_analytics_intent, extract_analytics_entities
from app.analytics.engine import (
    get_kpi_summary, get_revenue_by_month, get_top_products,
    get_top_countries, get_customer_stats, get_revenue_trend,
    detect_anomalies, get_revenue_by_day, get_revenue_comparison,
)
from app.llm.shopping_prompt import get_shopping_reply, get_clarifying_reply, is_vague_query
from app.llm.analytics_prompt import get_analytics_reply
from app.analytics.intent import (
    INTENT_KPI, INTENT_REVENUE, INTENT_PRODUCTS, INTENT_CUSTOMERS,
    INTENT_TREND, INTENT_COMPARISON, INTENT_ANOMALY,
    INTENT_COUNTRY, INTENT_DAY, INTENT_UNKNOWN,
)

router = APIRouter()

SHOPPING_KEYWORDS = [
    "recommend", "suggest", "buy", "purchase", "earbuds", "headphone",
    "laptop", "keyboard", "mouse", "cable", "speaker", "phone", "tablet",
    "charger", "camera", "monitor", "printer", "router", "ssd", "pen drive",
    "under", "below", "budget", "cheap", "affordable", "best product",
    "wireless", "bluetooth", "gaming", "mechanical", "waterproof",
    "show me", "find me", "i need", "looking for", "gift",
    "what should i buy", "what can i buy", "suggest something",
    "recommend something", "help me choose", "suggest me", "something to buy",
    "any suggestions", "any recommendations", "what to buy",
]

_chat_sessions: dict = {}
_shopping_sessions: set = set()


class ChatRequest(BaseModel):
    message   : str
    session_id: str = "default"
    role      : str = "customer"

    class Config:
        json_schema_extra = {
            "example": {
                "message"   : "what should I buy under 5000",
                "session_id": "user_123",
                "role"      : "customer",
            }
        }


def _get_session(session_id: str) -> list:
    if session_id not in _chat_sessions:
        _chat_sessions[session_id] = []
    return _chat_sessions[session_id]


def _is_shopping_query(message: str, role: str) -> bool:
    if role == "admin":
        return False
    msg = message.lower()
    return any(kw in msg for kw in SHOPPING_KEYWORDS)


def _session_is_shopping(session_id: str, role: str) -> bool:
    if role == "admin":
        return False
    return session_id in _shopping_sessions


def _context_has_category(history: list) -> bool:
    """
    Only returns True when a REAL product category is confirmed in user messages.
    Words like 'sister', 'gift', 'birthday' are NOT enough — we need an actual category.
    """
    CATEGORY_SIGNALS = [
        "earbuds", "headphone", "laptop", "keyboard", "mouse", "speaker",
        "phone", "tablet", "charger", "camera", "monitor", "tv", "fan",
        "cooler", "mixer", "iron", "trimmer", "bag", "shoes", "watch",
        "electronics", "clothing", "home", "kitchen", "appliance",
        "dress", "notebook", "calculator", "pen", "bottle", "backpack",
        "stationery", "gaming", "wireless", "bluetooth", "drawing",
        "art", "craft", "beauty", "makeup", "jewellery", "jewelry",
        "book", "toy", "sport", "fitness", "music", "perfume",
    ]
    user_messages = " ".join(
        m["content"].lower() for m in history if m["role"] == "user"
    )
    return any(s in user_messages for s in CATEGORY_SIGNALS)


def _build_enriched_query(history: list) -> str:
    """
    Build search query from last 2 user messages only.
    Avoids polluting the query with old unrelated messages.
    """
    user_messages = [m["content"] for m in history if m["role"] == "user"]
    recent = user_messages[-2:] if len(user_messages) >= 2 else user_messages
    return " ".join(recent)


def _clean_query(query: str) -> str:
    """
    Remove negative/exclusion phrases that confuse FAISS.
    e.g. 'suggest something other than tablet' → 'suggest something'
    """
    exclusion_patterns = [
        r'\bother than\s+\w+',
        r'\bnot\s+\w+',
        r'\bexcept\s+\w+',
        r'\binstead of\s+\w+',
        r'\bno\s+\w+',
        r'\bwithout\s+\w+',
    ]
    cleaned = query
    for pattern in exclusion_patterns:
        cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE)
    return cleaned.strip()


def _run_analytics_engine(intent: str, entities: dict):
    if intent == INTENT_KPI:
        data = get_kpi_summary()
        summary = (f"Total revenue: £{data['total_revenue']:,.2f} | "
                   f"Orders: {data['total_orders']:,} | "
                   f"Customers: {data['total_customers']:,} | "
                   f"AOV: £{data['average_order_value']:.2f}")
    elif intent == INTENT_REVENUE:
        data = get_revenue_by_month(last_n=12)
        summary = f"Monthly revenue for last 12 months. Latest: £{data[-1]['revenue']:,.2f}" if data else "No data"
    elif intent == INTENT_PRODUCTS:
        data = get_top_products(top_k=entities.get("top_k", 10), by=entities.get("by", "revenue"))
        summary = f"Top product: {data[0]['product']} — £{data[0]['revenue']:,.2f}" if data else "No data"
    elif intent == INTENT_CUSTOMERS:
        data = get_customer_stats()
        summary = (f"Total customers: {data['total_customers']:,} | "
                   f"Avg spend: £{data['avg_spend_per_customer']:,.2f}")
    elif intent == INTENT_TREND:
        data = get_revenue_trend()
        summary = (f"Business is {data.get('trend','unknown')}. "
                   f"Growth: {data.get('growth_pct', 0):+.1f}%")
    elif intent == INTENT_COMPARISON:
        p1 = entities.get("period")
        p2 = entities.get("period2")
        if p1 and p2:
            data = get_revenue_comparison(p1, p2)
            summary = f"{p1} vs {p2}: {data.get('change_pct', 0):+.1f}% change"
        else:
            monthly = get_revenue_by_month(last_n=2)
            if len(monthly) >= 2:
                p1, p2 = monthly[-2]["month"], monthly[-1]["month"]
                data = get_revenue_comparison(p1, p2)
                summary = f"{p1} vs {p2}: {data.get('change_pct', 0):+.1f}% change"
            else:
                data, summary = {}, "Not enough data to compare"
    elif intent == INTENT_ANOMALY:
        data = detect_anomalies()
        summary = (f"Found {data['anomalies_found']} anomalies." if data["anomalies_found"]
                   else "No anomalies detected.")
    elif intent == INTENT_COUNTRY:
        data = get_top_countries(top_k=10)
        summary = f"Top country: {data[0]['country']} — £{data[0]['revenue']:,.2f}" if data else "No data"
    elif intent == INTENT_DAY:
        data = get_revenue_by_day()
        best = max(data, key=lambda x: x["revenue"]) if data else {}
        summary = f"Best day: {best.get('day')} — £{best.get('revenue',0):,.2f}"
    else:
        data, summary = None, "I couldn't understand that. Try: 'show KPIs', 'top products', 'revenue trend'"
    return data, summary


@router.post("/chat", summary="Unified AI Chatbot — Shopping + Analytics")
def chat(req: ChatRequest):
    message = req.message.strip()
    if not message:
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    history = _get_session(req.session_id)
    history.append({"role": "user", "content": message})

    try:
        is_shopping = (
            _is_shopping_query(message, req.role) or
            _session_is_shopping(req.session_id, req.role)
        )

        if is_shopping:
            _shopping_sessions.add(req.session_id)

            current_is_vague = is_vague_query(message)
            history_has_context = _context_has_category(history)

            if current_is_vague and not history_has_context:
                llm_reply = get_clarifying_reply(history)
                response = {
                    "message"   : message,
                    "reply"     : llm_reply,
                    "type"      : "shopping_clarify",
                    "products"  : [],
                    "session_id": req.session_id,
                }

            else:
                search_query = (
                    _build_enriched_query(history)
                    if history_has_context and current_is_vague
                    else message
                )

                search_query = _clean_query(search_query)

                result   = recommend(query=search_query, session_id=req.session_id, top_k=5)
                products = result["products"]

                # Filter out products with very low similarity scores
                products = [p for p in products if p.get("similarity_score", 0) > 0.2]

                intent   = result["intent"]
                entities = result["entities"]

                if products:
                    llm_reply = get_shopping_reply(
                        user_query=message,
                        products=products,
                        intent=intent,
                        entities=entities,
                        history=history,
                    )
                else:
                    llm_reply = ("I couldn't find products matching your request in our current inventory. "
                                 "Try a different category or broaden your search.")

                response = {
                    "message"   : message,
                    "reply"     : llm_reply,
                    "type"      : "shopping",
                    "intent"    : intent,
                    "entities"  : entities,
                    "products"  : products,
                    "session_id": req.session_id,
                }

        else:
            intent   = detect_analytics_intent(message)
            entities = extract_analytics_entities(message)
            data, summary = _run_analytics_engine(intent, entities)

            llm_reply = get_analytics_reply(
                user_query=message,
                intent=intent,
                data=data,
                summary=summary,
            )

            response = {
                "message"   : message,
                "reply"     : llm_reply,
                "type"      : "analytics",
                "intent"    : intent,
                "data"      : data,
                "session_id": req.session_id,
            }

    except Exception as e:
        history.pop()
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")

    history.append({"role": "assistant", "content": llm_reply})
    return response