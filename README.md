# Consumer360 — Retail Analytics Pipeline

An end-to-end customer analytics pipeline that segments customers using RFM scoring, predicts churn with machine learning, forecasts 12-month Customer Lifetime Value, discovers cross-sell product bundles, and tracks cohort retention — all automated with quality gates and feeding into an interactive Power BI dashboard.

## Key Results

| Metric | Value |
|--------|-------|
| Customers Analyzed | 5,863 |
| Transactions Processed | 401,604 |
| RFM Segments | 4 (Champions, Loyalists, At Risk, Hibernating) |
| Churn Model AUC | > 0.60 |
| At-Risk Customers Flagged | 1,101 |
| Cross-Sell Rules Discovered | 60 |
| Monthly Cohorts Tracked | 25 |
| Automated Quality Gates | 8 |

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
   git clone https://github.com/your-username/Consumer360.git
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

| Stage | Process | Gate Check |
|-------|---------|------------|
| 1 | Source data validation | Row count, nulls, uniqueness |
| 2 | RFM segmentation | Score ranges 1–5, full coverage |
| 3 | Churn prediction (Logistic Regression) | AUC > 0.60 |
| 4 | CLV forecasting (BG/NBD + Gamma-Gamma) | No negative values |
| 5 | Customer data merge | < 20% customer loss |
| 6 | Basket analysis (Apriori) | Min rules, lift > 1 |
| 7 | Cohort retention matrix | Percentages 0–100% |
| 8 | Output file validation | Files exist, min row counts |

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

| Role | Access |
|------|--------|
| UK Manager | United Kingdom only |
| Europe Manager | 13 European countries |
| Rest of World | Australia, Japan, USA, Canada, etc. |

## Dataset

UCI Machine Learning Repository — [Online Retail Dataset](https://archive.ics.uci.edu/dataset/352/online+retail)

- 401,604 transactions | 5,863 customers | 3,877 products | 25 countries
- Date range: December 2009 – December 2011

