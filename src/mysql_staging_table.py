import pandas as pd
from sqlalchemy import create_engine, text
import time
import os
from dotenv import load_dotenv

# CONFIG
load_dotenv()
DB_URL = os.getenv("DB_URL")
CSV_PATH    = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "online_retail_clean.csv")

# CONNECTION
engine = create_engine(DB_URL, pool_pre_ping=True)
print("Connected to MySQL")

# LOAD CSV 
df = pd.read_csv(CSV_PATH, parse_dates=["InvoiceDate"])

df["Quantity"]   = df["Quantity"].astype("int32")
df["UnitPrice"]  = df["UnitPrice"].astype("float32")
df["CustomerID"] = df["CustomerID"].astype("int32")
df["Amount"]     = df["Amount"].astype("float32")

print(f"Rows to load: {len(df):,}")
print(f"Columns: {list(df.columns)}")

# CREATE STAGING TABLE 
create_stg_sql = """
CREATE TABLE IF NOT EXISTS stg_raw_retail (
    InvoiceNo   VARCHAR(20)    NOT NULL,
    StockCode   VARCHAR(20)    NOT NULL,
    Description VARCHAR(255),
    Quantity    INT            NOT NULL,
    InvoiceDate DATETIME       NOT NULL,
    UnitPrice   DECIMAL(10,2)  NOT NULL,
    CustomerID  INT            NOT NULL,
    Country     VARCHAR(50),
    Amount      DECIMAL(12,2)  NOT NULL
);
"""

with engine.connect() as conn:
    conn.execute(text("DROP TABLE IF EXISTS stg_raw_retail;"))
    conn.execute(text(create_stg_sql))
    conn.commit()
print("stg_raw_retail table created (fresh)")

# BULK LOAD 
start = time.time()

df.to_sql(
    name      = "stg_raw_retail",
    con       = engine,
    if_exists = "append",
    index     = False,
    chunksize = 5000,
    method    = "multi"
)

print(f"Bulk load complete in {round(time.time() - start, 1)}s")

# VALIDATION 
with engine.connect() as conn:
    row_count = conn.execute(
        text("SELECT COUNT(*) FROM stg_raw_retail;")
    ).scalar()
    sample = conn.execute(
        text("SELECT InvoiceNo, Quantity, UnitPrice, Amount, CustomerID FROM stg_raw_retail LIMIT 3;")
    ).fetchall()

print(f"\n Staging Validation")
print(f"Rows in stg_raw_retail: {row_count:,}")
print(f"Expected: approximately 779,000")
print(f"\n Sample rows:")
for row in sample:
    print(f"{row}")

assert row_count == len(df), \
    f"Row mismatch! CSV={len(df):,} | DB={row_count:,}"

print(f"Step 4 complete — stg_raw_retail loaded and validated")