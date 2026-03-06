# Consumer360 End-to-End Architecture Design

**Date:** 2026-03-02
**Status:** Approved

## Overview

Consumer360 is a retail analytics pipeline that processes ~800K e-commerce transactions through RFM segmentation, churn prediction, CLV modeling, basket analysis, and cohort retention analysis. This document defines the end-to-end architecture for a local, single-machine deployment with cron-based scheduling.

## Architecture Decision

**Chosen approach:** Linear Orchestrator — a Python `orchestrator.py` that runs modular pipeline steps sequentially, with retry logic, JSON state tracking, and per-run logging.

**Why:** At ~800K rows, a simple sequential orchestrator provides everything needed (retry, resume, logging) without the complexity of a workflow framework like Airflow or Prefect.

## Project Structure

```
Consumer360 Project/
├── config.py                     # Centralized DB credentials, paths, constants
├── orchestrator.py               # Main entry point — runs all steps in sequence
├── pipeline/
│   ├── __init__.py
│   ├── step1_clean_data.py       # Load raw CSV → clean → save cleaned CSV
│   ├── step2_load_staging.py     # Load cleaned CSV → MySQL staging table
│   ├── step3_build_warehouse.py  # Create star schema (fact + dimension tables)
│   ├── step4_create_views.py     # Create SQL views (SingleCustomerView, cohort, basket)
│   ├── step5_rfm_segmentation.py # RFM scoring and customer segments
│   ├── step6_churn_model.py      # Logistic regression churn prediction
│   ├── step7_clv_model.py        # BG/NBD + Gamma-Gamma CLV forecast
│   ├── step8_basket_analysis.py  # Apriori association rules
│   ├── step9_cohort_analysis.py  # Cohort retention metrics
│   └── step10_export.py          # Export results to CSV/Excel
├── utils/
│   ├── __init__.py
│   ├── db.py                     # Database connection factory (SQLAlchemy engine)
│   ├── logger.py                 # Logging setup (file + console)
│   └── validation.py             # Data quality checks
├── exports/                      # Output CSV/Excel files (gitignored)
├── logs/                         # Log files per run (gitignored)
├── online_retail.csv             # Raw data (gitignored)
├── online_retail.clean.csv       # Cleaned data (gitignored)
└── requirements.txt              # Python dependencies
```

Each `pipeline/step*.py` module exposes a single `run(engine, logger)` function.

## Pipeline Steps & Data Flow

```
Raw CSV → [Step 1] → Cleaned CSV → [Step 2] → stg_raw_retail (MySQL)
                                                     │
                                                [Step 3]
                                                     │
                                        ┌────────────┼────────────┐
                                        ▼            ▼            ▼
                                   dim_customer  dim_product  dim_date
                                        │            │            │
                                        └────────┬───┘────────────┘
                                                 ▼
                                            fact_sales
                                                 │
                                            [Step 4]
                                                 │
                                        ┌────────┼────────┐
                                        ▼        ▼        ▼
                               vw_SingleCustomer  vw_Cohort  vw_ProductBasket
                                        │        │          │
                        ┌───────────────┤        │          │
                        ▼               ▼        ▼          ▼
                   [Step 5]        [Step 6]  [Step 9]   [Step 8]
                   RFM Scores     Churn Pred  Cohort    Basket Rules
                        │               │      │          │
                        ▼               ▼      ▼          ▼
                   [Step 7]        MySQL tables + result DataFrames
                   CLV Forecast          │
                        │                │
                        └────────┬───────┘
                                 ▼
                            [Step 10]
                            Export CSVs
```

### Step Details

| Step | Input | Output | Validation |
|------|-------|--------|------------|
| 1. Clean Data | `online_retail.csv` | `online_retail.clean.csv` | Row count > 0, no nulls in key columns, positive Quantity/UnitPrice |
| 2. Load Staging | Cleaned CSV | `stg_raw_retail` table | Row count matches CSV, schema matches expected types |
| 3. Build Warehouse | `stg_raw_retail` | `fact_sales`, `dim_customer`, `dim_product`, `dim_date` | FK integrity, no orphan records, row counts |
| 4. Create Views | Star schema tables | SQL views for analytics | Views queryable, return > 0 rows |
| 5. RFM Segmentation | `vw_SingleCustomerView` | `rfm_segments` table | All customers scored, segments sum to total |
| 6. Churn Model | `rfm_segments` | `churn_predictions` table | Probabilities 0-1, AUC > 0.5, all customers scored |
| 7. CLV Model | `vw_SingleCustomerView` | `clv_predictions` table | CLV values >= 0, model convergence check |
| 8. Basket Analysis | `vw_ProductBasket` | `basket_rules` table | Support/confidence within valid ranges |
| 9. Cohort Analysis | `vw_Cohort` | `cohort_retention` table | Retention rates 0-100%, no gaps in cohort months |
| 10. Export | All result tables | CSVs in `exports/` | Files created, non-empty, headers match |

