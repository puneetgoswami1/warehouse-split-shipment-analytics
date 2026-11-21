-- 1. Split-shipment rate by region for multi-item orders
WITH order_summary AS (
    SELECT
        order_id,
        customer_region,
        COUNT(DISTINCT sku_id) AS total_items,
        COUNT(DISTINCT warehouse_id) AS warehouses_used,
        SUM(shipping_cost) AS order_shipping_cost
    FROM order_items
    GROUP BY order_id, customer_region
    HAVING COUNT(DISTINCT sku_id) > 1
)
SELECT
    customer_region,
    COUNT(*) AS multi_item_orders,
    SUM(CASE WHEN warehouses_used > 1 THEN 1 ELSE 0 END) AS split_orders,
    ROUND(
        100.0 * SUM(CASE WHEN warehouses_used > 1 THEN 1 ELSE 0 END) / COUNT(*),
        2
    ) AS split_rate_pct,
    ROUND(AVG(order_shipping_cost), 2) AS avg_shipping_cost
FROM order_summary
GROUP BY customer_region
ORDER BY split_rate_pct DESC;


-- 2. Top 10 SKU pairs bought together but shipped from separate warehouses
SELECT
    a.sku_id AS primary_sku,
    b.sku_id AS paired_sku,
    COUNT(DISTINCT a.order_id) AS split_order_count,
    ROUND(SUM(b.shipping_cost), 2) AS extra_shipping_cost
FROM order_items a
JOIN order_items b
    ON a.order_id = b.order_id
    AND a.sku_id < b.sku_id
WHERE a.warehouse_id <> b.warehouse_id
GROUP BY a.sku_id, b.sku_id
ORDER BY split_order_count DESC
LIMIT 10;