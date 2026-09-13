/**
 * Executive BI Dashboard Application Logic
 * Renders KPIs, Interactive Chart.js Visualizations, RFM Cohorts,
 * and Filterable Data Tables for all 6 core business questions.
 */

document.addEventListener("DOMContentLoaded", () => {
  if (typeof ANALYTICS_DATA === "undefined") {
    console.error("ANALYTICS_DATA is not defined. Ensure data.js is loaded.");
    return;
  }

  // 1. Navigation Tab Switching
  setupTabNavigation();

  // 2. Render Top Executive KPIs
  renderKPIs(ANALYTICS_DATA.kpis);

  // 3. Render Question 1: Top Revenue Products & Pareto
  renderTopProducts(ANALYTICS_DATA.top_products);

  // 4. Render Question 2: Customer Valuation (RFM)
  renderRFMAnalytics(ANALYTICS_DATA.rfm_summary, ANALYTICS_DATA.top_customers);

  // 5. Render Question 3: Monthly Sales Trends
  renderMonthlyTrends(ANALYTICS_DATA.monthly_trend);

  // 6. Render Question 4: Declining Categories
  renderDecliningCategories(ANALYTICS_DATA.category_momentum);

  // 7. Render Question 5: Average Order Value
  renderAOVAnalytics(ANALYTICS_DATA.aov_channel);

  // 8. Render Question 6: Churn Risk Watchlist
  renderChurnWatchlist(ANALYTICS_DATA.churn_watchlist);

  // 9. Render Overview Charts
  renderOverviewCharts(ANALYTICS_DATA);
});

/* --------------------------------------------------------------------------
   Navigation Tab Switching
   -------------------------------------------------------------------------- */
function setupTabNavigation() {
  const tabs = document.querySelectorAll(".nav-tab");
  const sections = document.querySelectorAll(".dashboard-section");

  tabs.forEach(tab => {
    tab.addEventListener("click", () => {
      tabs.forEach(t => t.classList.remove("active"));
      tab.classList.add("active");

      const targetId = tab.getAttribute("data-target");
      sections.forEach(sec => {
        if (sec.id === targetId) {
          sec.classList.remove("hidden-section");
        } else {
          sec.classList.add("hidden-section");
        }
      });
      window.scrollTo({ top: 0, behavior: "smooth" });
    });
  });
}

/* --------------------------------------------------------------------------
   KPI Formatting & Rendering
   -------------------------------------------------------------------------- */
function renderKPIs(kpis) {
  const formatCur = num => "$" + Number(num).toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
  const formatInt = num => Number(num).toLocaleString("en-US");

  document.getElementById("kpiTotalRevenue").textContent = formatCur(kpis.total_revenue);
  document.getElementById("kpiTotalProfit").textContent = formatCur(kpis.total_profit);
  document.getElementById("kpiProfitMargin").textContent = kpis.profit_margin + "%";
  document.getElementById("kpiTotalOrders").textContent = formatInt(kpis.total_orders);
  document.getElementById("kpiAov").textContent = formatCur(kpis.aov);
  document.getElementById("kpiTotalCustomers").textContent = formatInt(kpis.total_customers);
  document.getElementById("kpiAtRiskCount").textContent = formatInt(kpis.at_risk_count);
  document.getElementById("kpiAtRiskSpend").textContent = formatCur(kpis.at_risk_spend);
}

/* --------------------------------------------------------------------------
   Question 1: Top Revenue Products & Pareto
   -------------------------------------------------------------------------- */
