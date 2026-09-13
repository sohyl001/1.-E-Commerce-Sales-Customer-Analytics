# Excel Analytics & Modeling Guide

## 1. Overview

This project includes multi-tab, pivot-ready Excel exports created directly from the cleaned transaction datasets. Excel serves as a primary tool for ad-hoc stakeholder reporting, dynamic pivot modeling, and financial auditing.

---

## 2. Recommended Pivot Table Configurations

### Sheet 1: Product Revenue & Pareto Breakdown
- **Source Data**: `data/raw/order_items.csv` joined with `data/raw/products.csv` and `data/raw/categories.csv` (or use `data/processed/top_products_summary.csv`)
- **Rows**: `Category Name` -> `Product Name`
- **Values**:
  - `Sum of total_item_price` (Format: Currency `$#,##0.00`, Title: "Total Revenue")
  - `Sum of quantity` (Format: `#,##0`, Title: "Units Sold")
  - `Sum of gross_profit` (Format: Currency `$#,##0.00`, Title: "Gross Profit")
  - Calculated Field: `='Gross Profit' / 'Total Revenue'` (Format: Percentage `0.0%`, Title: "Profit Margin %")
- **Sort**: Total Revenue (Descending)
- **Visual**: Pareto Chart (Clustered Column with Cumulative % Line on secondary axis)

### Sheet 2: Monthly Sales & MoM Growth
- **Source Data**: `data/processed/monthly_sales_summary.csv`
- **Rows**: `Sales Year` -> `Sales Month`
- **Values**:
  - `Sum of monthly_revenue` (Format: `$#,##0`)
  - `Sum of total_orders` (Format: `#,##0`)
  - `Average of monthly_aov` (Format: `$#,##0.00`)
- **Show Values As**:
  - Add `Sum of monthly_revenue` again -> Right Click -> **Show Values As** > **% Difference From** > `Previous Month` to display dynamic MoM growth directly in Excel!
- **Visual**: 2-D Line Chart with trendline and data markers.

### Sheet 3: RFM Customer Segmentation Matrix
- **Source Data**: `data/processed/rfm_customer_segments.csv`
- **Rows**: `rfm_segment` (e.g. Champions, Loyal Customers, At Risk)
- **Values**:
  - `Count of customer_id` (Title: "Customer Count")
  - `Sum of total_lifetime_spend` (Title: "Total Segment Revenue")
  - `Average of customer_avg_order_value` (Title: "Average AOV")
  - `Average of recency_days` (Title: "Avg Days Since Last Order")
- **Conditional Formatting**: Color scale (Green = high value, Red = at risk) on `Avg Days Since Last Order` and `Total Segment Revenue`.

### Sheet 4: Churn Risk Priority Action List
- **Source Data**: `data/processed/churn_risk_analysis.csv`
- **Filters**: `churn_risk_tier` in ("Critical Churn Risk (High Value At-Risk)", "High Churn Risk")
- **Columns**: `customer_id`, `customer_name`, `email`, `customer_tier`, `total_lifetime_spend`, `days_since_last_order`, `retention_action`
- **Data Bars**: Add Gradient Data Bars on `total_lifetime_spend` to highlight the highest value at-risk customers instantly.

---

## 3. Interactive Slicers & Formatting

For a professional C-level presentation in Excel:
1. Insert **Slicers** connected to all Pivot Tables:
   - **Sales Channel** (Web, Mobile App, Affiliate)
   - **Payment Method** (Credit Card, PayPal, Apple Pay, BNPL)
   - **Department / Category**
2. In Excel, navigate to **PivotTable Analyze** > **Filter Connections** to link a single slicer across all pivot tables on the worksheet.
3. Apply the **Dark Navy / Slate** table style with alternating row stripes.
