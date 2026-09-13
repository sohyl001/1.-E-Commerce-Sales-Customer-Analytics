"""
Customer Analytics & RFM Segmentation Engine.
Answers Question 2: Which customers are most valuable?
Computes Recency, Frequency, Monetary (RFM) segmentation,
NTILE scoring, Customer Lifetime Value (CLV), and Customer Tier distribution.
"""

import sqlite3
import pandas as pd
import numpy as np
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DB_PATH = BASE_DIR / "data" / "database" / "ecommerce_analytics.db"
PROCESSED_DIR = BASE_DIR / "data" / "processed"
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


def analyze_customer_rfm():
    """Computes comprehensive RFM segmentation and customer valuation."""
    conn = sqlite3.connect(str(DB_PATH))

    # Pull customer order summary
    query = """
    WITH ReferenceDate AS (
        SELECT DATE(MAX(order_date), '+1 day') AS snapshot_date FROM orders WHERE order_status = 'Completed'
    )
    SELECT 
        c.customer_id,
        c.first_name || ' ' || c.last_name AS customer_name,
        c.email,
        c.city,
        c.state,
        c.signup_date,
        c.acquisition_channel,
        c.customer_tier,
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
    GROUP BY c.customer_id, c.first_name, c.last_name, c.email, c.city, c.state, c.signup_date, c.acquisition_channel, c.customer_tier, ref.snapshot_date
    ORDER BY total_lifetime_spend DESC;
    """
    df = pd.read_sql_query(query, conn)
    conn.close()

    if df.empty:
        print("[Customer Analytics] No customer records found.")
        return df

    # RFM Quintile Scoring (1 to 5)
    # Recency: Lower days = higher score (inverted)
    df["r_score"] = pd.qcut(df["recency_days"], q=5, labels=[5, 4, 3, 2, 1]).astype(int)
    # Frequency: Higher orders = higher score (use rank method to handle ties)
    df["f_score"] = pd.qcut(df["total_orders"].rank(method="first"), q=5, labels=[1, 2, 3, 4, 5]).astype(int)
    # Monetary: Higher spend = higher score
    df["m_score"] = pd.qcut(df["total_lifetime_spend"].rank(method="first"), q=5, labels=[1, 2, 3, 4, 5]).astype(int)

    df["rfm_score_combined"] = df["r_score"].astype(str) + df["f_score"].astype(str) + df["m_score"].astype(str)
    df["rfm_index_numeric"] = df["r_score"] * 100 + df["f_score"] * 10 + df["m_score"]

    def assign_rfm_segment(row):
        r, f, m = row["r_score"], row["f_score"], row["m_score"]
        if r >= 4 and f >= 4 and m >= 4:
            return "Champions (VIP)"
        elif r >= 3 and f >= 3 and m >= 3:
            return "Loyal Customers"
        elif r >= 4 and f <= 2 and m >= 3:
            return "Potential Loyalists"
        elif r >= 4 and f == 1:
            return "New Recent Customers"
        elif r <= 2 and f >= 3 and m >= 3:
            return "At Risk VIPs (High Value)"
        elif r <= 2 and f <= 2 and m >= 3:
            return "About to Sleep"
        elif r <= 2 and f <= 2 and m <= 2:
            return "Lost / Inactive"
        else:
            return "Promising / Needs Attention"

    df["rfm_segment"] = df.apply(assign_rfm_segment, axis=1)
    df["monetary_rank"] = df["total_lifetime_spend"].rank(ascending=False, method="dense").astype(int)

    # Save detailed customer level file
    out_csv = PROCESSED_DIR / "rfm_customer_segments.csv"
    df.to_csv(out_csv, index=False)
    print(f"[Customer Analytics] Generated {out_csv.name} ({len(df)} customers)")

    # Aggregate Segment Summary for Executive Reporting
    segment_summary = df.groupby("rfm_segment").agg(
        customer_count=("customer_id", "count"),
        total_revenue=("total_lifetime_spend", "sum"),
        avg_lifetime_spend=("total_lifetime_spend", "mean"),
        avg_aov=("customer_avg_order_value", "mean"),
        avg_recency_days=("recency_days", "mean"),
        avg_order_count=("total_orders", "mean")
    ).reset_index()

    segment_summary["pct_of_customers"] = (
        segment_summary["customer_count"] / len(df) * 100
    ).round(2)
    segment_summary["pct_of_revenue"] = (
        segment_summary["total_revenue"] / df["total_lifetime_spend"].sum() * 100
    ).round(2)
    segment_summary = segment_summary.sort_values(by="total_revenue", ascending=False)

    summary_csv = PROCESSED_DIR / "rfm_segment_summary.csv"
    segment_summary.to_csv(summary_csv, index=False)
    print(f"[Customer Analytics] Generated {summary_csv.name}")

    return df, segment_summary


if __name__ == "__main__":
    analyze_customer_rfm()