function renderTopProducts(products) {
  const top10 = products.slice(0, 10);

  // 1. Horizontal Bar Chart (Top 10 SKUs)
  const ctxBar = document.getElementById("topProductsBarChart").getContext("2d");
  new Chart(ctxBar, {
    type: "bar",
    data: {
      labels: top10.map(p => p.product_name.length > 25 ? p.product_name.substring(0, 23) + "..." : p.product_name),
      datasets: [{
        label: "Revenue ($)",
        data: top10.map(p => p.total_revenue),
        backgroundColor: "rgba(99, 102, 241, 0.8)",
        borderColor: "#6366f1",
        borderRadius: 6,
        borderWidth: 1
      }]
    },
    options: {
      indexAxis: "y",
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            label: context => ` Revenue: $${context.raw.toLocaleString()}`
          }
        }
      },
      scales: {
        x: {
          ticks: { color: "#94a3b8", callback: v => "$" + (v / 1000) + "k" },
          grid: { color: "rgba(255, 255, 255, 0.05)" }
        },
        y: {
          ticks: { color: "#cbd5e1" },
          grid: { display: false }
        }
      }
    }
  });

  // 2. Pareto 80/20 Chart
  const ctxPareto = document.getElementById("paretoChart").getContext("2d");
  new Chart(ctxPareto, {
    type: "bar",
    data: {
      labels: products.slice(0, 15).map(p => p.product_id),
      datasets: [
        {
          type: "line",
          label: "Cumulative Revenue %",
          data: products.slice(0, 15).map(p => p.cumulative_revenue_pct),
          borderColor: "#38bdf8",
          backgroundColor: "#38bdf8",
          borderWidth: 2,
          pointRadius: 4,
          yAxisID: "yCumulative"
        },
        {
          type: "bar",
          label: "Product Revenue ($)",
          data: products.slice(0, 15).map(p => p.total_revenue),
          backgroundColor: "rgba(56, 189, 248, 0.25)",
          borderColor: "#38bdf8",
          borderWidth: 1,
          borderRadius: 4,
          yAxisID: "yRevenue"
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        yRevenue: {
          position: "left",
          ticks: { color: "#94a3b8", callback: v => "$" + (v / 1000) + "k" },
          grid: { color: "rgba(255, 255, 255, 0.05)" }
        },
        yCumulative: {
          position: "right",
          max: 100,
          ticks: { color: "#38bdf8", callback: v => v + "%" },
          grid: { display: false }
        },
        x: {
          ticks: { color: "#94a3b8" },
          grid: { display: false }
        }
      },
      plugins: {
        legend: { labels: { color: "#94a3b8" } }
      }
    }
  });

  // 3. Products Table
  const tableBody = document.getElementById("productsTableBody");
  function renderRows(items) {
    tableBody.innerHTML = items.map((p, idx) => `
      <tr>
        <td><strong>#${idx + 1}</strong></td>
        <td><code>${p.product_id}</code></td>
        <td><strong>${p.product_name}</strong></td>
        <td>${p.category_name}</td>
        <td>${Number(p.units_sold).toLocaleString()}</td>
        <td><strong>$${Number(p.total_revenue).toLocaleString(undefined, {minimumFractionDigits: 2})}</strong></td>
        <td class="accent-text">$${Number(p.total_gross_profit).toLocaleString(undefined, {minimumFractionDigits: 2})}</td>
        <td>${p.profit_margin_pct}%</td>
        <td>${p.cumulative_revenue_pct}%</td>
        <td>
          <span class="pareto-pill ${p.cumulative_revenue_pct <= 80 ? 'pareto-top' : 'pareto-tail'}">
            ${p.cumulative_revenue_pct <= 80 ? 'Core 80% SKU' : 'Long Tail'}
          </span>
        </td>
      </tr>
    `).join("");
  }
  renderRows(products);

  document.getElementById("productSearchInput").addEventListener("input", e => {
    const q = e.target.value.toLowerCase();
    const filtered = products.filter(p => 
      p.product_name.toLowerCase().includes(q) || 
      p.product_id.toLowerCase().includes(q) || 
      p.category_name.toLowerCase().includes(q)
    );
    renderRows(filtered);
  });
}

/* --------------------------------------------------------------------------
   Question 2: Customer Valuation & RFM
   -------------------------------------------------------------------------- */
