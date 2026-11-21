# Warehouse Split-Shipment Analysis

When a customer orders multiple items in one checkout, the order gets split into separate packages if one of the items is out of stock at their nearest warehouse. Shipping two boxes for a single order doubles the packaging and last-mile delivery cost.

I built this project to measure how often multi-item orders split, find which product pairs cause most of the splits, and test how much shipping cost drops if we keep safety stock of those items in regional hubs.

## Files
- `queries.sql` - SQL queries to check regional split rates and find SKU pairs frequently shipped from different warehouses.
- `analyze_splits.py` - Simulates 15,000 multi-item orders, finds the top split-causing item pairs, and tests regional stock rebalancing.
- `requirements.txt` - Python libraries needed (`pandas` and `numpy`).

## What I found
- Around 26% of multi-item orders were split across two or more warehouses.
- Just 15 fast-moving add-on items caused over 40% of all split shipments because they were only stocked in the Mumbai hub (`WH_MUM`).
- Keeping stock of those 15 add-on items in regional warehouses (`WH_DEL`, `WH_BLR`, `WH_KOL`) reduced the split rate by about 28% and saved significant shipping cost.

## Run locally

    pip install -r requirements.txt
    python analyze_splits.py