# Consumer360 — Project Report
## Retail Analytics: Customer Segmentation & Lifetime Value Engine

**Prepared by:** Squadron Beta | Infotact Solutions
**Date:** March 2026
**Dataset:** Online Retail (UCI Machine Learning Repository) | Dec 2009 - Dec 2011

---

## Page 1: Problem Statement & Objectives

### Business Problem

A national retail chain is experiencing significant customer churn. The business lacks visibility into which customers are high-value, which are at risk of leaving, and what products to recommend for cross-selling. Marketing campaigns are untargeted, resulting in wasted spend on low-value customers and missed opportunities with high-value ones.

### Objectives

1. **Segment customers** using RFM (Recency, Frequency, Monetary) scoring to identify Champions, Loyalists, At Risk, and Hibernating customers
2. **Predict churn probability** for every customer using machine learning
3. **Forecast Customer Lifetime Value (CLV)** over the next 12 months
4. **Discover product bundles** through association rule mining for cross-sell recommendations
5. **Track customer retention** across monthly acquisition cohorts
6. **Automate the entire pipeline** with quality gates and scheduled execution
7. **Deliver an interactive dashboard** with Row Level Security for regional managers

### Dataset Overview

| Metric | Value |
|--------|-------|
| Total Transactions | 401,604 |
| Unique Customers | 5,863 |
| Unique Products | 3,877 |
| Countries | 25 |
| Date Range | Dec 2009 - Dec 2011 |
| Primary Market | United Kingdom (82% of revenue) |

---

## Page 2: Architecture & Methodology

### Data Architecture

The pipeline follows a **star schema** design in MySQL 8.4:

- **Fact Table:** `fact_sales` (401,604 rows) — InvoiceNo, CustomerID, StockCode, Quantity, UnitPrice, TotalAmount, IsReturn, DateId
- **Dimension Tables:**
  - `dim_customer` (5,863 rows) — CustomerID, Country
  - `dim_date` (731 rows) — DateID, FullDate, Year, Month, Day, Weekday
  - `dim_product` (3,877 rows) — StockCode, Description
- **Analytical Views:** 7 views for segmentation, churn, revenue trends, and cohort analysis
- **Stored Procedure:** `refresh_rfm` — NTILE-based RFM scoring with quintile ranking

### Pipeline Architecture

```
MySQL Star Schema
    |
    v
Python Pipeline (Consumer360.py)
    |
    ├── Gate 1: Source Validation (row count, nulls, uniqueness)
    ├── RFM Segmentation (assign_segment function)
    ├── Gate 2: Segmentation Validation (score ranges, coverage)
    ├── Churn Prediction (Logistic Regression)
    ├── Gate 3: Churn Model Validation (AUC > 0.60)
    ├── CLV Prediction (BG/NBD + Gamma-Gamma)
    ├── Gate 4: CLV Validation (no negatives)
    ├── Customer Merge (left join)
    ├── Gate 5: Merge Reconciliation (< 20% loss)
    ├── Basket Analysis (Apriori algorithm)
    ├── Gate 6: Basket Validation (rule count, lift > 1)
    ├── Cohort Retention Analysis
    ├── Gate 7: Retention Validation (0-100%, M+0 = 100%)
    ├── CSV + Heatmap Output
    └── Gate 8: Output File Validation (existence, row counts)
    |
    v
Power BI Dashboard (8 pages + RLS)
```

### Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Database | MySQL 8.4 | Star schema, views, stored procedures |
| ETL/ML | Python 3.14 | pandas, scikit-learn, lifetimes, mlxtend |
| Visualization | Power BI Desktop | Interactive dashboard with RLS |
| Automation | Cron + Bash | Daily scheduled pipeline execution |
| Security | python-dotenv | Credential management via .env |

### Quality Assurance

8 automated quality gates validate every pipeline run. If any gate fails, the pipeline halts with a descriptive error and non-zero exit code. Gates cover:

1. Source data integrity (nulls, duplicates, row counts)
2. Segmentation correctness (score ranges, segment coverage, revenue ranking)
3. Model performance (AUC threshold, churn rate bounds)
4. CLV validity (no negative predictions)
5. Merge integrity (customer preservation)
6. Association rule quality (minimum rules, lift > 1)
7. Retention matrix validity (percentage bounds)
8. Output file completeness (existence, minimum rows)

---

## Page 3: Key Findings

### Customer Segmentation

| Segment | Customers | % of Base | Avg Recency (days) | Avg Frequency | Avg Revenue | Avg CLV (12mo) |
|---------|-----------|-----------|---------------------|---------------|-------------|----------------|
| Champions | 586 | 10.0% | 19.29 | 16.58 | 8,854.19 | 369.17 |
| Loyalists | 1,338 | 22.8% | 70.50 | 5.80 | 2,324.22 | 251.30 |
| At Risk | 1,146 | 19.6% | 353.97 | 5.92 | 2,529.32 | 45.92 |
| Hibernating | 2,793 | 47.6% | 308.34 | 1.61 | 436.26 | 33.56 |

**Key Insight:** Champions represent only 10% of customers but generate the highest average revenue (8,854) and CLV (369). Nearly half the customer base (47.6%) is Hibernating with minimal engagement.

### Churn Prediction

- **Model:** Logistic Regression (L2 regularized, C=0.1)
- **ROC-AUC:** > 0.60 (validated by Gate 3)
- **Churn Definition:** No purchase in 90+ days
- **Features:** F_Raw, M_Raw, F_Score, M_Score (R_Raw excluded to prevent data leakage)
- **Risk Distribution:**
  - Low Risk (< 0.3): 3,210 customers (54.8%)
  - Medium Risk (0.3 - 0.5): 1,360 customers (23.2%)
  - High Risk (> 0.5): 1,293 customers (22.0%)
- **At-Risk Customers (60-180 days):** 1,101 flagged for win-back campaigns

### Customer Lifetime Value

- **Models:** BG/NBD (purchase frequency) + Gamma-Gamma (monetary value)
- **Scope:** 4,244 repeat customers (72.4% of base)
- **Average 12-month CLV:** 199.87
- **Maximum CLV:** 129,069.24 (Customer 16446)
- **Single-purchase customers:** 1,619 (27.6%) — insufficient data for CLV estimation

### Basket Analysis

- **Method:** Apriori algorithm (min support: 2%, min lift: 1.5)
- **Rules Discovered:** 60
- **Top Product Pairs:**

| Product A | Product B | Confidence | Lift |
|-----------|-----------|------------|------|
| Teacup Regency Green | Teacup Regency Roses | 80% | 27.41x |
| Sweetheart Ceramic Trinket Box | Strawberry Ceramic Trinket Pot | 73% | 14.22x |
| Wooden Frame Antique White | Wooden Picture Frame White Finish | 60% | 12.43x |

A lift of 27x means customers are 27 times more likely to buy both items together than by chance.

### Cohort Retention

- **25 monthly cohorts** tracked (Dec 2009 - Dec 2011)
- **First-month retention:** 14-35% across cohorts (65-86% first-month drop-off)
- **Stabilization:** Retention stabilizes at 10-25% by month 3
- **Best cohort:** Dec 2009 (954 customers) — 49% retention at month 11
- **Worst cohort:** Dec 2010 (163 customers) — only 5% retention by month 5

---

## Page 4: Dashboard & Automation

### Power BI Dashboard

8-page interactive dashboard with the following structure:

| Page | Content | Key Visuals |
|------|---------|-------------|
| Executive Summary | KPI cards, segment donut, country map | 17.21M revenue, 6K customers, 37K orders |
| RFM Segmentation | Segment comparison, scatter plot | 4-segment breakdown with metrics |
| Churn Risk Analysis | Probability histogram, risk donut, customer list | 1K at-risk customers identified |
| Customer Lifetime Value | CLV distribution, top customers, CLV by segment | Avg CLV 199.87, Max 129K |
| Basket Analysis | Association rules table, confidence vs lift scatter | 60 rules, max lift 27.41 |
| Cohort Retention | Heatmap matrix with color scale | 25 cohorts, 12-month tracking |
| Revenue Trends | Monthly line chart, MoM change, country treemap | 24-month revenue trajectory |
| What-If Simulation | Re-engagement slider with projected revenue | Interactive scenario modeling |