## Orchestrator Design

### Execution Flow

1. Load config (DB credentials, file paths)
2. Set up logging (timestamped log file + console output)
3. Create SQLAlchemy engine
4. Run steps 1-10 in sequence, each wrapped in retry logic
5. On completion, print summary (steps run, time elapsed, pass/fail)

### Retry Logic

```
For each step:
  Try run(engine, logger)
  If fails → log error → wait 5 seconds → retry once
  If fails again → log fatal → halt pipeline → exit with non-zero code
```

### CLI Interface

```bash
python orchestrator.py                    # Run full pipeline
python orchestrator.py --from-step 5      # Resume from step 5
python orchestrator.py --only-step 3      # Run only step 3
python orchestrator.py --dry-run          # Show what would run without executing
python orchestrator.py --list             # List all steps and their status
```

### State Tracking

- `pipeline_state.json` records which steps completed, when, and their row counts
- `--from-step` uses this to skip already-completed steps
- State resets when source data changes (detected via file hash)

### Logging

- One log file per run: `logs/pipeline_YYYYMMDD_HHMMSS.log`
- Each step logs: start time, key metrics (row counts), validation results, end time
- Console shows progress with step name and status

## Validation Framework

Reusable validation functions in `utils/validation.py`:

| Check | Description | Used After |
|-------|-------------|------------|
| `check_row_count(df, min_rows)` | Assert DataFrame has at least N rows | Every step |
| `check_no_nulls(df, columns)` | Assert specified columns have no nulls | Steps 1-5 |
| `check_positive_values(df, columns)` | Assert numeric columns > 0 | Steps 1-2 |
| `check_value_range(df, column, min, max)` | Assert values within expected range | Steps 5-9 |
| `check_unique(df, columns)` | Assert no duplicates on key columns | Steps 3-4 |
| `check_schema(df, expected_dtypes)` | Assert column names and types match | Every step |
| `check_referential_integrity(engine, fk_query)` | Assert no orphan foreign keys | Step 3 |
| `check_segments_complete(df, segment_col)` | Assert all expected segments present | Step 5 |

On validation failure: log the specific check that failed with details (expected vs actual), raise `ValidationError`, which the orchestrator catches as a step failure (triggering retry).

## Configuration

`config.py` centralizes all settings:

- **Database:** host, port, user, password (env var `CONSUMER360_DB_PASSWORD` with hardcoded fallback), database name
- **File paths:** raw CSV, cleaned CSV, export directory, log directory
- **Analytics parameters:** churn threshold (90 days), CLV horizon (52 weeks), RFM quantiles (4), Apriori min support (0.01), min confidence (0.3)

## Export Outputs

| File | Contents |
|------|----------|
| `rfm_segments.csv` | CustomerID, R/F/M scores, segment label |
| `churn_predictions.csv` | CustomerID, churn probability, churn label |
| `clv_predictions.csv` | CustomerID, predicted purchases, predicted CLV |
| `basket_rules.csv` | Antecedent, consequent, support, confidence, lift |
| `cohort_retention.csv` | Cohort month, period, retention rate |
| `pipeline_summary.xlsx` | Multi-sheet Excel with all above + summary stats |

## Scheduling

Cron (Linux):
```cron
0 2 * * 0 cd /run/media/miko/Autumn/Consumer360\ Project && /path/to/python orchestrator.py >> logs/cron.log 2>&1
```

Windows Task Scheduler: scheduled task pointing to `python orchestrator.py` with working directory set to the project root.

## Technology Stack

| Layer | Technology |
|-------|-----------|
| Data Source | Online Retail CSV (~800K rows) |
| Database | MySQL (Online_retail) |
| Processing | Python 3.10, pandas, numpy, SQLAlchemy |
| ML/Analytics | scikit-learn, lifetimes, mlxtend, XGBoost |
| Visualization | Power BI (connects to MySQL + exported files) |
| Scheduling | Cron / Task Scheduler |
| Version Control | Git |
