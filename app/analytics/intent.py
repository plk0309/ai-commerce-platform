import re

INTENT_KPI         = "kpi_summary"
INTENT_REVENUE     = "revenue_analysis"
INTENT_PRODUCTS    = "product_analysis"
INTENT_CUSTOMERS   = "customer_analysis"
INTENT_TREND       = "trend_analysis"
INTENT_COMPARISON  = "comparison"
INTENT_ANOMALY     = "anomaly_detection"
INTENT_COUNTRY     = "country_analysis"
INTENT_DAY         = "day_analysis"
INTENT_UNKNOWN     = "unknown"


def detect_analytics_intent(query: str) -> str:
    q = query.lower().strip()

    if re.search(r"(kpi|overview|summary|dashboard|snapshot|business|total|all metrics|show)", q):
        return INTENT_KPI

    if re.search(r"(anomal|spike|drop|why|unusual|sudden|problem|issue|decline|fell|decreased)", q):
        return INTENT_ANOMALY

    if re.search(r"(compare|vs|versus|difference|growth)", q):
        return INTENT_COMPARISON

    if re.search(r"(trend|growing|declining|trajectory|over time|month by month|quarterly)", q):
        return INTENT_TREND

    if re.search(r"(country|countries|region|geographic|location|where|market)", q):
        return INTENT_COUNTRY

    if re.search(r"(day|weekday|monday|tuesday|wednesday|thursday|friday|saturday|sunday|best day)", q):
        return INTENT_DAY

    if re.search(r"(customer|buyer|client|top buyer|loyal|repeat|who bought)", q):
        return INTENT_CUSTOMERS

    if re.search(r"(product|item|sell|sold|top product|best product|popular|bestseller|selling)", q):
        return INTENT_PRODUCTS

    if re.search(r"(revenue|sales|earning|income|profit|money|turnover|amount)", q):
        return INTENT_REVENUE

    return INTENT_UNKNOWN


def extract_analytics_entities(query: str) -> dict:
    q = query.lower()
    entities = {"period": None, "period2": None, "top_k": 10, "by": "revenue"}

    month_map = {
        "january": "01", "february": "02", "march": "03",
        "april": "04", "may": "05", "june": "06",
        "july": "07", "august": "08", "september": "09",
        "october": "10", "november": "11", "december": "12",
    }

    for month_name, month_num in month_map.items():
        if month_name in q:
            year_match = re.search(r"(20\d{2})", q)
            year = year_match.group(1) if year_match else "2011"
            if entities["period"] is None:
                entities["period"] = f"{year}-{month_num}"
            else:
                entities["period2"] = f"{year}-{month_num}"

    period_matches = re.findall(r"(20\d{2}-\d{2})", q)
    if period_matches:
        entities["period"] = period_matches[0]
        if len(period_matches) > 1:
            entities["period2"] = period_matches[1]

    k_match = re.search(r"top\s+(\d+)", q)
    if k_match:
        entities["top_k"] = min(int(k_match.group(1)), 100)

    if re.search(r"(quantity|units|volume|pieces)", q):
        entities["by"] = "quantity"

    return entities
