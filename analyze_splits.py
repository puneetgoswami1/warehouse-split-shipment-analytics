import numpy as np
import pandas as pd


def generate_orders(num_orders=15000, seed=42):
    rng = np.random.default_rng(seed)

    regions = ["North", "West", "South", "East"]
    local_hub = {
        "North": "WH_DEL",
        "West": "WH_MUM",
        "South": "WH_BLR",
        "East": "WH_KOL",
    }

    main_skus = [f"SKU_MAIN_{i:02d}" for i in range(1, 21)]
    addon_skus = [f"SKU_ADDON_{i:02d}" for i in range(1, 16)]

    rows = []
    for order_id in range(1, num_orders + 1):
        region = rng.choice(regions, p=[0.32, 0.30, 0.24, 0.14])
        primary_wh = local_hub[region]
        basket_size = rng.choice([2, 3], p=[0.75, 0.25])

        chosen_main = rng.choice(main_skus)
        rows.append((order_id, region, chosen_main, primary_wh, 4.20))

        for _ in range(basket_size - 1):
            if rng.random() < 0.65:
                sku = rng.choice(addon_skus)
                if primary_wh != "WH_MUM" and rng.random() < 0.55:
                    wh = "WH_MUM"
                    cost = 4.60
                else:
                    wh = primary_wh
                    cost = 0.80
            else:
                sku = rng.choice([s for s in main_skus if s != chosen_main])
                wh = primary_wh
                cost = 0.80

            rows.append((order_id, region, sku, wh, cost))

    return pd.DataFrame(
        rows,
        columns=["order_id", "region", "sku_id", "warehouse_id", "shipping_cost"],
    )


def run_analysis(df, seed=42):
    rng = np.random.default_rng(seed)

    order_stats = df.groupby(["order_id", "region"]).agg(
        warehouses_used=("warehouse_id", "nunique"),
        order_shipping=("shipping_cost", "sum"),
    )

    total_orders = len(order_stats)
    split_orders = (order_stats["warehouses_used"] > 1).sum()
    split_rate = (split_orders / total_orders) * 100
    total_spend = order_stats["order_shipping"].sum()

    print(f"Total Multi-Item Orders: {total_orders:,}")
    print(f"Split Orders: {split_orders:,} ({split_rate:.2f}%)")
    print(f"Total Shipping Spend: ${total_spend:,.2f}\n")

    merged = df.merge(df, on="order_id", suffixes=("_a", "_b"))
    split_pairs = merged[
        (merged["sku_id_a"] < merged["sku_id_b"])
        & (merged["warehouse_id_a"] != merged["warehouse_id_b"])
    ]

    top_pairs = (
        split_pairs.groupby(["sku_id_a", "sku_id_b"])
        .size()
        .reset_index(name="split_count")
        .sort_values("split_count", ascending=False)
        .head(5)
    )

    print("Top 5 Split-Causing SKU Pairs:")
    print(top_pairs.to_string(index=False))

    local_hub = {"North": "WH_DEL", "West": "WH_MUM", "South": "WH_BLR", "East": "WH_KOL"}
    sim_df = df.copy()
    is_addon = sim_df["sku_id"].str.startswith("SKU_ADDON_")
    was_split = sim_df["warehouse_id"] != sim_df["region"].map(local_hub)

    rebalanced = is_addon & was_split & (rng.random(len(sim_df)) < 0.80)
    sim_df.loc[rebalanced, "warehouse_id"] = sim_df.loc[rebalanced, "region"].map(local_hub)
    sim_df.loc[rebalanced, "shipping_cost"] = 0.80

    new_stats = sim_df.groupby("order_id").agg(
        warehouses_used=("warehouse_id", "nunique"),
        order_shipping=("shipping_cost", "sum"),
    )

    new_split_rate = ((new_stats["warehouses_used"] > 1).sum() / total_orders) * 100
    savings = total_spend - new_stats["order_shipping"].sum()

    print(f"\nNew Split Rate After Rebalancing: {new_split_rate:.2f}%")
    print(f"Estimated Shipping Saved: ${savings:,.2f} per 15k orders")


if __name__ == "__main__":
    orders = generate_orders()
    run_analysis(orders)