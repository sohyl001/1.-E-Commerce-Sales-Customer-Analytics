"""
Sales Analytics Engine.
Solves Question 1 (Top Revenue Products & Pareto Analysis),
Question 3 (Monthly Sales Trends & Seasonality),
Question 4 (Declining Categories & Growth Momentum),
and Question 5 (Average Order Value across dimensions).
"""

import sqlite3
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DB_PATH = BASE_DIR / "data" / "database" / "ecommerce_analytics.db"
PROCESSED_DIR = BASE_DIR / "data" / "processed"
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


def get_db_connection():
    return sqlite3.connect(str(DB_PATH))


def analyze_top_revenue_products():
    """Question 1: Which products generate the most revenue? (Includes Pareto 80/20 analysis)"""
    conn = get_db_connection()
    query = """
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
    ORDER BY total_revenue DESC;
    """
    df = pd.read_sql_query(query, conn)
    conn.close()

    total_revenue = df["total_revenue"].sum()
    df["pct_of_total_revenue"] = (df["total_revenue"] / total_revenue * 100).round(2)
    df["cumulative_revenue_pct"] = (df["total_revenue"].cumsum() / total_revenue * 100).round(2)
    df["pareto_classification"] = df["cumulative_revenue_pct"].apply(
        lambda x: "Core 80% Driver (Pareto Top Tier)" if x <= 80.0 else "Long Tail Product"
    )

    out_csv = PROCESSED_DIR / "top_products_summary.csv"
    df.to_csv(out_csv, index=False)
    print(f"[Sales Analytics] Generated {out_csv.name} ({len(df)} products)")
    return df


def analyze_monthly_sales_trend():
    """Question 3: What is the monthly sales trend? (MoM growth & rolling averages)"""
    conn = get_db_connection()
    query = """
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
    )
    SELECT * FROM MonthlyAggregation
    ORDER BY sales_month ASC;
    """
    df = pd.read_sql_query(query, conn)
    conn.close()

    df["prev_month_revenue"] = df["monthly_revenue"].shift(1)
    df["mom_revenue_growth_pct"] = (
        (df["monthly_revenue"] - df["prev_month_revenue"]) / df["prev_month_revenue"] * 100
    ).round(2).fillna(0.0)

    df["rolling_3mo_avg_revenue"] = df["monthly_revenue"].rolling(window=3, min_periods=1).mean().round(2)
    df["cumulative_running_revenue"] = df["monthly_revenue"].cumsum().round(2)

    out_csv = PROCESSED_DIR / "monthly_sales_summary.csv"
    df.to_csv(out_csv, index=False)
    print(f"[Sales Analytics] Generated {out_csv.name} ({len(df)} months)")
    return df


def analyze_declining_categories():
    """Question 4: Which categories have declining sales? (QoQ momentum & status)"""
    conn = get_db_connection()
    query = """
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
    ORDER BY c.category_id, sales_quarter ASC;
    """
    df = pd.read_sql_query(query, conn)
    conn.close()

    df["prev_quarter_revenue"] = df.groupby("category_id")["quarterly_revenue"].shift(1)
    df["qoq_revenue_growth_pct"] = (
        (df["quarterly_revenue"] - df["prev_quarter_revenue"]) / df["prev_quarter_revenue"] * 100
    ).round(2).fillna(0.0)

    def classify_trajectory(growth):
        if growth < -15.0:
            return "Critical Decline (Immediate Action Required)"
        elif growth < 0.0:
            return "Moderate Decline (Watchlist)"
        elif growth == 0.0:
            return "Flat / Baseline"
        elif growth < 15.0:
            return "Healthy Growth"
        else:
            return "Strong Expansion"

    df["trajectory_status"] = df["qoq_revenue_growth_pct"].apply(classify_trajectory)

    out_csv = PROCESSED_DIR / "category_quarterly_momentum.csv"
    df.to_csv(out_csv, index=False)
    print(f"[Sales Analytics] Generated {out_csv.name} ({len(df)} category-quarters)")
    return df


def analyze_average_order_value():
    """Question 5: What is the average order value (AOV) across segments & channels?"""
    conn = get_db_connection()
    
    # 1. By Channel & Payment
    q_channel = """
    SELECT 
        sales_channel,
        payment_method,
        COUNT(DISTINCT order_id) AS total_orders,
        ROUND(SUM(total_amount), 2) AS total_revenue,
        ROUND(AVG(total_amount), 2) AS channel_aov
    FROM orders
    WHERE order_status = 'Completed'
    GROUP BY sales_channel, payment_method
    ORDER BY channel_aov DESC;
    """
    df_channel = pd.read_sql_query(q_channel, conn)
    out_ch = PROCESSED_DIR / "aov_by_channel_payment.csv"
    df_channel.to_csv(out_ch, index=False)

    # 2. Overall Summary
    q_overall = """
    SELECT 
        'Overall Store' AS metric_scope,
        COUNT(DISTINCT order_id) AS total_orders,
        ROUND(SUM(total_amount), 2) AS total_revenue,
        ROUND(AVG(total_amount), 2) AS average_order_value,
        ROUND(MIN(total_amount), 2) AS min_order_value,
        ROUND(MAX(total_amount), 2) AS max_order_value
    FROM orders
    WHERE order_status = 'Completed';
    """
    df_overall = pd.read_sql_query(q_overall, conn)
    out_ov = PROCESSED_DIR / "aov_overall_kpis.csv"
    df_overall.to_csv(out_ov, index=False)

    conn.close()
    print(f"[Sales Analytics] Generated {out_ch.name} and {out_ov.name}")
    return df_overall, df_channel


def run_all_sales_analytics():
    print("=== Running Sales Analytics Suite ===")
    analyze_top_revenue_products()
    analyze_monthly_sales_trend()
    analyze_declining_categories()
    analyze_average_order_value()
    print("=== Sales Analytics Suite Complete! ===")


if __name__ == "__main__":
    run_all_sales_analytics()
