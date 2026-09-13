-- ====================================================================
-- Question 2: Which customers are most valuable?
-- Features: RFM (Recency, Frequency, Monetary) Customer Segmentation,
--           NTILE quintiles, Customer Lifetime Value (CLV), and Tiering.
-- ====================================================================

WITH ReferenceDate AS (
    -- Anchor snapshot date to the maximum order date in the dataset
    SELECT DATE(MAX(order_date), '+1 day') AS snapshot_date FROM orders WHERE order_status = 'Completed'
),
CustomerAggregates AS (
    SELECT 
        c.customer_id,
        c.first_name || ' ' || c.last_name AS customer_name,
        c.email,
        c.city,
        c.state,
        c.signup_date,
        c.acquisition_channel,
        COUNT(DISTINCT o.order_id) AS total_orders,
        ROUND(SUM(o.total_amount), 2) AS total_lifetime_spend,
        ROUND(AVG(o.total_amount), 2) AS customer_avg_order_value,
        MAX(o.order_date) AS last_order_date,
        MIN(o.order_date) AS first_order_date,
        CAST(ROUND(JULIANDAY(ref.snapshot_date) - JULIANDAY(MAX(o.order_date))) AS INTEGER) AS recency_days
    FROM customers c
    INNER JOIN orders o ON c.customer_id = o.customer_id
    CROSS JOIN ReferenceDate ref
    WHERE o.order_status = 'Completed'
    GROUP BY c.customer_id, c.first_name, c.last_name, c.email, c.city, c.state, c.signup_date, c.acquisition_channel, ref.snapshot_date
),
RFM_Quintiles AS (
    SELECT 
        ca.*,
        -- Recency: Lower days = higher score (5 = most recent, 1 = longest inactive)
        NTILE(5) OVER (ORDER BY recency_days DESC) AS r_score,
        -- Frequency: Higher orders = higher score (5 = most frequent)
        NTILE(5) OVER (ORDER BY total_orders ASC) AS f_score,
        -- Monetary: Higher spend = higher score (5 = highest spending)
        NTILE(5) OVER (ORDER BY total_lifetime_spend ASC) AS m_score,
        DENSE_RANK() OVER (ORDER BY total_lifetime_spend DESC) AS monetary_rank
    FROM CustomerAggregates ca
),
SegmentedCustomers AS (
    SELECT 
        *,
        (r_score * 100 + f_score * 10 + m_score) AS rfm_combined_score,
        ROUND((r_score + f_score + m_score) / 3.0, 2) AS rfm_average_score,
        CASE 
            WHEN r_score >= 4 AND f_score >= 4 AND m_score >= 4 THEN 'Champions'
            WHEN r_score >= 3 AND f_score >= 3 AND m_score >= 3 THEN 'Loyal Customers'
            WHEN r_score >= 4 AND f_score <= 2 AND m_score >= 3 THEN 'Potential Loyalists'
            WHEN r_score >= 4 AND f_score = 1 THEN 'New Recent Customers'
            WHEN r_score <= 2 AND f_score >= 3 AND m_score >= 3 THEN 'At Risk (High Spenders)'
            WHEN r_score <= 2 AND f_score <= 2 AND m_score >= 3 THEN 'About to Sleep'
            WHEN r_score <= 2 AND f_score <= 2 AND m_score <= 2 THEN 'Lost Customers'
            ELSE 'Promising / Needs Attention'
        END AS rfm_segment
    FROM RFM_Quintiles
)
SELECT 
    monetary_rank,
    customer_id,
    customer_name,
    email,
    state,
    acquisition_channel,
    total_orders,
    total_lifetime_spend,
    customer_avg_order_value,
    recency_days,
    r_score,
    f_score,
    m_score,
    rfm_combined_score,
    rfm_segment
FROM SegmentedCustomers
ORDER BY total_lifetime_spend DESC;
