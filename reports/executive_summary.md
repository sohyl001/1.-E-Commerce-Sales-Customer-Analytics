# Executive Business Intelligence & Analytics Report
**Project**: E-Commerce Sales & Customer Analytics System  
**Prepared For**: Commercial Leadership, Operations & Marketing Executives  
**Period Analyzed**: 2023 – 2026 (Multi-Year Retail Lifecycle)  

---

## 1. Executive Commercial Summary

| Metric Scope | Core Metric | Portfolio Value | Strategic Interpretation |
| :--- | :--- | :--- | :--- |
| **Top-Line Scale** | Total Gross Revenue | **$4.12M+** | Strong multi-year expansion across 10,661 completed orders (12,067 total orders) |
| **Profitability** | Gross Margin % | **56.5%** | Healthy unit economics driven by high-value electronics and consumer products |
| **Transaction Economics**| Average Order Value (AOV) | **$386.91** | Robust basket economics; elevated significantly by Mobile App and BNPL channels |
| **Customer Base** | Unique Customer Accounts | **2,442 Active** | 64.2% repeat purchase rate across customer lifecycle |
| **Revenue At-Risk** | Churn Exposure | **$1.73M** | Total lifetime value residing in cooling-down and high-risk accounts |

---

## 2. Deep Dive: Answering The 6 Core Business Questions

### Question 1: Which products generate the most revenue?
* **Pareto 80/20 Distribution Confirmed**: The top **10 product SKUs (20.4% of catalog)** generate **78.6% of total commercial gross revenue**.
* **Top Revenue Drivers**:
  1. `PRD-0005`: **Zenith Creator 16-inch Laptop** — Over $780,000 revenue (Gross Margin: 47.3%)
  2. `PRD-0001`: **Aura Pro Max 5G Smartphone** — Over $420,000 revenue (Gross Margin: 53.3%)
  3. `PRD-0006`: **UltraBook Air 14-inch Laptop** — Over $380,000 revenue (Gross Margin: 52.7%)
  4. `PRD-0007`: **CurveVision 34-inch Ultrawide 4K Monitor** — Over $210,000 revenue
  5. `PRD-0026`: **BaristaPro Italian Espresso Machine** — Over $170,000 revenue
* **Long Tail Opportunity**: Accessories (such as screen protectors, charging pads, and apparel basics) exhibit high volume (1,200+ units) and margins (>80%), making them ideal cross-sell and basket add-ons.

---

### Question 2: Which customers are most valuable?
* **RFM Segmentation Findings**:
  * **Champions (VIP Cohort)**: Comprise only **8.5% of accounts** but generate **34.2% of total storewide revenue**, averaging $4,200+ in lifetime spend with an average of 14 orders.
  * **Loyal Customers**: 16.4% of accounts, contributing 26.8% of revenue with steady repurchase behavior (5-9 orders).
  * **At-Risk VIPs**: 6.2% of accounts who historically generated $1,500+ spend but haven't placed an order in over 90 days.
* **Strategic Recommendation**: Establish an exclusive VIP tier ("Founder's Circle") offering concierge customer support, early product drops, and customized loyalty perks.

---

### Question 3: What is the monthly sales trend?
* **Seasonal Surges**: Pronounced peak spikes occur every year in **November and December (Q4)**, where monthly revenues surge by **42% to 65% MoM** due to Black Friday, Cyber Week, and holiday gifting.
* **Spring Baseline**: January and February observe an anticipated seasonal cooldown (-18% to -24% MoM) before stabilizing in Q2.
* **Compound Trajectory**: Sustained 18.4% Year-over-Year revenue growth from 2023 to 2025.

---

### Question 4: Which categories have declining sales?
* **Declining Categories Identified**:
  1. `CAT-010`: **Outdoor & Camping** — Observed a **-16.8% QoQ decline** in the most recent quarter, with unit volume contracting by 14.2%.
  2. `CAT-008`: **Home Decor & Lighting** — Flattening growth (-4.3% QoQ), indicating market saturation or shifting consumer preference.
* **Growth Anchors**:
  * **Smartphones & Mobile (`CAT-001`)** and **Laptops & Computing (`CAT-002`)** continue strong expansion (+14.5% QoQ).
  * **Skincare & Beauty (`CAT-011`)** demonstrates the highest repurchase replenishment rate (+22.1% QoQ).
* **Strategic Action**: Liquidate slow-moving outdoor and decor inventory through targeted bundled promotions and redirect procurement budgets into high-velocity computing and skincare lines.

---

### Question 5: What is the average order value (AOV)?
* **Storewide Benchmark**: Overall Average Order Value stands at **$302.50**.
* **Channel Comparison**:
  * **Mobile App**: **$328.40 AOV** (highest engagement and multiple line-item additions).
  * **Web Store**: **$294.10 AOV**.
  * **Affiliate / Referral**: **$268.80 AOV**.
* **Payment Processor Impact**:
  * **Buy Now Pay Later (BNPL - Klarna/Affirm)** yields the highest AOV at **$412.30**, as installments reduce sticker shock on premium hardware.
  * **Credit Card**: **$310.20 AOV**.
  * **PayPal & Apple Pay**: **$245.00 - $265.00 AOV**.
* **Action Item**: Promote BNPL options on product pages above $200 and incentivize desktop users to download the Mobile App using a $15 first-in-app discount.

---

### Question 6: Which customers are likely to stop purchasing (Churn Risk)?
* **Risk Breakdown**:
  * **Critical Churn Risk (High Value)**: **184 customers** who have spent >$800 historically but are now **2.5x past their normal repurchase cycle** (>120 days inactive).
  * **High Churn Risk (Dormant)**: **412 customers** showing purchase decay.
  * **Medium Churn Risk (Cooling Down)**: **353 customers** between 60 to 90 days inactive.
* **Total Value at Risk**: Over **$480,000 in potential lost annual repeat revenue**.
* **Retention Action Playbook**:
  1. **Tier 1 (VIP Winback)**: Automated high-touch campaign with $30 account credit and dedicated customer success manager email.
  2. **Tier 2 (Dormant Repeat Buyers)**: Time-sensitive 20% discount on their most frequently purchased category.
  3. **Tier 3 (1-Time Buyers at 60 Days)**: Automated replenishment reminder sequence offering Free Shipping.

---

## 3. Technology Stack & Deliverable Artifacts

1. **SQL Layer**: 6 production scripts (`sql/01_*.sql` through `sql/06_*.sql`) and `sql/schema.sql` executing complex CTEs, window functions (`NTILE`, `LAG`, `RANK`, cumulative sums).
2. **Python & Pandas Layer**: Scalable data generation, ETL orchestrator (`src/etl_pipeline.py`), and analytics modules (`src/analytics/`).
3. **Power BI Model**: Star schema, 25+ DAX measures (`power_bi/dax_measures.txt`), and visual template specifications.
4. **Excel Master Model**: Formatted multi-tab executive workbook (`excel/ecommerce_analytics_master.xlsx`) with automated data formatting.
5. **Interactive Executive BI Web Dashboard**: Standalone browser dashboard (`dashboard/index.html`) featuring interactive Chart.js visualizations, RFM matrix, and churn risk filters.
