# Consumer360 — Retail Analytics Pipeline

An end-to-end customer analytics pipeline that segments customers using RFM scoring, predicts churn with machine learning, forecasts 12-month Customer Lifetime Value, discovers cross-sell product bundles, and tracks cohort retention — all automated with quality gates and feeding into an interactive Power BI dashboard.

## Key Results

| Metric                      | Value                                          |
| --------------------------- | ---------------------------------------------- |
| Customers Analyzed          | 5,863                                          |
| Transactions Processed      | 401,604                                        |
| RFM Segments                | 4 (Champions, Loyalists, At Risk, Hibernating) |
| Churn Model AUC             | > 0.60                                         |
| At-Risk Customers Flagged   | 1,101                                          |
| Cross-Sell Rules Discovered | 60                                             |
| Monthly Cohorts Tracked     | 25                                             |
| Automated Quality Gates     | 8                                              |

## Architecture

```
Raw CSV → EDA & Cleaning → MySQL Star Schema → Python Pipeline → CSV Outputs → Power BI Dashboard
                                                     |
                                              8 Quality Gates
                                                     |
                                              Cron Automation
```

### Tech Stack

- **Database:** MySQL 8.4 (star schema, views, stored procedures)
- **ETL & ML:** Python 3.14 (pandas, scikit-learn, lifetimes, mlxtend)
- **Visualization:** Power BI Desktop (8 pages + Row Level Security)
- **Automation:** Cron + Bash (daily at 3:00 PM)
- **Security:** python-dotenv for credential management

## Project Structure

```
├── basic_EDA.py                # Data cleaning and exploratory analysis
├── step4_load_staging.py       # Load clean data into MySQL staging table
├── Consumer360.py              # Main pipeline — ETL, ML models, quality gates
├── cron_consumer360.sh         # Cron wrapper with logging
├── requirements.txt            # Python dependencies
├── .env.example                # Credential template
│
├── mysql/
│   └── online_retail.sql       # Full database dump (tables, views, procedures)
│
├── output/                     # Pipeline outputs (generated on each run)
│   ├── rfm_segments.csv
│   ├── clv_predictions.csv
│   ├── basket_rules.csv
│   ├── cohort_retention.csv
│   ├── churn_risk_list.csv
│   └── cohort_retention_heatmap.png
│
├── consumer360.pbix            # Power BI dashboard
├── Consumer360_ER_Diagram.png  # Database schema diagram
│
└── docs/
    ├── project_report.md       # Full project report
    ├── executive_brief.md      # 1-page executive summary
    ├── project_workflow.md     # Workflow & file reference
    └── executive_deck_outline.md  # Presentation guide
```

## Setup

### Prerequisites

- Python 3.10+
- MySQL 8.0+
- Power BI Desktop (Windows)

### Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/Miko0115/Consumer360.git
   cd Consumer360
   ```
2. **Install Python dependencies**

   ```bash
   pip install -r requirements.txt
   ```
3. **Set up MySQL database**

   ```bash
   mysql -u root -p < mysql/online_retail.sql
   ```
4. **Configure credentials**

   ```bash
   cp .env.example .env
   # Edit .env with your MySQL credentials
   ```
5. **Run the pipeline**

   ```bash
   python Consumer360.py
   ```

### Cron Automation (Optional)

```bash
crontab -e
# Add:
0 15 * * * /path/to/cron_consumer360.sh
```

## Pipeline Stages & Quality Gates

| Stage | Process                                | Gate Check                       |
| ----- | -------------------------------------- | -------------------------------- |
| 1     | Source data validation                 | Row count, nulls, uniqueness     |
| 2     | RFM segmentation                       | Score ranges 1–5, full coverage |
| 3     | Churn prediction (Logistic Regression) | AUC = 0.70                       |
| 4     | CLV forecasting (BG/NBD + Gamma-Gamma) | No negative values               |
| 5     | Customer data merge                    | < 20% customer loss              |
| 6     | Basket analysis (Apriori)              | Min rules, lift > 1              |
| 7     | Cohort retention matrix                | Percentages 0–100%              |
| 8     | Output file validation                 | Files exist, min row counts      |

If any gate fails, the pipeline halts with a descriptive error and non-zero exit code.

## Power BI Dashboard

8-page interactive dashboard with Row Level Security:

1. **Executive Summary** — KPIs, segment breakdown, country map
2. **RFM Segmentation** — Segment comparison and scatter plot
3. **Churn Risk** — Probability distribution, at-risk customer list
4. **Customer Lifetime Value** — CLV distribution, top 20 customers
5. **Basket Analysis** — Association rules, confidence vs lift
6. **Cohort Retention** — Color-coded retention heatmap
7. **Revenue Trends** — Monthly trends, MoM change, country treemap
8. **What-If Simulation** — Re-engagement scenario modeling

### RLS Roles

| Role           | Access                              |
| -------------- | ----------------------------------- |
| UK Manager     | United Kingdom only                 |
| Europe Manager | 13 European countries               |
| Rest of World  | Australia, Japan, USA, Canada, etc. |

## Sample Output

Pipeline generates 5 CSVs and a heatmap in `output/`.

### rfm_segments.csv

Master customer file — one row per customer with segment, churn probability, and CLV.

| CustomerID | Country        | Segment     | R_Raw | F_Raw |  M_Raw | R_Score | F_Score | M_Score | RFM_Score | ChurnProbability | CLV_12months |
| ---------- | -------------- | ----------- | ----: | ----: | -----: | ------: | ------: | ------: | --------: | ---------------: | -----------: |
| 15729      | United Kingdom | Hibernating |   212 |     3 | 192.55 |       2 |       3 |       1 |         6 |           0.5848 |        32.05 |
| 14768      | United Kingdom | Hibernating |    17 |     2 | 192.60 |       5 |       3 |       1 |         9 |           0.5909 |       128.73 |
| 12522      | Germany        | Hibernating |    39 |     2 | 192.72 |       4 |       3 |       1 |         8 |           0.5909 |        84.17 |

### clv_predictions.csv

12-month lifetime value forecast for repeat customers.

| CustomerID | Frequency | Recency (wks) | T (wks) | Avg Order Value | Predicted Purchases | CLV 12mo |
| ---------- | --------: | ------------: | ------: | --------------: | ------------------: | -------: |
| 12346      |        11 |         57.14 |  103.57 |        2,281.07 |                0.93 | 1,997.70 |
| 12347      |         7 |         57.43 |   57.71 |           22.17 |                6.03 |   128.23 |
| 12348      |         4 |         51.86 |   62.57 |           39.60 |                3.44 |   130.52 |

### basket_rules.csv

Cross-sell product pairs from Apriori association rule mining.

| Antecedent                     | Consequent                     | Support | Confidence |  Lift |
| ------------------------------ | ------------------------------ | ------: | ---------: | ----: |
| Teacup Regency Roses           | Teacup Regency Green           |   2.05% |      70.5% | 27.4x |
| Teacup Regency Green           | Teacup Regency Roses           |   2.05% |      79.7% | 27.4x |
| Sweetheart Ceramic Trinket Box | Strawberry Ceramic Trinket Pot |   2.33% |      73.2% | 14.2x |

### cohort_retention.csv

Monthly retention percentages by acquisition cohort.

| CohortSize | M+(0) | M+(1) | M+(2) | M+(3) | M+(4) | M+(5) | M+(6) | M+(7) | M+(8) | M+(9) | M+(10) | M+(11) |
| ---------: | ----: | ----: | ----: | ----: | ----: | ----: | ----: | ----: | ----: | ----: | -----: | -----: |
|        954 |   100 | 35.22 | 33.23 | 42.45 | 37.95 | 35.85 | 37.74 | 34.28 | 33.65 | 36.06 |  42.03 |  49.48 |
|        382 |   100 | 20.68 | 31.15 | 30.63 | 26.44 | 30.10 | 25.92 | 23.04 | 28.01 | 31.68 |  30.10 |  17.28 |
|        375 |   100 | 24.00 | 22.67 | 29.33 | 24.53 | 19.73 | 19.20 | 28.80 | 25.60 | 27.73 |  11.47 |  12.53 |

### churn_risk_list.csv

High-value customers inactive 60–180 days — win-back campaign targets.

| CustomerID | Country        | Segment   | Days Inactive | Revenue | Churn Prob |
| ---------- | -------------- | --------- | ------------: | ------: | ---------: |
| 18251      | United Kingdom | Loyalists |            87 |  26,279 |       0.17 |
| 13802      | United Kingdom | Loyalists |           138 |  26,259 |       0.14 |
| 12939      | United Kingdom | Loyalists |            64 |  25,265 |       0.13 |

---

## Dataset

UCI Machine Learning Repository — [Online Retail Dataset](https://archive.ics.uci.edu/dataset/352/online+retail)

- 401,604 transactions | 5,863 customers | 3,877 products | 25 countries
- Date range: December 2009 – December 2011
