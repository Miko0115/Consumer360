import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, roc_auc_score
from lifetimes import BetaGeoFitter, GammaGammaFitter
from mlxtend.frequent_patterns import apriori, association_rules
from mlxtend.preprocessing import TransactionEncoder
# from utils.validation import check_row_count, check_value_range
import os
import sys
import warnings
warnings.filterwarnings("ignore")


load_dotenv()
DB_URL          = os.getenv("DB_URL")
CHURN_THRESHOLD = 90
MIN_SUPPORT     = 0.02
MIN_LIFT        = 1.5
OUTPUT_DIR      = "/run/media/miko/Autumn/Consumer360 Project/output/"


try:
    engine = create_engine(DB_URL, pool_pre_ping=True)
    print("Connected to MySQL")


    df_rfm = pd.read_sql("SELECT * FROM vw_SingleCustomerView", con=engine)

    # Gate 1: Source validation
    if len(df_rfm) < 1000:
        raise ValueError(f"Gate 1 FAILED: Too few customers {len(df_rfm)}")
    if df_rfm["CustomerID"].isna().any():
        raise ValueError("Gate 1 FAILED: Null CustomerIDs")
    if not df_rfm["CustomerID"].is_unique:
        raise ValueError("Gate 1 FAILED: Duplicate CustomerIDs")
    for col in ["R_Raw", "F_Raw", "M_Raw", "R_Score", "F_Score", "M_Score"]:
        if df_rfm[col].isna().any():
            raise ValueError(f"Gate 1 FAILED: Nulls in {col}")
    print("Gate 1 PASSED: Source validated")

    print(f"{len(df_rfm):} customers_loaded")


    def assign_segment(row):
        r, f, m = row["R_Score"], row["F_Score"], row["M_Score"]

        if r >= 4 and f >= 4 and m >= 4:
            return "Champions"
        elif r <= 2 and f >= 3 and m >= 3:
            return "At Risk"
        elif f >= 3 and m >= 3:
            return "Loyalists"
        else:
            return "Hibernating"

    df_rfm["Segment"] = df_rfm.apply(assign_segment, axis=1)
    print(df_rfm["Segment"].value_counts().to_string())
    print(f"Total Segments: {df_rfm['Segment'].nunique()} (Champions / Loyalists / At Risk/ Hibernating)")

    # Customer Segmentation Validation
    segment_audit = df_rfm.groupby("Segment").agg(
        CustomerCount = ("CustomerID", "count"),
        AvgRecency = ("R_Raw", "mean"),
        AvgFrequency = ("F_Raw", "mean"),
        AvgRevenue = ("M_Raw", "mean")
    ).round(2).sort_values("AvgRevenue", ascending=False)

    print(segment_audit.to_string())

    # Gate 2: Segmentation validation
    for col in ["R_Score", "F_Score", "M_Score"]:
        if not df_rfm[col].between(1, 5).all():
            raise ValueError(f"Gate 2 FAILED: {col} outside range 1-5")
    if df_rfm["Segment"].isna().any():
        raise ValueError("Gate 2 FAILED: Customers without segments")
    expected = {"Champions", "Loyalists", "At Risk", "Hibernating"}
    missing = expected - set(df_rfm["Segment"].unique())
    if missing:
        raise ValueError(f"Gate 2 FAILED: Missing segments: {missing}")
    if segment_audit.index[0] != "Champions":
        raise ValueError(f"Gate 2 FAILED: Champions not top revenue - got {segment_audit.index[0]}")
    print("Gate 2 PASSED: Segmentation validated")

    # Logistic Regression
    df_rfm["Churned"] = (df_rfm["R_Raw"] > CHURN_THRESHOLD).astype(int)
    churn_rate = df_rfm["Churned"].mean()

    print(df_rfm["Churned"])
    print(f"Churn threshold: R_Raw > {CHURN_THRESHOLD} days")
    print(f"Churned(1): {df_rfm['Churned'].sum():,}")
    print(f"Active(0): {(df_rfm['Churned']==0).sum():,}")
    print(f"Churn rate: {churn_rate:.1%}")

    features = ["F_Raw", "M_Raw", "F_Score", "M_Score"]
    X = df_rfm[features]
    y = df_rfm["Churned"]

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    X_train, X_test, y_train, y_test = train_test_split(
        X_scaled, y, test_size=0.2, random_state=42, stratify=y
    )

    lr = LogisticRegression(C=0.1, solver="lbfgs", max_iter=1000, random_state=42)
    lr.fit(X_train, y_train)

    y_pred = lr.predict(X_test)
    y_pred_proba = lr.predict_proba(X_test)[:, 1]
    auc = roc_auc_score(y_test, y_pred_proba)

    print(classification_report(y_test, y_pred, target_names=["Active", "Churned"]))
    print(f"ROC-AUC Score: {auc:.4f}")

    df_rfm["ChurnedProbability"] = lr.predict_proba(
        scaler.transform(df_rfm[features])
    )[:, 1].round(4)

    print(df_rfm)

    # Gate 3: Churn model validation
    if not (0.05 <= churn_rate <= 0.80):
        raise ValueError(f"Gate 3 FAILED: Churn rate extreme ({churn_rate:.1%})")
    if auc <= 0.6:
        raise ValueError(f"Gate 3 FAILED: AUC too low ({auc:.4f})")
    if not df_rfm["ChurnedProbability"].between(0, 1).all():
        raise ValueError(f"Gate 3 FAILED: Churn probability outside [0,1]")
    print(f"Gate 3 PASSED: AUC={auc:.4f}, churn rate={churn_rate:.1%}")

    # CLV Prediction
    clv_data = pd.read_sql("""
                           SELECT
                                f.CustomerID,
                                COUNT(DISTINCT f.InvoiceNo) - 1 AS frequency,
                                DATEDIFF(MAX(d.FullDate), MIN(d.FullDate)) / 7.0 AS recency,
                                DATEDIFF(
                                    (SELECT MAX(FullDate) FROM dim_date),
                                    MIN(d.FullDate)
                                ) / 7.0 AS T,
                                AVG(f.TotalAmount) AS avg_order_value
                           FROM fact_sales f JOIN dim_date d ON f.DateId=d.DateId
                           GROUP BY f.CustomerID
                           HAVING frequency > 0
    """, con=engine)

    print(clv_data)
    print(f"{len(clv_data)}: customers")

    bgf = BetaGeoFitter(penalizer_coef=0.01)
    bgf.fit(clv_data["frequency"], clv_data["recency"], clv_data["T"])

    clv_data["predicted_purchase_1yr"] = bgf.conditional_expected_number_of_purchases_up_to_time(
                                                52, clv_data["frequency"], clv_data["recency"], clv_data["T"]
    ).round(2)

    repeat_customers = clv_data[clv_data["frequency"] > 1].copy()
    ggf = GammaGammaFitter(penalizer_coef=0.01)
    ggf.fit(repeat_customers["frequency"], repeat_customers["avg_order_value"])

    clv_values = ggf.customer_lifetime_value(
        bgf,
        clv_data["frequency"],
        clv_data["recency"],
        clv_data["T"],
        clv_data["avg_order_value"],
        time=12, freq="W", discount_rate=0.01
    ).round(2)

    clv_data["CLV_12months"] = clv_values

    print(f"Avg CLV: ${clv_data['CLV_12months'].mean():.2f}")
    print(f"Max CLV: ${clv_data['CLV_12months'].max():.2f} ")

    # Gate 4: CLV validation:
    if (clv_data["CLV_12months"] < 0).any():
        raise ValueError(f"Gate 4 FAILED: {(clv_data['CLV_12months'] < 0).sum()} negative clv values")
    if (clv_data["predicted_purchase_1yr"] < 0).any():
        raise ValueError("Gate 4 FAILED: Negative purchase predictions")
    print(f"Gate 4 PASSED: CLV range ${clv_data['CLV_12months'].min():.2f} - ${clv_data['CLV_12months'].max():.2f}")


    df_final = df_rfm.merge(
        clv_data[["CustomerID", "predicted_purchase_1yr", "CLV_12months"]],
        how="left"
    )

    # Gate 5: Merge validation
    rows_lost = len(df_rfm) - len(df_final)
    pct_lost = rows_lost / len(df_rfm) * 100
    print(f"Merge: {rows_lost} customers dropped ({pct_lost:.1f}%)")
    if pct_lost > 20:
        raise ValueError(f"Gate 5 FAILED: Merge lost {pct_lost:.1f}% of customers")
    print("Gate 5 PASSED: Merge validated")


    df_final[[
        "CustomerID", "Country", "FirstPurchase", "LastPurchase", "Segment",
        "R_Raw", "F_Raw", "M_Raw", "R_Score", "F_Score", "M_Score", "RFM_Score",
        "ChurnedProbability", "CLV_12months", "predicted_purchase_1yr"
    ]].to_csv(OUTPUT_DIR + "rfm_segments.csv", index=False)

    clv_data.to_csv(OUTPUT_DIR + "clv_predictions.csv", index=False)

    print(f"rfm_segments.csv: {len(df_final):,} rows")
    print(f"clv_predictions.csv: {len(clv_data):,} rows")

    df_trans = pd.read_sql("""
                           SELECT
                                f.InvoiceNo,
                                p.Description
                           FROM fact_sales f JOIN dim_product p ON f.StockCode=p.StockCode
                           WHERE f.Quantity > 0
                           ORDER BY f.InvoiceNo
    """, con=engine)

    print(f"Rows loaded: {len(df_trans):,}")
    print(f"Unique Invoices: {df_trans['InvoiceNo'].nunique():,}")

    basket_sets = df_trans.groupby("InvoiceNo")["Description"].apply(list).to_list()
    te = TransactionEncoder()
    te_array = te.fit_transform(basket_sets)
    basket_matrix = pd.DataFrame(te_array, columns=te.columns_)

    print(f"Basket Matrix: {basket_matrix.shape}")

    frequent_itemsets = apriori(
        basket_matrix, min_support=MIN_SUPPORT, use_colnames=True, max_len=2
    )

    print(f"Frequent Itemsets: {len(frequent_itemsets):,}")

    rules = association_rules(frequent_itemsets, metric="lift", min_threshold=MIN_LIFT)
    rules["antecedents"] = rules["antecedents"].apply(lambda x: ", ".join(list(x)))
    rules["consequents"] = rules["consequents"].apply(lambda x: ", ".join(list(x)))
    rules = rules[["antecedents", "consequents", "support", "confidence", "lift"]].round(4).sort_values("lift", ascending=False).reset_index(drop=True)

    print(rules.head(10).to_string(index=False))

    # Gate 6: Basket Analysis validation
    if len(rules) < 10:
        raise ValueError(f"Gate 6 FAILED: Only {len(rules)} rules generated")
    if not (rules["lift"] > 1.0).all():
        raise ValueError("Gate 6 FAILED: Rules with lift <= 1.0")
    if not rules["confidence"].between(0, 1).all():
        raise ValueError("Gate 6 FAILED: Confidence out of [0,1] range")
    print(f"Gate 6 PASSED: {len(rules)} rules, max lift={rules['lift'].max():.2f}")

    rules.to_csv(OUTPUT_DIR + "basket_rules.csv", index=False)

    print(f"basket_rules.csv: {len(rules):,} rules")

    #Cohort Retention
    df_coh = pd.read_sql("""
        SELECT
            f.CustomerID,
            d.FullDate AS InvoiceDate
        FROM fact_sales f JOIN dim_date d ON f.DateId = d.DateId
        WHERE f.CustomerID IS NOT NULL
            AND d.FullDate IS NOT NULL
            AND f.IsReturn = False
    """, con=engine)

    df_coh["InvoiceDate"] = pd.to_datetime(df_coh["InvoiceDate"])

    print(f"{len(df_coh):,} rows loaded ")

    df_coh["OrderMonth"] = df_coh["InvoiceDate"].dt.to_period("M")
    df_coh["CohortMonth"] = df_coh.groupby("CustomerID")["InvoiceDate"] \
        .transform("min").dt.to_period("M")
    df_coh["CohortIndex"] = (df_coh["OrderMonth"] - df_coh["CohortMonth"]).apply(lambda x: x.n)

    print(df_coh)

    cohort_data = (
        df_coh.groupby(["CohortMonth", "CohortIndex"])["CustomerID"].nunique().reset_index()
    )

    cohort_matrix = cohort_data.pivot(index="CohortMonth", columns="CohortIndex", values="CustomerID")
    cohort_sizes = cohort_matrix[0]
    retention_matrix = cohort_matrix.divide(cohort_sizes, axis=0).round(4)
    MAX_MONTHS = 11
    retention_matrix = retention_matrix.iloc[:, :MAX_MONTHS +1]
    retention_matrix = retention_matrix.sort_index(ascending=True)

    print(cohort_matrix)
    print(cohort_sizes)
    print(retention_matrix)
    print(len(retention_matrix))

    # Gate 7: Retention validation
    if not (retention_matrix.fillna(0) >= 0).all().all():
        raise ValueError("Gate 7 FAILED: Negative retention values")
    if not (retention_matrix.fillna(0) <= 1).all().all():
        raise ValueError("Gate 7 Failed: Retention > 100%")
    if not (retention_matrix[0] == 1).all():
        raise ValueError("Gate 7 FAILED: Month 0 retention != 100%")
    print("Gate 7 PASSED: Retention Matrix valid")


    out = (retention_matrix * 100).round(2)
    out_index = out.index.astype(str)
    out.columns = [f"M+({i})" for i in out.columns]
    out.insert(0, "CohortSize", cohort_sizes.values)
    out.to_csv(OUTPUT_DIR + "cohort_retention.csv", index=False)
    
    churn_risk = df_rfm[
        (df_rfm["R_Raw"].between(60, 180))
    ].sort_values("M_Raw", ascending=False)

    churn_risk.to_csv(OUTPUT_DIR + "churn_risk_list.csv", index=False)

    fig, ax = plt.subplots(figsize=(16, 10))

    sns.heatmap(
        retention_matrix,
        annot=True,
        fmt=".0%",
        cmap="YlOrRd_r",
        linewidths=0.4,
        ax=ax,
        vmin=0,
        vmax=1
    )

    ax.set_title("Customer Cohort Retention — Consumer360", fontsize=14, pad=15)
    ax.set_xlabel("Months Since First Purchase")
    ax.set_ylabel("Cohort (First Purchase Month)")
    ax.set_xticklabels([f"M+{i}" for i in range(12)], rotation=0)
    ax.set_yticklabels(retention_matrix.index.astype(str), rotation=0)

    plt.tight_layout()
    plt.savefig(OUTPUT_DIR + "cohort_retention_heatmap.png", dpi=150, bbox_inches="tight")
    plt.close()

    # Gate 8: Output file validation
    for fname, min_rows in [("rfm_segments.csv", 1000), ("clv_predictions.csv", 500), ("basket_rules.csv", 10), ("cohort_retention.csv", 5)]:
        path = OUTPUT_DIR + fname
        if not os.path.exists(path):
            raise ValueError(f"Gate 8 FAILED: {fname} not written")
        row_count = len(pd.read_csv(path))
        if row_count < min_rows:
            raise ValueError(f"Gate 8 FAILED: {fname} has only {row_count} rows")
        print(f"✓ {fname}: {row_count} rows, {os.path.getsize(path)/1024:.1f} KB")
    print("All 8 gates passed — pipeline complete")

except Exception as e:
    print(f"PIPELINE FAILED: {e}", file=sys.stderr)
    sys.exit(1)
finally:
    if 'engine' in dir():
        engine.dispose()



