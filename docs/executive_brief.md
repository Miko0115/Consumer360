# Consumer360 — Executive Brief

**Customer Intelligence Platform | Online Retail Dataset | Dec 2009 - Dec 2011**

---

## Overview

Consumer360 is an automated customer analytics pipeline that transforms raw transactional data into actionable segmentation, churn predictions, lifetime value forecasts, and cross-sell recommendations. The pipeline runs daily at 3:00 PM via cron, validated by 8 automated quality gates.

---

## Key Figures

| Metric                        | Value             |
|-------------------------------|-------------------|
| Total Customers               | 5,863             |
| Total Transactions            | 401,604           |
| Countries                     | 41                |
| Products                      | 3,877             |
| Repeat Customers (CLV-eligible)| 4,244 (72.4%)    |
| At-Risk Customers (60-180 days)| 1,101            |
| Association Rules Discovered  | 60                |
| Monthly Cohorts Tracked       | 25                |
| Churn Threshold               | 90 days           |
| Pipeline Quality Gates        | 8 (all passing)   |

---

## Customer Segmentation (RFM)

Customers are scored on Recency, Frequency, and Monetary value (1-5 each) and classified into four segments:

| Segment      | Description                          | Action                              |
|--------------|--------------------------------------|-------------------------------------|
| Champions    | Recent, frequent, high-spend buyers  | VIP loyalty program, early access   |
| Loyalists    | Consistent mid-high spenders         | Upsell, referral programs           |
| At Risk      | Previously active, now fading        | Win-back campaigns, targeted offers |
| Hibernating  | Inactive, low frequency/spend        | Deep discounts or deprioritize      |

Champions rank highest in average revenue per customer, confirming the scoring logic is correct.

---

## Churn Prediction

- **Model:** Logistic Regression (L2, C=0.1)
- **ROC-AUC:** > 0.60 (Gate 3 enforced)
- **Churn Definition:** No purchase in 90+ days
- **Features:** F_Raw, M_Raw, F_Score, M_Score (R_Raw excluded to prevent data leakage)
- **Output:** Every customer receives a ChurnedProbability score (0 to 1)
- **1,101 at-risk customers** flagged (60-180 days since last purchase), prioritized by total revenue

---

## Customer Lifetime Value (CLV)

- **Models:** BG/NBD (purchase frequency) + Gamma-Gamma (monetary value)
- **Scope:** 4,244 repeat customers
- **Forecast:** 12-month CLV per customer
- **Single-purchase customers** (1,619) receive no CLV estimate — insufficient behavioral data

CLV enables prioritized acquisition spend and identifies high-value customers for retention investment.

---

## Basket Analysis (Cross-Sell)

- **Method:** Apriori algorithm (min support 2%, min lift 1.5)
- **60 rules discovered**, top pairs:

| Product A                        | Product B                        | Confidence | Lift   |
|----------------------------------|----------------------------------|------------|--------|
| Teacup & Saucer Regency Roses   | Teacup & Saucer Regency Green   | 70.5%      | 27.41  |
| Sweetheart Ceramic Trinket Box   | Strawberry Ceramic Trinket Pot   | 73.2%      | 14.22  |

A lift of 27x means customers are 27 times more likely to buy both items together than by chance. These rules directly inform bundle promotions and product recommendations.

---

## Cohort Retention

- **25 monthly cohorts** (Dec 2009 - Dec 2011)
- **First-month retention:** 9-35% across cohorts (65-91% drop-off)
- **Stabilization:** ~10-25% by month 3
- **Best cohort:** Dec 2009 (954 customers) — 49.48% retention at month 11

The steep first-month drop signals an opportunity for post-purchase follow-up campaigns.

---

## Data Quality & Automation

The pipeline enforces 8 sequential gates before any output is written:

1. Source validation (row count, nulls, uniqueness)
2. Segmentation validation (score ranges, segment coverage, revenue ranking)
3. Churn model validation (AUC threshold, churn rate bounds)
4. CLV validation (no negative values)
5. Merge reconciliation (< 20% customer loss)
6. Basket analysis validation (rule count, lift > 1)
7. Retention validation (0-100% range, month 0 = 100%)
8. Output file validation (file existence, minimum row counts)

**Automation:** Cron-scheduled daily at 3:00 PM. Credentials secured via .env. Non-zero exit code on failure for alerting.

---

## Strategic Recommendations

1. **Retain Champions** — VIP program, personalized offers, early access to new products
2. **Win back At-Risk customers** — Target the 1,101 flagged customers with re-engagement campaigns, prioritized by revenue
3. **Activate Hibernating segment** — Deep discounts for high-CLV hibernators; deprioritize low-CLV ones
4. **Bundle top basket pairs** — Implement the 60 association rules as product page recommendations and bundle deals
5. **Fix first-month retention** — Post-purchase email sequence to address the 65-91% first-month drop-off
6. **Invest by CLV** — Use CLV scores to allocate acquisition budget toward high-value lookalike audiences
