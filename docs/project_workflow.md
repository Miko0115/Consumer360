# Consumer360 — Project Workflow & File Reference

## Workflow Overview

```
Raw Data (UCI Online Retail CSV — online_retail.csv)
        |
        v
EDA & Cleaning (basic_EDA.py)
        |   - Column renaming, null removal, cancellation filtering
        |   - Type casting, amount calculation, deduplication
        |   - Output: online_retail_clean.csv
        |
        v
MySQL Staging Load (step4_load_staging.py)
        |   - Loads clean CSV into stg_raw_retail staging table
        |   - Bulk insert with validation (row count assertion)
        |
        v
MySQL 8.4 Database (Online_retail)
        |
        ├── Star Schema: fact_sales + 3 dimension tables
        ├── 7 Analytical Views
        ├── Stored Procedure: refresh_rfm
        └── Triggers & Events
        |
        v
Python Pipeline (Consumer360.py)
        |
        ├── Stage 1: Source Validation (Gate 1)
        ├── Stage 2: RFM Segmentation (Gate 2)
        ├── Stage 3: Churn Prediction — Logistic Regression (Gate 3)
        ├── Stage 4: CLV Forecasting — BG/NBD + Gamma-Gamma (Gate 4)
        ├── Stage 5: Customer Merge (Gate 5)
        ├── Stage 6: Basket Analysis — Apriori (Gate 6)
        ├── Stage 7: Cohort Retention (Gate 7)
        └── Stage 8: Output Files (Gate 8)
        |
        v
CSV Outputs + Heatmap PNG
        |
        v
Power BI Dashboard (8 pages + RLS)
        |
        v
Cron Automation (daily at 3:00 PM)
```

---

## File Structure

```
Consumer360 Project/
│
├── basic_EDA.py                # Step 1: EDA, cleaning, exports online_retail_clean.csv
├── step4_load_staging.py       # Step 2: Loads clean CSV into MySQL staging table
├── Consumer360.py              # Step 3: Main pipeline (ETL + ML + quality gates)
├── .env                        # MySQL credentials (excluded from git)
├── .gitignore                  # Ignores .env, logs/, __pycache__/
├── cron_consumer360.sh         # Bash wrapper for cron automation
│
├── mysql/
│   └── online_retail.sql       # Full MySQL dump (tables, views, procedures, triggers)
│
├── consumer360.pbix            # Power BI dashboard (8 pages + RLS)
│
├── Consumer360_ER_Diagram.png      # Database ER diagram
│
├── output/                         # Pipeline-generated outputs
│   ├── rfm_segments.csv            # RFM scores and segment labels per customer
│   ├── clv_predictions.csv         # 12-month CLV forecast per customer
│   ├── basket_rules.csv            # Association rules from Apriori
│   ├── cohort_retention.csv        # Monthly cohort retention matrix
│   ├── churn_risk_list.csv         # At-risk customers (60–180 days inactive)
│   └── cohort_retention_heatmap.png  # Retention heatmap visualization
│
├── docs/
│   ├── project_report.md           # Project report (structured format)
│   ├── project_report_natural.md   # Project report (narrative format)
│   ├── executive_brief.md          # 1-page executive summary
│   ├── executive_deck_outline.md   # 11-slide presentation guide
│   ├── powerbi_setup_guide.md      # Step-by-step Power BI build guide
│   ├── powerbi_fixes_guide.md      # Power BI troubleshooting & fixes
│   └── project_workflow.md         # This file — workflow & file reference
│
└── logs/
    └── pipeline.log            # Timestamped cron execution logs
```

---

## Database Schema

**Fact Table**
- `fact_sales` — 401,604 rows (InvoiceNo, CustomerID, StockCode, Quantity, UnitPrice, TotalAmount, IsReturn, DateId)

**Dimension Tables**
- `dim_customer` — 5,863 rows (CustomerID, Country)
- `dim_date` — 731 rows (DateID, FullDate, Year, Month, Day, Weekday)
- `dim_product` — 3,877 rows (StockCode, Description)

**Views**
- `vw_RFMScores` — RFM raw values and NTILE scores
- `vw_SegmentSummary` — Segment-level aggregations
- `vw_ChurnRiskList` — Customers inactive 60–180 days
- `vw_RevenueTrend` — Monthly revenue with MoM change
- `vw_CohortRetention` — Monthly cohort retention percentages
- `vw_TopProducts` — Best-selling products by revenue
- `vw_CountryRevenue` — Revenue breakdown by country

**Stored Procedure**
- `refresh_rfm` — Recalculates RFM scores using NTILE quintile ranking

---

## Pipeline Stages & Quality Gates

| Stage | Process | Gate Validation |
|-------|---------|-----------------|
| 1 | Connect to MySQL, load fact_sales | Row count > 0, null checks, uniqueness |
| 2 | Calculate RFM scores, assign segments | Scores 1–5, all customers assigned, revenue ranking |
| 3 | Train logistic regression churn model | AUC > 0.60, churn rate within bounds |
| 4 | Fit BG/NBD + Gamma-Gamma, predict CLV | No negative CLV values |
| 5 | Merge RFM + churn + CLV into one table | < 20% customer loss on join |
| 6 | Run Apriori basket analysis | Minimum rule count, all lifts > 1 |
| 7 | Build cohort retention matrix | Percentages 0–100%, M+0 = 100% |
| 8 | Export CSVs and heatmap | All files exist, minimum row counts |

---

## Power BI Dashboard Pages

| Page | Content | Data Source |
|------|---------|-------------|
| 1. Executive Summary | KPI cards, segment donut, country map | rfm_segments.csv, fact_sales |
| 2. RFM Segmentation | Segment comparison, scatter plot | rfm_segments.csv |
| 3. Churn Risk Analysis | Probability histogram, risk donut, customer list | rfm_segments.csv |
| 4. Customer Lifetime Value | CLV distribution, top 20 customers | clv_predictions.csv |
| 5. Basket Analysis | Rules table, confidence vs lift scatter | basket_rules.csv |
| 6. Cohort Retention | Color-coded heatmap matrix | cohort_retention.csv |
| 7. Revenue Trends | Monthly line chart, MoM %, country treemap | vw_RevenueTrend |
| 8. What-If Simulation | Re-engagement slider, projected revenue | rfm_segments.csv + DAX |

---

## Automation

- **Schedule:** Daily at 3:00 PM via crontab (`0 15 * * *`)
- **Wrapper:** `cron_consumer360.sh` runs the pipeline with logging
- **Logging:** `logs/pipeline.log` with timestamps and exit codes
- **Error handling:** `sys.exit(1)` on gate failure for cron alerting
- **Credentials:** `.env` file loaded by python-dotenv

---

## Technology Stack

| Layer | Technology |
|-------|-----------|
| Database | MySQL 8.4 |
| ETL & ML | Python 3.14 (pandas, scikit-learn, lifetimes, mlxtend) |
| Visualization | Power BI Desktop |
| Automation | Cron + Bash |
| Security | python-dotenv, Power BI RLS |
| Version Control | Git + GitHub |
