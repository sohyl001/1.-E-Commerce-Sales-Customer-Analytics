"""
Master ETL and Analytics Pipeline.
Orchestrates:
1. Data Generation & Database Seeding (if not already seeded)
2. Question 1: Product Revenue & Pareto Analysis
3. Question 2: Customer RFM Segmentation
4. Question 3: Monthly Sales Trends & Seasonality
5. Question 4: Category Momentum & Decline Analysis
6. Question 5: Average Order Value Dimensions
7. Question 6: Customer Churn Risk Modeling & Retention Watchlist
"""

import os
import sys
import time
from pathlib import Path

# Ensure UTF-8 output on Windows console
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Add src and project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR / "src"))
sys.path.append(str(BASE_DIR))

from data_generator import generate_all_data
from analytics.sales_analytics import run_all_sales_analytics
from analytics.customer_analytics import analyze_customer_rfm
from analytics.churn_model import calculate_churn_risk
from utils.db_helper import DB_PATH, run_query


def run_full_pipeline(force_regenerate=False):
    start_time = time.time()
    print("====================================================================")
    print("[PIPELINE] STARTING E-COMMERCE SALES & CUSTOMER ANALYTICS ETL")
    print("====================================================================")

    # Step 1: Check Database & Raw Data
    if not DB_PATH.exists() or force_regenerate:
        print("\n[Step 1/3] Database not detected or force flag set. Generating synthetic transactions...")
        generate_all_data()
    else:
        print(f"\n[Step 1/3] Existing SQLite database detected at {DB_PATH}.")
        order_count = run_query("SELECT COUNT(*) as cnt FROM orders;")[0]["cnt"]
        print(f"Verified {order_count:,} orders in database.")

    # Step 2: Run Analytical Modules
    print("\n[Step 2/3] Executing Analytics Engine...")
    print("--> Processing Sales Analytics (Questions 1, 3, 4, 5)...")
    run_all_sales_analytics()

    print("\n--> Processing Customer Valuation & RFM Segmentation (Question 2)...")
    analyze_customer_rfm()

    print("\n--> Processing Customer Churn Prediction & Risk Watchlist (Question 6)...")
    calculate_churn_risk()

    # Step 3: Sync Dashboard & Excel Assets
    print("\n[Step 3/4] Exporting Web Dashboard Payload & Master Excel Workbook...")
    export_dashboard_payload()
    
    from excel.export_excel_summary import export_master_workbook
    export_master_workbook()

    # Step 4: Verification Summary
    print("\n[Step 4/4] Pipeline Execution Summary...")
    processed_dir = Path(__file__).resolve().parent.parent / "data" / "processed"
    files = list(processed_dir.glob("*.csv"))
    print(f"Successfully generated {len(files)} analytical data artifacts in data/processed/:")
    for f in sorted(files):
        line_count = sum(1 for _ in open(f, encoding="utf-8")) - 1
        print(f"  [OK] {f.name:<32} ({line_count:>6,} rows)")

    elapsed = round(time.time() - start_time, 2)
    print("\n====================================================================")
    print(f"[SUCCESS] ALL PIPELINES, DASHBOARD & EXCEL SYNCED IN {elapsed}s")
    print("====================================================================")


def export_dashboard_payload():
    """Compiles processed analytics into dashboard/data.js for standalone browser visualization."""
    import json
    import pandas as pd

    base_dir = Path(__file__).resolve().parent.parent
    pdir = base_dir / "data" / "processed"

    df_prod = pd.read_csv(pdir / "top_products_summary.csv")
    df_month = pd.read_csv(pdir / "monthly_sales_summary.csv")
    df_cat = pd.read_csv(pdir / "category_quarterly_momentum.csv")
    df_rfm_summary = pd.read_csv(pdir / "rfm_segment_summary.csv")
    df_rfm_cust = pd.read_csv(pdir / "rfm_customer_segments.csv")
    df_churn = pd.read_csv(pdir / "churn_watchlist_actionable.csv")
    df_aov_channel = pd.read_csv(pdir / "aov_by_channel_payment.csv")

    total_revenue = float(df_month["monthly_revenue"].sum())
    total_profit = float(df_prod["total_gross_profit"].sum())
    total_orders = int(df_month["total_orders"].sum())
    aov = round(total_revenue / total_orders, 2)
    profit_margin = round((total_profit / float(df_prod["total_revenue"].sum())) * 100, 1)

    data = {
        "kpis": {
            "total_revenue": total_revenue,
            "total_profit": total_profit,
            "profit_margin": profit_margin,
            "total_orders": total_orders,
            "aov": aov,
            "total_customers": int(df_rfm_summary["customer_count"].sum()),
            "at_risk_count": len(df_churn),
            "at_risk_spend": float(df_churn["total_lifetime_spend"].sum())
        },
        "top_products": df_prod.head(15).to_dict(orient="records"),
        "monthly_trend": df_month.to_dict(orient="records"),
        "category_momentum": df_cat.tail(48).to_dict(orient="records"),
        "rfm_summary": df_rfm_summary.to_dict(orient="records"),
        "top_customers": df_rfm_cust.head(25).to_dict(orient="records"),
        "churn_watchlist": df_churn.head(50).to_dict(orient="records"),
        "aov_channel": df_aov_channel.to_dict(orient="records")
    }

    out_js = base_dir / "dashboard" / "data.js"
    with open(out_js, "w", encoding="utf-8") as f:
        f.write("const ANALYTICS_DATA = " + json.dumps(data, indent=2) + ";\n")
    print(f"[Dashboard Sync] Updated {out_js.name} with live metrics.")


if __name__ == "__main__":
    run_full_pipeline(force_regenerate=True)