### Row Level Security (RLS)

Three roles configured to restrict data access by region:

| Role | Filter | Countries |
|------|--------|-----------|
| UK Manager | Country = "United Kingdom" | UK only |
| Europe Manager | Country IN {...} | 13 European countries |
| Rest of World | Country IN {...} | Australia, Japan, USA, Canada, etc. |

### Automation

| Component | Details |
|-----------|---------|
| Schedule | Daily at 3:00 PM via cron |
| Wrapper | `cron_consumer360.sh` — handles logging and exit codes |
| Logging | `logs/pipeline.log` — timestamped with exit codes |
| Error Handling | try/except with sys.exit(1) for cron alerting |
| Credentials | .env file (excluded from git via .gitignore) |
| Quality Gates | 8 sequential gates — pipeline halts on any failure |

---

## Page 5: Strategic Recommendations & Next Steps

### Recommendations

**1. Retain Champions (586 customers, 10% of base)**
Champions generate the highest revenue per customer (avg 8,854) and CLV (avg 369). Implement a VIP loyalty program with early access to new products, personalized offers, and dedicated account management. Estimated retention value: high — losing even 10% of Champions represents significant revenue loss.

**2. Win Back At-Risk Customers (1,101 flagged, 60-180 days inactive)**
These customers have purchase history but are fading. Launch targeted re-engagement campaigns prioritized by revenue. The What-If simulation shows that re-engaging just 20% of at-risk customers could recover approximately 411K in revenue.

**3. Activate High-CLV Hibernating Customers**
Not all Hibernating customers are equal. Use CLV scores to identify Hibernating customers with above-average predicted lifetime value and target them with deep discount offers. Deprioritize low-CLV Hibernating customers to optimize marketing spend.

**4. Implement Cross-Sell Bundles**
Deploy the 60 association rules as product page recommendations and bundle deals. The top rule (Teacup Regency pair, lift 27x) is a strong candidate for an immediate bundle promotion. Expected outcome: increased average order value.

**5. Fix First-Month Retention**
Cohort analysis reveals a consistent 65-86% drop-off in the first month across all cohorts. Implement a post-purchase email sequence (order confirmation → usage tips → feedback request → next purchase incentive) to address this critical leakage point.

**6. Allocate Acquisition Budget by CLV**
Use CLV profiles to build lookalike audiences for customer acquisition. Focus acquisition spend on profiles that match Champions and Loyalists rather than broad targeting. This shifts marketing from volume-based to value-based acquisition.

### Next Steps

| Priority | Action | Timeline |
|----------|--------|----------|
| 1 | Deploy Power BI dashboard to stakeholders | Immediate |
| 2 | Launch win-back campaign for 1,101 at-risk customers | Week 1 |
| 3 | Implement top 10 bundle recommendations on product pages | Week 2 |
| 4 | Design post-purchase email sequence for first-month retention | Week 3 |
| 5 | Set up A/B testing framework for retention campaigns | Month 2 |
| 6 | Explore real-time scoring via API endpoint | Month 3 |
| 7 | Expand to product-level CLV and category affinity | Quarter 2 |

### Project Deliverables

| Deliverable | Location |
|-------------|----------|
| Python Pipeline | `Consumer360.py` |
| MySQL Database | `mysql/online_retail.sql` |
| Pipeline Outputs | `rfm_segments.csv`, `clv_predictions.csv`, `basket_rules.csv`, `cohort_retention.csv`, `churn_risk_list.csv` |
| Cohort Heatmap | `cohort_retention_heatmap.png` |
| ER Diagram | `Consumer360_ER_Diagram.png` |
| Power BI Dashboard | `consumer360.pbix` (8 pages + RLS) |
| Executive Brief | `docs/executive_brief.md` |
| Presentation Outline | `docs/executive_deck_outline.md` |
| Cron Automation | `cron_consumer360.sh` + crontab |
| This Report | `docs/project_report.md` |
