-- ====================================================================
-- Question 5: What is the average order value (AOV)?
-- Features: Overall Store AOV, AOV by Sales Channel, Payment Method,
--           Customer Tier, and Order Size Distribution Buckets.
-- ====================================================================

-- 1. Overall Executive AOV Summary
SELECT 
    'Overall Store Metric' AS metric_scope,
    COUNT(DISTINCT order_id) AS total_orders,
    ROUND(SUM(total_amount), 2) AS total_revenue,
    ROUND(AVG(total_amount), 2) AS average_order_value,
    ROUND(MIN(total_amount), 2) AS min_order_value,
    ROUND(MAX(total_amount), 2) AS max_order_value
FROM orders
WHERE order_status = 'Completed';

-- 2. AOV by Sales Channel & Payment Method
SELECT 
    sales_channel,
    payment_method,
    COUNT(DISTINCT order_id) AS total_orders,
    ROUND(SUM(total_amount), 2) AS total_revenue,
    ROUND(AVG(total_amount), 2) AS channel_aov,
    ROUND(SUM(total_amount) * 100.0 / SUM(SUM(total_amount)) OVER(), 2) AS revenue_share_pct
FROM orders
WHERE order_status = 'Completed'
GROUP BY sales_channel, payment_method
ORDER BY channel_aov DESC;

-- 3. Order Basket Size Value Distribution Buckets
WITH OrderBins AS (
    SELECT 
        order_id,
        total_amount,
        CASE 
            WHEN total_amount < 50.0  THEN '1. Under $50 (Micro)'
            WHEN total_amount < 100.0 THEN '2. $50 - $99.99 (Standard)'
            WHEN total_amount < 250.0 THEN '3. $100 - $249.99 (Medium)'
            WHEN total_amount < 500.0 THEN '4. $250 - $499.99 (Large)'
            ELSE '5. $500+ (VIP / Bulk)'
        END AS order_value_tier
    FROM orders
    WHERE order_status = 'Completed'
)
SELECT 
    order_value_tier,
    COUNT(order_id) AS order_count,
    ROUND(COUNT(order_id) * 100.0 / (SELECT COUNT(*) FROM OrderBins), 2) AS order_percentage,
    ROUND(SUM(total_amount), 2) AS tier_total_revenue,
    ROUND(AVG(total_amount), 2) AS tier_aov
FROM OrderBins
GROUP BY order_value_tier
ORDER BY order_value_tier ASC;
