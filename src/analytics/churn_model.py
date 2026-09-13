"""
Customer Churn Risk Scoring & Retention Engine.
Answers Question 6: Which customers are likely to stop purchasing?
Evaluates customer order history, expected repurchase interval (cadence),
recency latency, and assigns probabilistic churn risk scores and retention tactics.
"""

import sqlite3
import pandas as pd
import numpy as np
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DB_PATH = BASE_DIR / "data" / "database" / "ecommerce_analytics.db"
PROCESSED_DIR = BASE_DIR / "data" / "processed"
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


def calculate_churn_risk():
    """Identifies customers at risk of churn based on purchase latency and historical cadence."""
    conn = sqlite3.connect(str(DB_PATH))

    query = """
    WITH SnapshotDate AS (
        SELECT DATE(MAX(order_date), '+1 day') AS ref_date FROM orders WHERE order_status = 'Completed'
    )
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
        CAST(ROUND(JULIANDAY(s.ref_date) - JULIANDAY(MAX(o.order_date))) AS INTEGER) AS days_since_last_order,
        CAST(ROUND(JULIANDAY(MAX(o.order_date)) - JULIANDAY(MIN(o.order_date))) AS INTEGER) AS active_tenure_days
    FROM customers c
    INNER JOIN orders o ON c.customer_id = o.customer_id
    CROSS JOIN SnapshotDate s
    WHERE o.order_status = 'Completed'
    GROUP BY c.customer_id, c.first_name, c.last_name, c.email, c.customer_tier, c.acquisition_channel, s.ref_date;
    """
    df = pd.read_sql_query(query, conn)
    conn.close()

    if df.empty:
        print("[Churn Analytics] No records found.")
        return df

    # Calculate average repurchase cadence
    df["avg_days_between_orders"] = np.where(
        df["total_orders"] > 1,
        (df["active_tenure_days"] / (df["total_orders"] - 1)).round(1),
        60.0 # Standard benchmark for 1-time buyers
    )

    # Latency multiplier (how much past expected cycle)
    df["cadence_latency_multiplier"] = (
        df["days_since_last_order"] / df["avg_days_between_orders"].replace(0, 1)
    ).round(2)

    # Churn Risk Probability Score (0 - 100)
    # Factor 1: Latency multiplier (up to 60 pts)
    # Factor 2: Raw inactive days (up to 30 pts)
    # Factor 3: Single purchase vulnerability (+10 pts)
    def calculate_score(row):
        score = 0.0
        # Latency contribution
        mult = row["cadence_latency_multiplier"]
        if mult >= 3.0:
            score += 55.0
        elif mult >= 2.0:
            score += 40.0
        elif mult >= 1.3:
            score += 25.0
        elif mult >= 1.0:
            score += 10.0

        # Days inactive contribution
        days = row["days_since_last_order"]
        if days >= 180:
            score += 35.0
        elif days >= 120:
            score += 25.0
        elif days >= 90:
            score += 15.0
        elif days >= 60:
            score += 8.0

        # Single order penalty
        if row["total_orders"] == 1:
            score += 10.0

        return min(100.0, round(score, 1))

    df["churn_probability_score"] = df.apply(calculate_score, axis=1)

    # Tier Classification
    def assign_churn_tier(row):
        score = row["churn_probability_score"]
        spend = row["total_lifetime_spend"]
        days = row["days_since_last_order"]

        if score >= 75.0 and spend >= 500.0:
            return "Critical Churn Risk (High Value At-Risk)"
        elif score >= 75.0:
            return "High Churn Risk (Dormant / Churning)"
        elif score >= 45.0:
            return "Medium Churn Risk (Cooling Down)"
        else:
            return "Active & Healthy"

    df["churn_risk_tier"] = df.apply(assign_churn_tier, axis=1)

    # Actionable Retention Recommendation
    def assign_retention_action(row):
        tier = row["churn_risk_tier"]
        spend = row["total_lifetime_spend"]
        orders = row["total_orders"]

        if "Critical" in tier or spend >= 800.0:
            return "Tier 1: High-Priority VIP Winback ($30 Loyalty Credit + Personal Email)"
        elif tier == "High Churn Risk (Dormant / Churning)":
            if orders > 1:
                return "Tier 2: Targeted Re-engagement Campaign (20% Promo Code)"
            else:
                return "Tier 3: First-to-Second Order Conversion Offer (Free Shipping + Free Gift)"
        elif tier == "Medium Churn Risk (Cooling Down)":
            return "Tier 4: Automated Replenishment Reminder & New Arrivals Newsletter"
        else:
            return "Standard Loyalty Points & Regular Marketing Flow"

    df["retention_action"] = df.apply(assign_retention_action, axis=1)

    # Sort so most critical at-risk high spenders appear at top
    df = df.sort_values(
        by=["churn_probability_score", "total_lifetime_spend"],
        ascending=[False, False]
    )

    out_csv = PROCESSED_DIR / "churn_risk_analysis.csv"
    df.to_csv(out_csv, index=False)
    print(f"[Churn Analytics] Generated {out_csv.name} ({len(df)} customer churn profiles)")

    # High-Risk Watchlist subset for fast action
    watchlist = df[df["churn_risk_tier"].str.contains("Risk|Dormant")]
    watch_csv = PROCESSED_DIR / "churn_watchlist_actionable.csv"
    watchlist.to_csv(watch_csv, index=False)
    print(f"[Churn Analytics] Generated {watch_csv.name} ({len(watchlist)} at-risk customers)")

    return df


if __name__ == "__main__":
    calculate_churn_risk()
