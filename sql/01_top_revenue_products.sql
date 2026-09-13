-- ====================================================================
-- Question 1: Which products generate the most revenue?
-- Features: Total Gross Revenue, Units Sold, Net Profit, Margin %,
--           and Pareto Cumulative % (80/20 rule identification).
-- ====================================================================

WITH ProductMetrics AS (
    SELECT 
        p.product_id,
        p.product_name,
        c.category_name,
        c.department,
        p.unit_price,
        p.unit_cost,
        COUNT(DISTINCT oi.order_id) AS total_orders,
        SUM(oi.quantity) AS units_sold,
        ROUND(SUM(oi.total_item_price), 2) AS total_revenue,
        ROUND(SUM(oi.gross_profit), 2) AS total_gross_profit,
        ROUND((SUM(oi.gross_profit) * 100.0 / NULLIF(SUM(oi.total_item_price), 0)), 2) AS profit_margin_pct
    FROM order_items oi
    INNER JOIN orders o ON oi.order_id = o.order_id
    INNER JOIN products p ON oi.product_id = p.product_id
    INNER JOIN categories c ON p.category_id = c.category_id
    WHERE o.order_status = 'Completed'
    GROUP BY p.product_id, p.product_name, c.category_name, c.department, p.unit_price, p.unit_cost
),
TotalStoreRevenue AS (
    SELECT SUM(total_revenue) AS grand_total_revenue FROM ProductMetrics
),
RankedProducts AS (
    SELECT 
        pm.*,
        RANK() OVER (ORDER BY pm.total_revenue DESC) AS revenue_rank,
        ROUND(pm.total_revenue * 100.0 / tsr.grand_total_revenue, 2) AS pct_of_total_revenue,
        ROUND(
            SUM(pm.total_revenue) OVER (
                ORDER BY pm.total_revenue DESC 
                ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
            ) * 100.0 / tsr.grand_total_revenue, 
            2
        ) AS cumulative_revenue_pct
    FROM ProductMetrics pm
    CROSS JOIN TotalStoreRevenue tsr
)
SELECT 
    revenue_rank,
    product_id,
    product_name,
    category_name,
    department,
    units_sold,
    total_orders,
    total_revenue,
    total_gross_profit,
    profit_margin_pct,
    pct_of_total_revenue,
    cumulative_revenue_pct,
    CASE 
        WHEN cumulative_revenue_pct <= 80.0 THEN 'Core 80% Driver (Pareto Top Tier)'
        ELSE 'Long Tail Product'
    END AS pareto_classification
FROM RankedProducts
ORDER BY total_revenue DESC;
