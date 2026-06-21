import json
from app.llm.groq_client import get_llm_response

ANALYTICS_SYSTEM_PROMPT = """You are an AI Business Analytics Assistant for a platform owner.
Your job is to explain business data in clear, actionable language.

Rules:
- Be professional and concise (3-5 sentences)
- Always highlight the most important number or insight first
- Mention trends, growth rates, or anomalies when present
- Give one actionable business recommendation at the end
- Use £ for currency (this is UK retail data)
- Never make up data — only use what's provided
- If data shows a problem, explain possible causes
"""


def format_analytics_for_prompt(intent: str, data: dict, summary: str) -> str:
    """Convert analytics data to readable text for the LLM."""
    if data is None:
        return f"Summary: {summary}"

    # For lists (top products, countries, monthly revenue), show top 5
    if isinstance(data, list):
        lines = []
        for item in data[:5]:
            lines.append(str(item))
        return f"Summary: {summary}\n\nData:\n" + "\n".join(lines)

    # For dicts (KPI, trend, anomaly), show key fields
    if isinstance(data, dict):
        # Limit nested lists inside dict to 3 items
        clean = {}
        for k, v in data.items():
            if isinstance(v, list):
                clean[k] = v[:3]
            else:
                clean[k] = v
        return f"Summary: {summary}\n\nData: {json.dumps(clean, indent=2)}"

    return f"Summary: {summary}"


def get_analytics_reply(
    user_query: str,
    intent: str,
    data,
    summary: str,
) -> str:
    """
    Generate a natural language business analytics reply.

    Args:
        user_query : original admin query
        intent     : detected analytics intent
        data       : raw data from analytics engine
        summary    : pre-computed summary string
    """
    data_text = format_analytics_for_prompt(intent, data, summary)

    user_message = f"""Admin query: "{user_query}"
Intent: {intent}

Analytics results:
{data_text}

Please provide a clear business insight response with one recommendation."""

    return get_llm_response(ANALYTICS_SYSTEM_PROMPT, user_message, max_tokens=400)


if __name__ == "__main__":
    dummy_data = {
        "total_revenue": 10666684.54,
        "total_orders": 22190,
        "total_customers": 4372,
        "average_order_value": 480.69,
    }
    reply = get_analytics_reply(
        user_query="show business KPIs",
        intent="kpi_summary",
        data=dummy_data,
        summary="Total revenue: £10.6M | Orders: 22,190 | Customers: 4,372 | AOV: £480.69"
    )
    print(reply)