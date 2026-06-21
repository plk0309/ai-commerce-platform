import pandas as pd
import numpy as np
from app.analytics.data_loader import load_retail_data


def _get_df() -> pd.DataFrame:
    return load_retail_data()


# ── 1. KPI Summary ───────────────────────────────────────────────────────────
def get_kpi_summary() -> dict:
    """Total revenue, orders, customers, AOV for entire dataset."""
    df = _get_df()
    total_revenue  = round(df["Revenue"].sum(), 2)
    total_orders   = df["InvoiceNo"].nunique()
    total_customers = df[df["CustomerID"] != "Guest"]["CustomerID"].nunique()
    aov            = round(total_revenue / total_orders, 2) if total_orders else 0

    return {
        "total_revenue"   : total_revenue,
        "total_orders"    : total_orders,
        "total_customers" : total_customers,
        "average_order_value": aov,
        "date_range": {
            "from": str(df["InvoiceDate"].min().date()),
            "to"  : str(df["InvoiceDate"].max().date()),
        }
    }


# ── 2. Revenue Analysis ───────────────────────────────────────────────────────
def get_revenue_by_month(last_n: int = 12) -> list:
    """Monthly revenue for the last N months."""
    df = _get_df()
    monthly = (
        df.groupby("MonthStr")["Revenue"]
        .sum()
        .reset_index()
        .sort_values("MonthStr")
        .tail(last_n)
    )
    result = []
    prev   = None
    for _, row in monthly.iterrows():
        rev    = round(row["Revenue"], 2)
        growth = None
        if prev is not None and prev > 0:
            growth = round(((rev - prev) / prev) * 100, 1)
        result.append({
            "month"          : row["MonthStr"],
            "revenue"        : rev,
            "growth_pct"     : growth,
        })
        prev = rev
    return result


def get_revenue_comparison(period1: str, period2: str) -> dict:
    """
    Compare revenue between two months.
    period format: 'YYYY-MM'  e.g. '2011-11'
    """
    df = _get_df()
    def rev_for(period):
        sub = df[df["MonthStr"] == period]
        return round(sub["Revenue"].sum(), 2)

    r1 = rev_for(period1)
    r2 = rev_for(period2)
    change = round(((r2 - r1) / r1 * 100), 1) if r1 > 0 else None

    return {
        period1       : r1,
        period2       : r2,
        "change_pct"  : change,
        "direction"   : "up" if (change or 0) > 0 else "down",
    }


# ── 3. Top Products ───────────────────────────────────────────────────────────
def get_top_products(top_k: int = 10, by: str = "revenue") -> list:
    """
    Top products by revenue or quantity.
    by: 'revenue' | 'quantity'
    """
    df    = _get_df()
    col   = "Revenue" if by == "revenue" else "Quantity"
    label = "revenue" if by == "revenue" else "quantity_sold"

    grouped = (
        df.groupby("Description")
        .agg(
            revenue      = ("Revenue",  "sum"),
            quantity_sold= ("Quantity", "sum"),
            orders       = ("InvoiceNo","nunique"),
        )
        .reset_index()
        .sort_values(col, ascending=False)
        .head(top_k)
    )

    return [
        {
            "rank"         : i + 1,
            "product"      : row["Description"],
            "revenue"      : round(row["revenue"], 2),
            "quantity_sold": int(row["quantity_sold"]),
            "orders"       : int(row["orders"]),
        }
        for i, (_, row) in enumerate(grouped.iterrows())
    ]


# ── 4. Top Countries ──────────────────────────────────────────────────────────
def get_top_countries(top_k: int = 10) -> list:
    df = _get_df()
    grouped = (
        df.groupby("Country")
        .agg(revenue=("Revenue","sum"), orders=("InvoiceNo","nunique"))
        .reset_index()
        .sort_values("revenue", ascending=False)
        .head(top_k)
    )
    total = df["Revenue"].sum()
    return [
        {
            "rank"      : i + 1,
            "country"   : row["Country"],
            "revenue"   : round(row["revenue"], 2),
            "orders"    : int(row["orders"]),
            "share_pct" : round(row["revenue"] / total * 100, 1),
        }
        for i, (_, row) in enumerate(grouped.iterrows())
    ]


