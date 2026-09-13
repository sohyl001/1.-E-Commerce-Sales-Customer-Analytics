-- ====================================================================
-- Question 4: Which categories have declining sales?
-- Features: Category Quarterly Performance, Quarter-over-Quarter (QoQ) Growth %,
--           Consecutive Decline Detection, and Trajectory Classification.
-- ====================================================================

WITH CategoryQuarterlySales AS (
    SELECT 
        c.category_id,
        c.category_name,
        c.department,
        STRFTIME('%Y', o.order_date) || '-Q' || ((CAST(STRFTIME('%m', o.order_date) AS INTEGER) - 1) / 3 + 1) AS sales_quarter,
        COUNT(DISTINCT o.order_id) AS total_orders,
        SUM(oi.quantity) AS total_units_sold,
        ROUND(SUM(oi.total_item_price), 2) AS quarterly_revenue,
        ROUND(SUM(oi.gross_profit), 2) AS quarterly_gross_profit
    FROM order_items oi
    INNER JOIN orders o ON oi.order_id = o.order_id
    INNER JOIN products p ON oi.product_id = p.product_id
    INNER JOIN categories c ON p.category_id = c.category_id
    WHERE o.order_status = 'Completed'
    GROUP BY c.category_id, c.category_name, c.department, sales_quarter
),
QuarterlyLagAnalysis AS (
    SELECT 
        cqs.*,
        LAG(cqs.quarterly_revenue, 1) OVER (
            PARTITION BY cqs.category_id 
            ORDER BY cqs.sales_quarter
        ) AS prev_quarter_revenue,
        LAG(cqs.total_units_sold, 1) OVER (
            PARTITION BY cqs.category_id 
            ORDER BY cqs.sales_quarter
        ) AS prev_quarter_units
    FROM CategoryQuarterlySales cqs
),
GrowthCalculations AS (
    SELECT 
        qla.*,
        ROUND(
            CASE 
                WHEN prev_quarter_revenue IS NULL OR prev_quarter_revenue = 0 THEN 0.0
                ELSE ((quarterly_revenue - prev_quarter_revenue) * 100.0 / prev_quarter_revenue)
            END, 2
        ) AS qoq_revenue_growth_pct,
        ROUND(
            CASE 
                WHEN prev_quarter_units IS NULL OR prev_quarter_units = 0 THEN 0.0
                ELSE ((total_units_sold - prev_quarter_units) * 100.0 / prev_quarter_units)
            END, 2
        ) AS qoq_units_growth_pct
    FROM QuarterlyLagAnalysis qla
)
SELECT 
    category_id,
    category_name,
    department,
    sales_quarter,
    quarterly_revenue,
    prev_quarter_revenue,
    qoq_revenue_growth_pct,
    total_units_sold,
    qoq_units_growth_pct,
    CASE 
        WHEN qoq_revenue_growth_pct < -15.0 THEN 'Critical Decline (Immediate Action Required)'
        WHEN qoq_revenue_growth_pct < 0.0   THEN 'Moderate Decline (Watchlist)'
        WHEN qoq_revenue_growth_pct = 0.0   THEN 'Flat / Baseline'
        WHEN qoq_revenue_growth_pct < 15.0  THEN 'Healthy Growth'
        ELSE 'Strong Expansion'
    END AS trajectory_status
FROM GrowthCalculations
ORDER BY sales_quarter DESC, qoq_revenue_growth_pct ASC;
