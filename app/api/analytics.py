from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.analytics.intent import (
    detect_analytics_intent, extract_analytics_entities,
    INTENT_KPI, INTENT_REVENUE, INTENT_PRODUCTS, INTENT_CUSTOMERS,
    INTENT_TREND, INTENT_COMPARISON, INTENT_ANOMALY,
    INTENT_COUNTRY, INTENT_DAY, INTENT_UNKNOWN,
)
from app.analytics.engine import (
    get_kpi_summary, get_revenue_by_month, get_revenue_comparison,
    get_top_products, get_top_countries, get_customer_stats,
    get_revenue_trend, get_monthly_trend_series,
    detect_anomalies, get_revenue_by_day,
)

router = APIRouter()


class AnalyticsRequest(BaseModel):
    query     : str
    session_id: str = "admin"

    class Config:
        json_schema_extra = {
            "example": {
                "query"     : "show business KPIs",
                "session_id": "admin_1",
            }
        }


# In-memory analytics session store
_analytics_sessions: dict = {}


def get_analytics_session(session_id: str) -> dict:
    if session_id not in _analytics_sessions:
        _analytics_sessions[session_id] = {
            "last_intent" : None,
            "last_entities": {},
        }
    return _analytics_sessions[session_id]


@router.post("/analytics", summary="Platform Owner AI Analytics Assistant")
def analytics_query(req: AnalyticsRequest):
    """
    Ask any business question in natural language.

    Examples:
    - "show business KPIs"
    - "top 10 products by revenue"
    - "revenue trend over time"
    - "compare october vs november 2011"
    - "why did sales drop"
    - "which country buys the most"
    - "top customers"
    - "best day for sales"
    """
    query = req.query.strip()
    if not query:
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    if len(query) > 500:
        raise HTTPException(status_code=400, detail="Query too long (max 500 chars)")

    # Detect intent and entities
    intent   = detect_analytics_intent(query)
    entities = extract_analytics_entities(query)

    # Save to session
    session = get_analytics_session(req.session_id)
    # Inherit previous entities for follow-ups
    if entities["period"] is None and session["last_entities"].get("period"):
        entities["period"] = session["last_entities"]["period"]

    _analytics_sessions[req.session_id] = {
        "last_intent"  : intent,
        "last_entities": entities,
    }

    # Route to correct engine function
    try:
        if intent == INTENT_KPI:
            data = get_kpi_summary()
            summary = (
                f"Total revenue: £{data['total_revenue']:,.2f} | "
                f"Orders: {data['total_orders']:,} | "
                f"Customers: {data['total_customers']:,} | "
                f"AOV: £{data['average_order_value']:.2f}"
            )

        elif intent == INTENT_REVENUE:
            data    = get_revenue_by_month(last_n=12)
            summary = f"Monthly revenue for last 12 months. Latest: £{data[-1]['revenue']:,.2f} ({data[-1]['growth_pct']:+.1f}% vs prev month)" if data else "No revenue data"

        elif intent == INTENT_PRODUCTS:
            data    = get_top_products(top_k=entities["top_k"], by=entities["by"])
            summary = f"Top {len(data)} products by {entities['by']}. #1: {data[0]['product']} — £{data[0]['revenue']:,.2f}" if data else "No product data"

        elif intent == INTENT_CUSTOMERS:
            data    = get_customer_stats()
            summary = (
                f"Total customers: {data['total_customers']:,} | "
                f"Avg spend: £{data['avg_spend_per_customer']:,.2f} | "
                f"Avg orders: {data['avg_orders_per_customer']:.1f}"
            )

        elif intent == INTENT_TREND:
            data    = get_revenue_trend()
            summary = (
                f"Business is {data.get('trend','unknown')}. "
                f"Last 3 months: £{data.get('recent_3_months_revenue',0):,.2f} "
                f"({data.get('growth_pct',0):+.1f}% vs previous 3 months)"
            ) if "error" not in data else data["error"]

        elif intent == INTENT_COMPARISON:
            p1 = entities.get("period")
            p2 = entities.get("period2")
            if not p1 or not p2:
                # Default: last two available months
                monthly = get_revenue_by_month(last_n=2)
                if len(monthly) >= 2:
                    p1 = monthly[-2]["month"]
                    p2 = monthly[-1]["month"]
                else:
                    return _error_response(query, intent, "Please specify two months to compare, e.g. 'compare 2011-10 vs 2011-11'")
            data    = get_revenue_comparison(p1, p2)
            summary = (
                f"{p1}: £{data[p1]:,.2f} → {p2}: £{data[p2]:,.2f} | "
                f"Change: {data['change_pct']:+.1f}% ({data['direction']})"
            )

        elif intent == INTENT_ANOMALY:
            data    = detect_anomalies()
            if data["anomalies_found"] == 0:
                summary = "No significant anomalies detected in revenue data."
            else:
                tops = data["anomalies"][:3]
                summary = f"Found {data['anomalies_found']} anomal{'y' if data['anomalies_found']==1 else 'ies'}. " + \
                          " | ".join(f"{a['month']}: {a['direction']} (z={a['z_score']})" for a in tops)

        elif intent == INTENT_COUNTRY:
            data    = get_top_countries(top_k=entities["top_k"])
            summary = f"Top country: {data[0]['country']} — £{data[0]['revenue']:,.2f} ({data[0]['share_pct']}% of total)" if data else "No country data"

        elif intent == INTENT_DAY:
            data    = get_revenue_by_day()
            best    = max(data, key=lambda x: x["revenue"]) if data else {}
            summary = f"Best sales day: {best.get('day','?')} — £{best.get('revenue',0):,.2f}" if best else "No day data"

        else:
            return _error_response(query, intent,
                "I couldn't understand that query. Try: 'show KPIs', 'top products', "
                "'revenue trend', 'compare months', 'why did sales drop', 'top countries'")

    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analytics error: {str(e)}")

    return {
        "query"  : query,
        "intent" : intent,
        "entities": entities,
        "summary": summary,
        "data"   : data,
    }


def _error_response(query, intent, message):
    return {
        "query"  : query,
        "intent" : intent,
        "entities": {},
        "summary": message,
        "data"   : None,
    }