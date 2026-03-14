# Consumer360 — Project Report
**Retail Analytics: Customer Segmentation & Lifetime Value Engine**

Squadron Beta | Infotact Solutions | March 2026

---

## Problem Statement & Objectives

A national retail chain is losing customers without knowing why. The business has no clear picture of which customers are high-value, which are slipping away, and what products to recommend for cross-selling. Marketing campaigns go out untargeted — money is wasted on low-value customers while high-value ones go unnoticed.

This project set out to fix that. We built an end-to-end analytics pipeline that segments customers using RFM scoring, predicts churn probability with machine learning, forecasts 12-month Customer Lifetime Value, discovers product bundles through association rule mining, and tracks retention across monthly cohorts. The entire pipeline is automated with quality gates and scheduled execution, feeding into an interactive Power BI dashboard with Row Level Security for regional managers.

The dataset comes from the UCI Machine Learning Repository's Online Retail dataset — 401,604 transactions from 5,863 unique customers across 3,877 products and 25 countries, spanning December 2009 through December 2011. The United Kingdom accounts for 82% of total revenue.

---

## Architecture & Methodology

The data lives in a MySQL 8.4 star schema. At the center is `fact_sales` with 401,604 rows linking to three dimension tables: `dim_customer` (5,863 rows), `dim_date` (731 rows), and `dim_product` (3,877 rows). Seven analytical views power the segmentation, churn, revenue trend, and cohort analyses. A stored procedure (`refresh_rfm`) handles NTILE-based RFM scoring with quintile ranking.

The Python pipeline (`Consumer360.py`) connects to MySQL, pulls the data, and runs through eight sequential stages — each guarded by an automated quality gate. If any gate fails, the pipeline halts immediately with a descriptive error and non-zero exit code. The gates validate source data integrity, segmentation correctness, model performance (AUC > 0.60), CLV validity, merge integrity, association rule quality, retention matrix bounds, and output file completeness.

The technology stack pairs MySQL 8.4 for storage and views with Python 3.14 for ETL and machine learning (pandas, scikit-learn, lifetimes, mlxtend). Power BI Desktop provides the interactive dashboard layer. Automation runs through cron with a bash wrapper script (`cron_consumer360.sh`) that handles logging and exit codes. Credentials are managed securely through python-dotenv and a `.env` file excluded from version control.

---

## Key Findings

**Customer Segmentation.** RFM scoring divided the customer base into four segments. Champions make up just 10% of customers (586) but generate the highest average revenue at 8,854 and the highest predicted CLV at 369. Loyalists represent 22.8% (1,338 customers) with solid engagement. At Risk customers account for 19.6% (1,146) with an average recency of 354 days — they're fading fast. The largest group, Hibernating, comprises 47.6% of the base (2,793 customers) with minimal engagement and an average revenue of just 436.

**Churn Prediction.** A logistic regression model (L2 regularized, C=0.1) predicts churn probability for every customer, with churn defined as no purchase in 90+ days. Features include raw and scored Frequency and Monetary values — Recency was excluded to prevent data leakage. The model achieves an ROC-AUC above 0.60. Of the full base, 54.8% fall in the low-risk category, 23.2% are medium risk, and 22.0% are high risk. We flagged 1,101 customers inactive for 60–180 days as prime candidates for win-back campaigns.

**Customer Lifetime Value.** Using BG/NBD for purchase frequency and Gamma-Gamma for monetary value, we estimated 12-month CLV for the 4,244 repeat customers (72.4% of the base). The average predicted CLV is 199.87, with the highest individual value reaching 129,069 (Customer 16446). The remaining 1,619 single-purchase customers lack sufficient transaction history for reliable CLV estimation.

**Basket Analysis.** The Apriori algorithm (minimum support 2%, minimum lift 1.5) uncovered 60 association rules. The strongest pairing — Teacup Regency Green with Teacup Regency Roses — has 80% confidence and a lift of 27.41x, meaning customers are 27 times more likely to buy both together than by chance. Other strong pairs include the Sweetheart Ceramic Trinket Box with Strawberry Ceramic Trinket Pot (73% confidence, 14.22x lift) and Wooden Frame Antique White with Wooden Picture Frame White Finish (60% confidence, 12.43x lift).

**Cohort Retention.** Tracking 25 monthly cohorts reveals a consistent pattern: first-month retention ranges from 14–35%, meaning 65–86% of new customers drop off after their first month. Retention stabilizes around 10–25% by month three. The December 2009 cohort (954 customers) performed best with 49% retention at month 11, while December 2010 (163 customers) performed worst at just 5% by month five.

---

## Dashboard & Automation

The Power BI dashboard spans eight pages. The Executive Summary presents KPI cards (17.21M revenue, 6K customers, 37K orders), a segment donut chart, and a country map. Dedicated pages cover RFM Segmentation, Churn Risk Analysis (with a probability histogram and the 1,101 at-risk customer list), CLV distribution and top customers, Basket Analysis rules with a confidence-vs-lift scatter plot, Cohort Retention as a color-coded heatmap matrix, and Revenue Trends with month-over-month changes and a country treemap. The final page offers a What-If Simulation where stakeholders can adjust a re-engagement slider to see projected revenue recovery.

Row Level Security restricts data access across three roles: UK Manager sees only United Kingdom data, Europe Manager sees 13 European countries, and Rest of World covers Australia, Japan, USA, Canada, and others.

The pipeline runs daily at 3:00 PM via cron. A bash wrapper script (`cron_consumer360.sh`) manages logging to `logs/pipeline.log` with timestamps and exit codes. The Python pipeline uses try/except/finally with `sys.exit(1)` so cron can detect and alert on failures. All eight quality gates run sequentially — any single failure stops the pipeline before bad data reaches the dashboard.

---

## Strategic Recommendations

**Retain Champions.** These 586 customers generate an average revenue of 8,854 each. A VIP loyalty program with early product access, personalized offers, and dedicated account management would protect this critical revenue base. Losing even 10% of Champions would be significant.

**Win Back At-Risk Customers.** The 1,101 customers flagged at 60–180 days of inactivity still have meaningful purchase history. Targeted re-engagement campaigns prioritized by historical revenue could recover substantial value. The What-If simulation estimates that re-engaging just 20% of at-risk customers could recover approximately 411K in revenue.

**Activate High-CLV Hibernating Customers.** Not all Hibernating customers are equal. Using CLV scores to identify those with above-average predicted lifetime value and targeting them with deep discounts — while deprioritizing low-CLV Hibernating customers — would optimize marketing spend.

**Implement Cross-Sell Bundles.** The 60 association rules translate directly into product page recommendations and bundle deals. The Teacup Regency pair (27x lift) is a strong candidate for immediate promotion, with an expected increase in average order value.

**Fix First-Month Retention.** The 65–86% first-month drop-off is the single biggest leakage point. A structured post-purchase email sequence — order confirmation, usage tips, feedback request, next-purchase incentive — would address this across all cohorts.

**Shift to Value-Based Acquisition.** CLV profiles enable lookalike audience modeling for customer acquisition. Focusing spend on profiles matching Champions and Loyalists, rather than broad targeting, shifts marketing from volume-based to value-based.

