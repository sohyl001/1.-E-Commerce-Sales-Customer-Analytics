-- ====================================================================
-- Question 3: What is the monthly sales trend?
-- Features: Monthly Revenue, Order Volume, Unique Customers, MoM Growth %,
--           3-Month Rolling Average Revenue, and Cumulative Running Total.
-- ====================================================================

WITH MonthlyOrders AS (
    SELECT 
        STRFTIME('%Y-%m', order_date) AS sales_month,
        STRFTIME('%Y', order_date) AS sales_year,
        STRFTIME('%m', order_date) AS month_number,
        COUNT(DISTINCT order_id) AS total_orders,
        COUNT(DISTINCT customer_id) AS active_customers,
        ROUND(SUM(total_amount), 2) AS monthly_revenue,
        ROUND(AVG(total_amount), 2) AS monthly_aov
    FROM orders
    WHERE order_status = 'Completed'
    GROUP BY STRFTIME('%Y-%m', order_date), STRFTIME('%Y', order_date), STRFTIME('%m', order_date)
),
MonthlyItems AS (
    SELECT 
        STRFTIME('%Y-%m', o.order_date) AS sales_month,
        SUM(oi.quantity) AS total_units_sold,
        ROUND(SUM(oi.gross_profit), 2) AS monthly_gross_profit
    FROM order_items oi
    INNER JOIN orders o ON oi.order_id = o.order_id
    WHERE o.order_status = 'Completed'
    GROUP BY STRFTIME('%Y-%m', o.order_date)
),
MonthlyAggregation AS (
    SELECT 
        mo.sales_month,
        mo.sales_year,
        mo.month_number,
        mo.total_orders,
        mo.active_customers,
        mi.total_units_sold,
        mo.monthly_revenue,
        mi.monthly_gross_profit,
        mo.monthly_aov
    FROM MonthlyOrders mo
    INNER JOIN MonthlyItems mi ON mo.sales_month = mi.sales_month
),
MonthlyWithLag AS (
    SELECT 
        ma.*,
        LAG(monthly_revenue, 1) OVER (ORDER BY sales_month) AS prev_month_revenue,
        LAG(total_orders, 1) OVER (ORDER BY sales_month) AS prev_month_orders,
        ROUND(
            AVG(monthly_revenue) OVER (
                ORDER BY sales_month 
                ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
            ), 2
        ) AS rolling_3mo_avg_revenue,
        ROUND(
            SUM(monthly_revenue) OVER (
                ORDER BY sales_month 
                ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
            ), 2
        ) AS cumulative_running_revenue
    FROM MonthlyAggregation ma
)
SELECT 
    sales_month,
    sales_year,
    month_number,
    total_orders,
    active_customers,
    total_units_sold,
    monthly_revenue,
    monthly_gross_profit,
    monthly_aov,
    prev_month_revenue,
    ROUND(
        CASE 
            WHEN prev_month_revenue IS NULL OR prev_month_revenue = 0 THEN 0.0
            ELSE ((monthly_revenue - prev_month_revenue) * 100.0 / prev_month_revenue)
        END, 2
    ) AS mom_revenue_growth_pct,
    ROUND(
        CASE 
            WHEN prev_month_orders IS NULL OR prev_month_orders = 0 THEN 0.0
            ELSE ((total_orders - prev_month_orders) * 100.0 / prev_month_orders)
        END, 2
    ) AS mom_order_growth_pct,
    rolling_3mo_avg_revenue,
    cumulative_running_revenue
FROM MonthlyWithLag
ORDER BY sales_month ASC;