function renderRFMAnalytics(rfmSummary, topCustomers) {
  const cardsContainer = document.getElementById("rfmCardsContainer");
  cardsContainer.innerHTML = rfmSummary.map(seg => `
    <div class="rfm-cohort-card">
      <div class="rfm-card-title">
        <span>${seg.rfm_segment}</span>
        <span class="status-pill" style="font-size: 0.7rem; padding: 0.1rem 0.5rem;">${seg.pct_of_customers}% base</span>
      </div>
      <div class="rfm-stat-row">
        <span>Customer Count:</span>
        <span class="rfm-stat-val">${Number(seg.customer_count).toLocaleString()}</span>
      </div>
      <div class="rfm-stat-row">
        <span>Cohort Total Spend:</span>
        <span class="rfm-stat-val accent-text">$${Number(seg.total_revenue).toLocaleString(undefined, {minimumFractionDigits: 2})}</span>
      </div>
      <div class="rfm-stat-row">
        <span>Revenue Share:</span>
        <span class="rfm-stat-val">${seg.pct_of_revenue}%</span>
      </div>
      <div class="rfm-stat-row">
        <span>Average Orders:</span>
        <span class="rfm-stat-val">${Number(seg.avg_order_count).toFixed(1)}</span>
      </div>
      <div class="rfm-stat-row">
        <span>Avg Days Inactive:</span>
        <span class="rfm-stat-val">${Math.round(seg.avg_recency_days)} days</span>
      </div>
    </div>
  `).join("");

  // Top Customers Table
  const custTableBody = document.getElementById("topCustomersTableBody");
  custTableBody.innerHTML = topCustomers.map((c, idx) => `
    <tr>
      <td><strong>#${idx + 1}</strong></td>
      <td><code>${c.customer_id}</code></td>
      <td><strong>${c.customer_name}</strong></td>
      <td>${c.email}</td>
      <td>${c.state}</td>
      <td>${c.acquisition_channel}</td>
      <td>${c.total_orders}</td>
      <td class="accent-text"><strong>$${Number(c.total_lifetime_spend).toLocaleString(undefined, {minimumFractionDigits: 2})}</strong></td>
      <td>$${Number(c.customer_avg_order_value).toFixed(2)}</td>
      <td>${c.recency_days} d</td>
      <td><span class="status-pill" style="font-size: 0.7rem;">${c.rfm_segment}</span></td>
    </tr>
  `).join("");
}

/* --------------------------------------------------------------------------
   Question 3: Monthly Sales Trends
   -------------------------------------------------------------------------- */
