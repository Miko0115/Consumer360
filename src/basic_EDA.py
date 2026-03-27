import numpy as np
import pandas as pd
import os

BASE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")

# Loading raw data
df = pd.read_csv(os.path.join(BASE_DIR, "online_retail.csv"))
print(df)

print(f"Raw rows: {len(df):,}") 
print(df.shape)

# Data profiling
print(df.dtypes)
print()
print(df.isnull().sum())

print(df.describe())

# Column renaming
df.rename(columns={
    "Invoice": "InvoiceNo",
    "Customer ID": "CustomerID",
    "Price": "UnitPrice"
}, inplace=True)

# Null removal
df.dropna(subset=["CustomerID", "Description"], inplace=True)

# Invoice filtering
df = df[~df["InvoiceNo"].str.startswith("C", na=False)]

df = df[df["InvoiceNo"].str.match(r"^\d+$", na=False)]

# Data parsing
df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"])

# Positive values only for Quantity and UnitPrice
df = df[(df["Quantity"] > 0) & (df["UnitPrice"] > 0)]

# Cleaning Stockcode
df = df[df["StockCode"].str.strip() != "B"]

# Type casting
df["CustomerID"] = df["CustomerID"].astype("int32")
df["Quantity"] = df["Quantity"].astype("int32")
df["UnitPrice"] = df["UnitPrice"].astype("float32")

# Calculating Amount
df["Amount"] = (df["Quantity"] * df["UnitPrice"]).astype("float32")

# String cleanup
df["StockCode"] = df["StockCode"].str.strip()
df["Description"] = df["Description"].str.strip().str.upper()
df["Country"] = df["Country"].str.strip()

df.drop_duplicates(inplace=True)

df.to_csv(os.path.join(BASE_DIR, "online_retail_clean.csv"), index=False)

print(df.shape)