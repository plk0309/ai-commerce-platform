import pandas as pd

def load_products():

    df = pd.read_csv("datasets/products.csv")

    df = df[
        [
            "product_id",
            "product_name",
            "category",
            "about_product",
            "rating",
            "rating_count",
            "discounted_price"
        ]
    ]

    df = df.fillna("")

    df["combined_text"] = (
        df["product_name"].astype(str)
        + " "
        + df["category"].astype(str)
        + " "
        + df["about_product"].astype(str)
    )

    return df