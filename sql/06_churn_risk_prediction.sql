-- ====================================================================
-- Question 6: Which customers are likely to stop purchasing?
-- Features: Churn Risk Scoring, Purchase Cadence Latency,
--           High-Value At-Risk Identification, Retention Priority.
-- ====================================================================

WITH SnapshotDate AS (
    SELECT DATE(MAX(order_date), '+1 day') AS ref_date FROM orders WHERE order_status = 'Completed'
),
CustomerOrderStats AS (
    SELECT 
        c.customer_id,
        c.first_name || ' ' || c.last_name AS customer_name,
        c.email,
        c.customer_tier,
        c.acquisition_channel,
        COUNT(DISTINCT o.order_id) AS total_orders,
        ROUND(SUM(o.total_amount), 2) AS total_lifetime_spend,
        MIN(o.order_date) AS first_order_date,
        MAX(o.order_date) AS last_order_date,
        -- Days inactive since last order
        CAST(ROUND(JULIANDAY(s.ref_date) - JULIANDAY(MAX(o.order_date))) AS INTEGER) AS days_since_last_order,
        -- Total customer tenure in days
        CAST(ROUND(JULIANDAY(MAX(o.order_date)) - JULIANDAY(MIN(o.order_date))) AS INTEGER) AS active_tenure_days
    FROM customers c
    INNER JOIN orders o ON c.customer_id = o.customer_id
    CROSS JOIN SnapshotDate s
    WHERE o.order_status = 'Completed'
    GROUP BY c.customer_id, c.first_name, c.last_name, c.email, c.customer_tier, c.acquisition_channel, s.ref_date
),
CustomerCadence AS (
    SELECT 
        *,
        CASE 
            WHEN total_orders > 1 THEN ROUND(active_tenure_days * 1.0 / (total_orders - 1), 1)
            ELSE 60.0 -- Baseline assumed cycle for single-purchase customers
        END AS avg_days_between_orders
    FROM CustomerOrderStats
),
ChurnScoring AS (
    SELECT 
        *,
        -- Latency ratio: How many multiples of their normal cycle have passed since last purchase
        ROUND(days_since_last_order * 1.0 / NULLIF(avg_days_between_orders, 0), 2) AS cadence_latency_multiplier,
        CASE 
            -- VIP / High spenders inactive beyond 2.5x normal cycle
            WHEN days_since_last_order > 180 AND total_lifetime_spend >= 500 THEN 'Critical Churn Risk (High Value At-Risk)'
            WHEN days_since_last_order > 180 THEN 'Dormant / Churned'
            WHEN days_since_last_order > 90 AND (days_since_last_order >= avg_days_between_orders * 1.8) THEN 'High Churn Risk'
            WHEN days_since_last_order > 60 AND (days_since_last_order >= avg_days_between_orders * 1.2) THEN 'Medium Churn Risk (Cooling Down)'
            ELSE 'Active & Healthy'
        END AS churn_risk_tier,
        CASE 
            WHEN total_lifetime_spend >= 500 AND days_since_last_order > 90 THEN 'Tier 1: VIP Personal Win-Back Campaign ($25 Gift / Concierge)'
            WHEN total_orders > 1 AND days_since_last_order > 90 THEN 'Tier 2: Targeted Re-engagement Email (15% Discount Promo)'
            WHEN total_orders = 1 AND days_since_last_order > 60 THEN 'Tier 3: 2nd Order Onboarding Sequence (Free Shipping)'
            ELSE 'Maintain Standard Marketing Automation'
        END AS retention_action
    FROM CustomerCadence
)
SELECT 
    customer_id,
    customer_name,
    email,
    customer_tier,
    acquisition_channel,
    total_orders,
    total_lifetime_spend,
    days_since_last_order,
    avg_days_between_orders,
    cadence_latency_multiplier,
    churn_risk_tier,
    retention_action
FROM ChurnScoring
WHERE churn_risk_tier IN ('Critical Churn Risk (High Value At-Risk)', 'High Churn Risk', 'Medium Churn Risk (Cooling Down)')
ORDER BY 
    CASE churn_risk_tier 
        WHEN 'Critical Churn Risk (High Value At-Risk)' THEN 1 
        WHEN 'High Churn Risk' THEN 2 
        ELSE 3 
    END, 
    total_lifetime_spend DESC;
