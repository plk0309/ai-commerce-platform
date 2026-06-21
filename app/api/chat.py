from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import re

from app.recommendation.recommender import recommend
from app.analytics.intent import detect_analytics_intent, extract_analytics_entities
from app.analytics.engine import (
    get_kpi_summary, get_revenue_by_month, get_top_products,
    get_top_countries, get_customer_stats, get_revenue_trend,
    detect_anomalies, get_revenue_by_day, get_revenue_comparison,
)
from app.llm.shopping_prompt import get_shopping_reply
from app.llm.analytics_prompt import get_analytics_reply
from app.analytics.intent import (
    INTENT_KPI, INTENT_REVENUE, INTENT_PRODUCTS, INTENT_CUSTOMERS,
    INTENT_TREND, INTENT_COMPARISON, INTENT_ANOMALY,
    INTENT_COUNTRY, INTENT_DAY, INTENT_UNKNOWN,
)

router = APIRouter()

# Shopping keywords — if any match, route to shopping assistant
SHOPPING_KEYWORDS = [
    "recommend", "suggest", "buy", "purchase", "earbuds", "headphone",
    "laptop", "keyboard", "mouse", "cable", "speaker", "phone", "tablet",
    "charger", "camera", "monitor", "printer", "router", "ssd", "pen drive",
    "under", "below", "budget", "cheap", "affordable", "best product",
    "wireless", "bluetooth", "gaming", "mechanical", "waterproof",
    "show me", "find me", "i need", "looking for", "gift",
]

# Chat session store — holds full conversation history per session
_chat_sessions: dict = {}


class ChatRequest(BaseModel):
    message   : str
    session_id: str = "default"
    role      : str = "customer"   # "customer" | "admin"

    class Config:
        json_schema_extra = {
            "example": {
                "message"   : "recommend wireless earbuds under 2000",
                "session_id": "user_123",
                "role"      : "customer",
            }
        }


def _get_session(session_id: str) -> list:
    if session_id not in _chat_sessions:
        _chat_sessions[session_id] = []
    return _chat_sessions[session_id]


def _is_shopping_query(message: str, role: str) -> bool:
    """Route to shopping if role=customer OR message contains shopping keywords."""
    if role == "admin":
        return False
    msg = message.lower()
    return any(kw in msg for kw in SHOPPING_KEYWORDS)


def _run_analytics_engine(intent: str, entities: dict):
    """Run the right analytics function based on intent."""
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
        data, summary = None, "I couldn't understand that query. Try: 'show KPIs', 'top products', 'revenue trend', 'why did sales drop'"

    return data, summary


@router.post("/chat", summary="Unified AI Chatbot — Shopping + Analytics")
def chat(req: ChatRequest):
    """
    One endpoint for everything.

    - role='customer' → Shopping Assistant (product recommendations)
    - role='admin'    → Analytics Assistant (business insights)
    - Auto-detects based on message keywords if role is ambiguous

    Maintains full conversation history per session_id.
    """
    message = req.message.strip()
    if not message:
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    history = _get_session(req.session_id)

    try:
        if _is_shopping_query(message, req.role):
            # ── Shopping path ─────────────────────────────────
            result   = recommend(query=message, session_id=req.session_id, top_k=5)
            products = result["products"]
            intent   = result["intent"]
            entities = result["entities"]

            if products:
                llm_reply = get_shopping_reply(
                    user_query=message,
                    products=products,
                    intent=intent,
                    entities=entities,
                )
            else:
                llm_reply = ("I couldn't find products matching your request. "
                             "Try adjusting your budget or removing brand filters.")

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
            # ── Analytics path ────────────────────────────────
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
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")

    # Save to history
    history.append({"role": "user",      "content": message})
    history.append({"role": "assistant", "content": llm_reply})

    return response