# ── 5. Customer Analytics ─────────────────────────────────────────────────────
def get_customer_stats() -> dict:
    df = _get_df()
    df_known = df[df["CustomerID"] != "Guest"]

    customer_rev = df_known.groupby("CustomerID")["Revenue"].sum()
    customer_ord = df_known.groupby("CustomerID")["InvoiceNo"].nunique()

    top_customers = (
        customer_rev.sort_values(ascending=False)
        .head(10)
        .reset_index()
        .rename(columns={"Revenue": "total_spent"})
    )

    return {
        "total_customers"       : int(df_known["CustomerID"].nunique()),
        "avg_spend_per_customer": round(customer_rev.mean(), 2),
        "avg_orders_per_customer": round(customer_ord.mean(), 2),
        "top_customers": [
            {
                "rank"       : i + 1,
                "customer_id": row["CustomerID"],
                "total_spent": round(row["total_spent"], 2),
            }
            for i, (_, row) in enumerate(top_customers.iterrows())
        ],
    }


# ── 6. Trend Analysis ─────────────────────────────────────────────────────────
def get_revenue_trend() -> dict:
    """
    Compares last 3 months vs previous 3 months.
    Returns trend direction and growth.
    """
    df      = _get_df()
    monthly = df.groupby("MonthStr")["Revenue"].sum().sort_index()
    months  = list(monthly.index)

    if len(months) < 6:
        return {"error": "Not enough data for trend analysis"}

    recent   = monthly[months[-3:]].sum()
    previous = monthly[months[-6:-3]].sum()
    growth   = round(((recent - previous) / previous) * 100, 1) if previous > 0 else 0

    return {
        "recent_3_months_revenue"  : round(recent, 2),
        "previous_3_months_revenue": round(previous, 2),
        "growth_pct"               : growth,
        "trend"                    : "growing" if growth > 0 else "declining",
        "recent_months"            : months[-3:],
        "previous_months"          : months[-6:-3],
    }


def get_monthly_trend_series() -> list:
    """Full monthly series for charting."""
    df = _get_df()
    monthly = df.groupby("MonthStr")["Revenue"].sum().reset_index().sort_values("MonthStr")
    return [
        {"month": row["MonthStr"], "revenue": round(row["Revenue"], 2)}
        for _, row in monthly.iterrows()
    ]


# ── 7. Anomaly Detection ──────────────────────────────────────────────────────
def detect_anomalies() -> dict:
    """
    Flags months where revenue deviated > 1.5 std from mean.
    Returns anomalous months with direction (spike/drop).
    """
    df      = _get_df()
    monthly = df.groupby("MonthStr")["Revenue"].sum()

    mean = monthly.mean()
    std  = monthly.std()
    threshold = 1.5

    anomalies = []
    for month, rev in monthly.items():
        z = (rev - mean) / std if std > 0 else 0
        if abs(z) > threshold:
            anomalies.append({
                "month"    : month,
                "revenue"  : round(rev, 2),
                "z_score"  : round(z, 2),
                "direction": "spike" if z > 0 else "drop",
                "deviation": f"{abs(round(z, 1))}x standard deviation",
            })

    return {
        "mean_monthly_revenue": round(mean, 2),
        "std_monthly_revenue" : round(std, 2),
        "anomalies_found"     : len(anomalies),
        "anomalies"           : anomalies,
    }


# ── 8. Day of Week Analysis ───────────────────────────────────────────────────
def get_revenue_by_day() -> list:
    df = _get_df()
    order = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
    grouped = df.groupby("DayOfWeek")["Revenue"].sum().reindex(order).reset_index()
    return [
        {"day": row["DayOfWeek"], "revenue": round(row["Revenue"], 2)}
        for _, row in grouped.iterrows()
        if not pd.isna(row["Revenue"])
    ]


if __name__ == "__main__":
    print("=== KPI Summary ===")
    print(get_kpi_summary())
    print("\n=== Top 5 Products ===")
    for p in get_top_products(5):
        print(f"  #{p['rank']} {p['product']} — £{p['revenue']:,.2f}")
    print("\n=== Trend ===")
    print(get_revenue_trend())
    print("\n=== Anomalies ===")
    print(detect_anomalies())