function renderMonthlyTrends(monthly) {
  const ctx = document.getElementById("monthlyTrendFullChart").getContext("2d");
  new Chart(ctx, {
    type: "bar",
    data: {
      labels: monthly.map(m => m.sales_month),
      datasets: [
        {
          type: "line",
          label: "3-Mo Rolling Avg ($)",
          data: monthly.map(m => m.rolling_3mo_avg_revenue),
          borderColor: "#38bdf8",
          borderWidth: 2.5,
          tension: 0.3,
          pointRadius: 2,
          yAxisID: "yRev"
        },
        {
          type: "bar",
          label: "Monthly Sales ($)",
          data: monthly.map(m => m.monthly_revenue),
          backgroundColor: "rgba(99, 102, 241, 0.4)",
          borderColor: "#6366f1",
          borderRadius: 4,
          borderWidth: 1,
          yAxisID: "yRev"
        },
        {
          type: "line",
          label: "MoM Growth %",
          data: monthly.map(m => m.mom_revenue_growth_pct),
          borderColor: "#f59e0b",
          borderWidth: 1.5,
          borderDash: [4, 4],
          pointRadius: 0,
          yAxisID: "yPct"
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        yRev: {
          position: "left",
          ticks: { color: "#94a3b8", callback: v => "$" + (v / 1000) + "k" },
          grid: { color: "rgba(255, 255, 255, 0.05)" }
        },
        yPct: {
          position: "right",
          ticks: { color: "#f59e0b", callback: v => v + "%" },
          grid: { display: false }
        },
        x: {
          ticks: { color: "#94a3b8", maxRotation: 45 },
          grid: { display: false }
        }
      },
      plugins: {
        legend: { labels: { color: "#cbd5e1" } }
      }
    }
  });
}

/* --------------------------------------------------------------------------
   Question 4: Declining Categories
   -------------------------------------------------------------------------- */
function renderDecliningCategories(categoryMomentum) {
  // Take unique latest quarter per category
  const latestQuarter = categoryMomentum[categoryMomentum.length - 1].sales_quarter;
  const latestRecords = categoryMomentum.filter(r => r.sales_quarter === latestQuarter);

  // Bar Chart
  const ctx = document.getElementById("categoryGrowthChart").getContext("2d");
  new Chart(ctx, {
    type: "bar",
    data: {
      labels: latestRecords.map(c => c.category_name.split(" ")[0]),
      datasets: [{
        label: `QoQ Growth % (${latestQuarter})`,
        data: latestRecords.map(c => c.qoq_revenue_growth_pct),
        backgroundColor: latestRecords.map(c => c.qoq_revenue_growth_pct < 0 ? "rgba(244, 63, 94, 0.7)" : "rgba(16, 185, 129, 0.7)"),
        borderRadius: 4
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        y: {
          ticks: { color: "#94a3b8", callback: v => v + "%" },
          grid: { color: "rgba(255, 255, 255, 0.05)" }
        },
        x: {
          ticks: { color: "#cbd5e1" },
          grid: { display: false }
        }
      },
      plugins: {
        legend: { labels: { color: "#94a3b8" } }
      }
    }
  });

  // Department Alert List
  const alertList = document.getElementById("categoryAlertList");
  alertList.innerHTML = latestRecords.map(cat => {
    let alertClass = "healthy";
    if (cat.qoq_revenue_growth_pct < -15) alertClass = "critical";
    else if (cat.qoq_revenue_growth_pct < 0) alertClass = "moderate";

    const isNeg = cat.qoq_revenue_growth_pct < 0;
    return `
      <div class="category-alert-card ${alertClass}">
        <div>
          <div class="cat-alert-name">${cat.category_name}</div>
          <div class="cat-alert-dept">${cat.department} • Revenue: $${Number(cat.quarterly_revenue).toLocaleString(undefined, {minimumFractionDigits: 2})}</div>
        </div>
        <div class="cat-alert-growth ${isNeg ? 'growth-negative' : 'growth-positive'}">
          ${cat.qoq_revenue_growth_pct > 0 ? '+' : ''}${cat.qoq_revenue_growth_pct}%
        </div>
      </div>
    `;
  }).join("");
}

/* --------------------------------------------------------------------------
   Question 5: Average Order Value
   -------------------------------------------------------------------------- */
function renderAOVAnalytics(aovData) {
  // Aggregate AOV by Channel
  const channels = {};
  const payments = {};

  aovData.forEach(row => {
    channels[row.sales_channel] = (channels[row.sales_channel] || []).concat(row.channel_aov);
    payments[row.payment_method] = (payments[row.payment_method] || []).concat(row.channel_aov);
  });

  const avg = arr => (arr.reduce((a, b) => a + b, 0) / arr.length).toFixed(2);

  // AOV Channel Chart
  const ctxCh = document.getElementById("aovChannelChart").getContext("2d");
  new Chart(ctxCh, {
    type: "doughnut",
    data: {
      labels: Object.keys(channels),
      datasets: [{
        data: Object.values(channels).map(avg),
        backgroundColor: ["#6366f1", "#38bdf8", "#10b981"]
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { position: "bottom", labels: { color: "#cbd5e1" } },
        tooltip: { callbacks: { label: c => ` AOV: $${c.raw}` } }
      }
    }
  });

  // AOV Payment Chart
  const ctxPay = document.getElementById("aovPaymentChart").getContext("2d");
  new Chart(ctxPay, {
    type: "bar",
    data: {
      labels: Object.keys(payments),
      datasets: [{
        label: "Avg Order Value ($)",
        data: Object.values(payments).map(avg),
        backgroundColor: ["#ec4899", "#8b5cf6", "#f59e0b", "#38bdf8"],
        borderRadius: 6
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        y: {
          ticks: { color: "#94a3b8", callback: v => "$" + v },
          grid: { color: "rgba(255, 255, 255, 0.05)" }
        },
        x: {
          ticks: { color: "#cbd5e1" },
          grid: { display: false }
        }
      },
      plugins: {
        legend: { display: false }
      }
    }
  });
}

/* --------------------------------------------------------------------------
   Question 6: Churn Risk Watchlist
   -------------------------------------------------------------------------- */
function renderChurnWatchlist(churnWatchlist) {
  const tbody = document.getElementById("churnTableBody");

  function render(list) {
    tbody.innerHTML = list.map(c => {
      let tierClass = "tier-medium";
      if (c.churn_risk_tier.includes("Critical")) tierClass = "tier-critical";
      else if (c.churn_risk_tier.includes("High")) tierClass = "tier-high";

      return `
        <tr>
          <td><code>${c.customer_id}</code></td>
          <td><strong>${c.customer_name}</strong></td>
          <td>${c.email}</td>
          <td><span class="status-pill" style="font-size: 0.7rem;">${c.customer_tier}</span></td>
          <td class="accent-text"><strong>$${Number(c.total_lifetime_spend).toLocaleString(undefined, {minimumFractionDigits: 2})}</strong></td>
          <td>${c.total_orders}</td>
          <td><strong>${c.days_since_last_order} days</strong></td>
          <td>${c.cadence_latency_multiplier}x cycle</td>
          <td><strong>${c.churn_probability_score} / 100</strong></td>
          <td class="${tierClass}">${c.churn_risk_tier}</td>
          <td><span style="font-size: 0.78rem; color: #cbd5e1;">${c.retention_action}</span></td>
        </tr>
      `;
    }).join("");
  }

  render(churnWatchlist);

  // Filters
  const searchInput = document.getElementById("churnSearchInput");
  const tierFilter = document.getElementById("churnTierFilter");

  function applyFilters() {
    const q = searchInput.value.toLowerCase();
    const t = tierFilter.value;

    const filtered = churnWatchlist.filter(c => {
      const matchText = c.customer_name.toLowerCase().includes(q) || c.email.toLowerCase().includes(q) || c.customer_id.toLowerCase().includes(q);
      const matchTier = (t === "ALL") || c.churn_risk_tier.includes(t);
      return matchText && matchTier;
    });
    render(filtered);
  }

  searchInput.addEventListener("input", applyFilters);
  tierFilter.addEventListener("change", applyFilters);
}

/* --------------------------------------------------------------------------
   Overview Charts
   -------------------------------------------------------------------------- */
function renderOverviewCharts(data) {
  // 1. Overview Sales Line Chart
  const ctx = document.getElementById("overviewSalesChart").getContext("2d");
  new Chart(ctx, {
    type: "line",
    data: {
      labels: data.monthly_trend.map(m => m.sales_month),
      datasets: [
        {
          label: "Monthly Sales ($)",
          data: data.monthly_trend.map(m => m.monthly_revenue),
          borderColor: "#6366f1",
          backgroundColor: "rgba(99, 102, 241, 0.15)",
          fill: true,
          tension: 0.35,
          borderWidth: 2,
          pointRadius: 2
        },
        {
          label: "3-Month Moving Average",
          data: data.monthly_trend.map(m => m.rolling_3mo_avg_revenue),
          borderColor: "#38bdf8",
          borderWidth: 2,
          pointRadius: 0,
          borderDash: [5, 5]
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        y: {
          ticks: { color: "#94a3b8", callback: v => "$" + (v / 1000) + "k" },
          grid: { color: "rgba(255, 255, 255, 0.05)" }
        },
        x: {
          ticks: { color: "#94a3b8", maxTicksLimit: 12 },
          grid: { display: false }
        }
      },
      plugins: {
        legend: { labels: { color: "#cbd5e1" } }
      }
    }
  });

  // 2. Overview RFM Donut Chart
  const ctxDonut = document.getElementById("overviewRfmDonutChart").getContext("2d");
  new Chart(ctxDonut, {
    type: "doughnut",
    data: {
      labels: data.rfm_summary.map(s => s.rfm_segment),
      datasets: [{
        data: data.rfm_summary.map(s => s.total_revenue),
        backgroundColor: [
          "#6366f1", "#38bdf8", "#10b981", "#f59e0b",
          "#ec4899", "#8b5cf6", "#14b8a6", "#94a3b8"
        ],
        borderWidth: 0
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { position: "right", labels: { color: "#cbd5e1", boxWidth: 12 } },
        tooltip: {
          callbacks: {
            label: c => ` ${c.label}: $${Number(c.raw).toLocaleString(undefined, {maximumFractionDigits: 0})}`
          }
        }
      }
    }
  });
}
