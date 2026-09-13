# Power BI Data Modeling & Dashboard Blueprint

## 1. Star Schema Architecture

To achieve optimal query performance and visual flexibility in Power BI, structure the model as a standard Star Schema:

```
          +-------------------------+
          |      DimDate (DAX)      |
          +-------------------------+
                       | (1)
                       |
                       | (*)
+------------------+   |   +-----------------------+
|  DimCustomers    |---+---|      FactOrders       |
|  (customers.csv) |(1) (*)│      (orders.csv)     |
+------------------+       +-----------------------+
                                       | (1)
                                       |
                                       | (*)
+------------------+       +-----------------------+
|  DimCategories   |       |     FactOrderItems    |
| (categories.csv) |       |   (order_items.csv)   |
+------------------+       +-----------------------+
         | (1)                         | (*)
         |                             |
         | (*)                         | (1)
+------------------+                   |
|   DimProducts    |-------------------+
|  (products.csv)  |
+------------------+
```

### Table Relationships:
1. `DimCustomers[customer_id]` (1) to `FactOrders[customer_id]` (*) -> Single direction filter
2. `FactOrders[order_id]` (1) to `FactOrderItems[order_id]` (*) -> Single direction filter
3. `DimProducts[product_id]` (1) to `FactOrderItems[product_id]` (*) -> Single direction filter
4. `DimCategories[category_id]` (1) to `DimProducts[category_id]` (*) -> Single direction filter
5. `DimDate[Date]` (1) to `FactOrders[order_date]` (*) -> Single direction filter

---

## 2. Dynamic Date Table (DAX Script)

In Power BI Desktop, click **Modeling** > **New Table** and paste this DAX formula:

```dax
DimDate = 
VAR MinYear = 2023
VAR MaxYear = 2026
VAR CalendarTable = CALENDAR(DATE(MinYear, 1, 1), DATE(MaxYear, 12, 31))
RETURN
ADDCOLUMNS(
    CalendarTable,
    "Year", YEAR([Date]),
    "Quarter", "Q" & FORMAT([Date], "Q"),
    "YearQuarter", FORMAT([Date], "YYYY") & "-Q" & FORMAT([Date], "Q"),
    "MonthNumber", MONTH([Date]),
    "MonthName", FORMAT([Date], "mmmm"),
    "MonthShort", FORMAT([Date], "mmm"),
    "YearMonth", FORMAT([Date], "YYYY-MM"),
    "WeekNumber", WEEKNUM([Date]),
    "DayOfWeek", FORMAT([Date], "dddd"),
    "IsWeekend", IF(WEEKDAY([Date], 2) >= 6, 1, 0)
)
```

---

## 3. Recommended Power BI Visualizations Layout

### Page 1: Executive Sales & Product Performance
- **Top KPI Cards**: Total Revenue, Total Orders, Average Order Value (AOV), Gross Profit Margin %
- **Monthly Trend**: Clustered Column & Line Chart (`DimDate[YearMonth]` on X-axis, `Total Gross Revenue` on Columns, `MoM Sales Growth %` on Line)
- **Top Revenue Products**: Horizontal Bar Chart (`products[product_name]` on Y-axis, `Total Gross Revenue` on X-axis, sorted descending)
- **Category Matrix**: Table visual showing `Department`, `Category`, `Revenue`, `Profit Margin %`, and `QoQ Growth %`
- **Slicers**: Date range, Department, Sales Channel

### Page 2: Customer Valuation & RFM Segments
- **KPI Cards**: Active Customers, Customer Lifetime Spend Avg, VIP Champions Count
- **RFM Distribution**: Treemap visual (`Customer RFM Tier` by `Total Gross Revenue` and Customer Count)
- **Customer Lifetime Value Scatter Plot**: X-axis = `Customer Order Count`, Y-axis = `Customer Lifetime Spend`, Bubble Size = `Average Order Value`
- **Top Valuable Customers Table**: `Customer Name`, `Tier`, `Total Orders`, `Lifetime Spend`, `Days Inactive`

### Page 3: Attrition & Churn Risk Watchlist
- **KPI Cards**: Total At-Risk Customers, High-Value At-Risk Spend, Churn Risk Ratio %
- **Inactivity Distribution**: Donut chart (`Customer Retention Priority` by customer count)
- **Urgent Retention Action Table**: Filtered for `Is Churn Risk Flag = 1`
  - Columns: `Customer Name`, `Email`, `Customer Tier`, `Total Lifetime Spend`, `Days Since Last Order`, `Retention Action`
  - Conditional formatting: Red highlight on `Days Since Last Order > 120`

---

## 4. How to Import the Custom Theme

1. Open Power BI Desktop.
2. Navigate to the **View** tab > click the themes dropdown.
3. Click **Browse for themes...**
4. Select `power_bi/powerbi_theme.json`.
