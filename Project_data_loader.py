import pandas as pd


def load_all(data_dir="data"):
    orders = pd.read_csv(f"{data_dir}/olist_orders_dataset.csv")
    items = pd.read_csv(f"{data_dir}/olist_order_items_dataset.csv")
    customers = pd.read_csv(f"{data_dir}/olist_customers_dataset.csv")
    sellers = pd.read_csv(f"{data_dir}/olist_sellers_dataset.csv")

    df = items.merge(orders, on="order_id")
    df = df.merge(customers[["customer_id", "customer_state"]], on="customer_id")
    df = df.merge(sellers[["seller_id", "seller_state"]], on="seller_id")

    df = df[df["order_status"] == "delivered"].copy()
    df["purchase_date"] = pd.to_datetime(df["order_purchase_timestamp"]).dt.date
    df["delivered_date"] = pd.to_datetime(df["order_delivered_customer_date"]).dt.date
    df["delivery_days"] = (
        pd.to_datetime(df["delivered_date"]) - pd.to_datetime(df["purchase_date"])
    ).dt.days
    df = df.dropna(subset=["delivery_days"]).copy()

    daily = (
        df.groupby("purchase_date")["price"].sum()
        .reset_index().sort_values("purchase_date")
    )
    daily_dates = daily["purchase_date"].tolist()
    daily_values = daily["price"].tolist()

    seller_stats = {}
    for sid, grp in df.groupby("seller_id"):
        seller_stats[sid] = {
            "orders": int(len(grp)),
            "revenue": round(float(grp["price"].sum()), 2),
            "avg_days": round(float(grp["delivery_days"].mean()), 2),
        }

    graph = {}
    for (src, dst), grp in df.groupby(["seller_state", "customer_state"]):
        if pd.isna(src) or pd.isna(dst):
            continue
        graph.setdefault(src, {})[dst] = round(float(grp["delivery_days"].mean()), 2)

    states = sorted(
        set(df["seller_state"].dropna()) | set(df["customer_state"].dropna())
    )

    return daily_dates, daily_values, seller_stats, graph, states