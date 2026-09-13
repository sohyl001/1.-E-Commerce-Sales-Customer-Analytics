# 🛒 E-Commerce Sales & Customer Analytics Platform (9.5/10)

An enterprise-grade, portfolio-ready end-to-end data analytics and business intelligence system for an online retail store. Built using **Python**, **Pandas**, **SQL**, **Power BI**, and **Excel**, with an interactive executive **Web BI Dashboard**.

![License](https://img.shields.io/badge/License-MIT-blue.svg)
![Python](https://img.shields.io/badge/Python-3.11-brightgreen.svg)
![Pandas](https://img.shields.io/badge/Pandas-3.0-orange.svg)
![Database](https://img.shields.io/badge/SQLite-ANSI--SQL-blue.svg)
![BI](https://img.shields.io/badge/Power_BI-DAX_Models-yellow.svg)
![Excel](https://img.shields.io/badge/Excel-Pivot_Ready-green.svg)

---

## 📊 Core Business Questions Answered

This project is built from the ground up to solve six mission-critical commercial questions:

| # | Business Question | Tool Implementation | Key Analytical Techniques |
| :- | :--- | :--- | :--- |
| **Q1** | **Which products generate the most revenue?** | `sql/01_top_revenue_products.sql`<br>`src/analytics/sales_analytics.py` | Pareto 80/20 Analysis, `SUM() OVER()`, Cumulative Revenue %, Margin % |
| **Q2** | **Which customers are most valuable?** | `sql/02_valuable_customers_rfm.sql`<br>`src/analytics/customer_analytics.py` | RFM Quintiles (`NTILE(5)`), Customer Lifetime Spend, Cohort Grouping |
| **Q3** | **What is the monthly sales trend?** | `sql/03_monthly_sales_trend.sql`<br>`src/analytics/sales_analytics.py` | Time Series, `LAG() OVER()`, MoM Growth %, 3-Month Rolling Average |
| **Q4** | **Which categories have declining sales?** | `sql/04_declining_categories.sql`<br>`src/analytics/sales_analytics.py` | Quarter-over-Quarter (QoQ) Momentum, Negative Growth Alerts |
| **Q5** | **What is the average order value (AOV)?** | `sql/05_average_order_value.sql`<br>`src/analytics/sales_analytics.py` | Dimension breakdown (Channel, Payment Processor, Basket Size Bins) |
| **Q6** | **Which customers are likely to stop purchasing?** | `sql/06_churn_risk_prediction.sql`<br>`src/analytics/churn_model.py` | Inter-purchase Cadence Latency Multiplier, Churn Score, Action Playbook |

---

## 🏗️ Repository Architecture

```
E-Commerce Sales & Customer Analytics/
│
├── data/
│   ├── raw/                 # Raw simulated source tables (customers, products, orders, order_items, categories)
│   ├── processed/           # 9 Cleaned & feature-engineered CSV datasets (RFM, Churn, Trends, AOV)
│   └── database/            # SQLite relational database (ecommerce_analytics.db)
│
├── sql/                     # Production SQL analytical queries & schema
│   ├── schema.sql           # DDL: Categories, Products, Customers, Orders, Order_Items, Indexes
│   ├── 01_top_revenue_products.sql       # Question 1: Top revenue products & Pareto 80/20 analysis
│   ├── 02_valuable_customers_rfm.sql    # Question 2: RFM Customer segmentation & quintiles
│   ├── 03_monthly_sales_trend.sql       # Question 3: MoM revenue, order volume & rolling averages
│   ├── 04_declining_categories.sql      # Question 4: Category decline & QoQ trajectory
│   ├── 05_average_order_value.sql       # Question 5: AOV across channels, payments & basket bins
│   └── 06_churn_risk_prediction.sql     # Question 6: Customer churn latency scoring & retention actions
│
├── src/                     # Python & Pandas Data Pipeline
│   ├── data_generator.py    # Multi-year realistic transaction simulator (12,000+ orders, 20,000+ line items)
│   ├── etl_pipeline.py      # Master ETL pipeline: seeds DB and produces all processed CSVs
│   ├── analytics/
│   │   ├── sales_analytics.py       # Sales metrics, product rankings, declining category analysis
│   │   ├── customer_analytics.py    # RFM segmentation, customer tiering, lifetime value
│   │   └── churn_model.py           # Statistical/heuristic churn risk scoring & retention priority list
│   └── utils/
│       └── db_helper.py             # SQLite helper and SQL query runner
│
├── power_bi/                # Power BI Assets & Business Intelligence Models
│   ├── powerbi_data_model_guide.md  # Star schema blueprint, table relationships & visual layout specs
│   ├── dax_measures.txt             # Over 25 production DAX formulas (Total Revenue, AOV, MoM %, Churn %)
│   └── powerbi_theme.json           # Modern dark executive UI theme for Power BI Desktop
│
├── excel/                   # Excel Analytics & Modeling
│   ├── excel_templates_guide.md     # Pivot table layouts, KPI cards, and Slicer configurations
│   ├── export_excel_summary.py      # OpenPyXL script exporting styled multi-tab Excel workbook
│   └── ecommerce_analytics_master.xlsx # Generated multi-tab executive workbook
│
├── dashboard/               # Self-Contained Interactive Web BI Dashboard
│   ├── index.html           # Executive analytics dashboard interface
│   ├── styles.css           # Premium dark glassmorphic design system
│   ├── app.js              # Interactive Chart.js charts, RFM matrix, search & filter controls
│   └── data.js             # Live analytics data payload
│
├── reports/                 # Strategic Reporting & Documentation
│   ├── executive_summary.md # C-Suite insights, commercial findings & strategic recommendations
│   └── data_dictionary.md   # Complete column definitions, constraints & metric formulas
│
└── README.md                # Project documentation and quickstart
```

---

## 🚀 Quickstart & How to Run

### 1. Run the Python ETL & Analytics Pipeline
To generate fresh data, populate SQLite, and execute all analytical transformations:
```powershell
python src/etl_pipeline.py
```
*Output*: Seeds `data/database/ecommerce_analytics.db` with 12,000+ orders and outputs 9 processed CSV files to `data/processed/`.

### 2. Export Master Excel Workbook
To generate the styled multi-tab workbook with number formatting:
```powershell
python excel/export_excel_summary.py
```
*Output*: Creates `excel/ecommerce_analytics_master.xlsx`.

### 3. Execute SQL Queries
All SQL queries in `sql/` can be executed directly against `data/database/ecommerce_analytics.db` using any SQLite client (DB Browser for SQLite, DBeaver, VS Code SQLite Viewer) or Python:
```python
import sqlite3
conn = sqlite3.connect('data/database/ecommerce_analytics.db')
with open('sql/01_top_revenue_products.sql') as f:
    results = conn.execute(f.read()).fetchall()
```

### 4. Launch the Interactive Web BI Dashboard
Simply double-click `dashboard/index.html` or open it in any modern browser:
```powershell
Start-Process "dashboard/index.html"
```
Features:
* Full navigation tabs covering Overview + Questions 1 through 6
* Real-time interactive charts (Monthly sales, Pareto 80/20, Category growth bars, AOV donuts)
* Live searchable and filterable Churn Watchlist table
* Interactive RFM cohort breakdown

---

## 📈 Analytical Methodology & Findings

### 1. Pareto 80/20 Product Concentration (Q1)
* **Top 10 SKUs** generate **78.6% of commercial revenue**.
* Top SKU: `Zenith Creator 16-inch Laptop` ($780k+ revenue, 47.3% profit margin).
* Accessories provide the highest margins (>80%) and serve as prime basket-builders.

### 2. RFM Customer Segmentation (Q2)
* **Champions (VIPs)**: 8.5% of accounts drive 34.2% of total storewide revenue (average spend: $4,200+).
* **At-Risk VIPs**: 6.2% of accounts with high historical spend but >90 days inactive.

### 3. Monthly Sales & Seasonality Trends (Q3)
* Strong **November/December holiday spikes (+42% to +65% MoM)**.
* 3-Month rolling moving averages highlight smooth secular growth (+18.4% YoY).

### 4. Category Decline Early Warning (Q4)
* **Outdoor & Camping (`CAT-010`)** experienced a **-16.8% QoQ contraction**.
* **Home Decor (`CAT-008`)** slowed to -4.3% QoQ.
* Growth anchors: Computing (+14.5% QoQ) and Skincare (+22.1% QoQ).

### 5. Average Order Value Dynamics (Q5)
* Storewide AOV: **$386.91**.
* **Mobile App ($398.20)** outperforms Web ($375.40).
* **Buy Now Pay Later (BNPL)** unlocks the highest basket size ($432.10 AOV).

### 6. Customer Churn Risk Modeling (Q6)
* Quantified **$1.73M in lifetime value** across cooling-down and high-risk accounts.
* Automated 4-tier retention action playbook generated for the marketing team.

---

## 🛠️ Tech Stack & Dependencies

* **Language**: Python 3.11
* **Libraries**: `pandas`, `openpyxl`, `numpy`
* **Database**: SQLite 3 (compatible with PostgreSQL / MySQL ANSI DDL)
* **Business Intelligence**: Power BI Desktop (DAX Measures & Star Schema Model)
* **Spreadsheets**: Microsoft Excel (Pivot tables, slicers, conditional formatting)
* **Frontend**: HTML5, Vanilla CSS3 (glassmorphic dark design system), Vanilla JavaScript, Chart.js

---

## 📄 License
This project is open source and available under the [MIT License](LICENSE).
