import pandas as pd
import os

RETAIL_PATH = "datasets/online_retail.csv"

_df_cache = None


def load_retail_data(force: bool = False) -> pd.DataFrame:
    """
    Load and clean online_retail.csv.

    Cleaning steps:
      - Remove cancelled orders (InvoiceNo starts with C)
      - Remove rows with Quantity <= 0 or UnitPrice <= 0
      - Parse InvoiceDate to datetime
      - Compute Revenue = Quantity * UnitPrice
      - Add Month and Year columns for grouping
      - Fill missing CustomerID with 'Guest'
      - Strip whitespace from Description

    Returns clean DataFrame cached in memory.
    """
    global _df_cache
    if _df_cache is not None and not force:
        return _df_cache

    if not os.path.exists(RETAIL_PATH):
        raise FileNotFoundError(
            f"Dataset not found at {RETAIL_PATH}. "
            "Please copy online_retail.csv into your datasets/ folder."
        )

    print("📦 Loading online_retail.csv...")
    df = pd.read_csv(RETAIL_PATH, encoding="unicode_escape")
    raw_count = len(df)

    # Remove cancelled orders
    df = df[~df["InvoiceNo"].astype(str).str.startswith("C")]

    # Remove invalid rows
    df = df[df["Quantity"] > 0]
    df = df[df["UnitPrice"] > 0]

    # Parse dates
    df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"])

    # Compute revenue
    df["Revenue"] = df["Quantity"] * df["UnitPrice"]

    # Time columns for grouping
    df["Month"]      = df["InvoiceDate"].dt.to_period("M")
    df["MonthStr"]   = df["InvoiceDate"].dt.strftime("%Y-%m")
    df["Year"]       = df["InvoiceDate"].dt.year
    df["Quarter"]    = df["InvoiceDate"].dt.to_period("Q").astype(str)
    df["DayOfWeek"]  = df["InvoiceDate"].dt.day_name()

    # Clean text
    df["Description"] = df["Description"].astype(str).str.strip().str.title()
    df["Country"]     = df["Country"].astype(str).str.strip()

    # Fill missing CustomerID
    df["CustomerID"] = df["CustomerID"].fillna(0).astype(int).astype(str)
    df["CustomerID"] = df["CustomerID"].replace("0", "Guest")

    df = df.reset_index(drop=True)
    _df_cache = df

    print(f"✅ Loaded {len(df):,} clean rows (removed {raw_count - len(df):,} invalid/cancelled)")
    print(f"   Revenue range: {df['InvoiceDate'].min().date()} → {df['InvoiceDate'].max().date()}")
    print(f"   Total revenue: £{df['Revenue'].sum():,.2f}")

    return df


if __name__ == "__main__":
    df = load_retail_data()
    print(df[["InvoiceNo", "Description", "Quantity", "Revenue", "MonthStr"]].head(5))