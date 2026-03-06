import numpy as np
import pandas as pd
from sqlalchemy import create_engine, text
import time

df = pd.read_csv("online_retail.csv")
print(df)

print(f"Raw rows: {len(df):,}") 
print(df.shape)

print(df.dtypes)
print()
print(df.isnull().sum())

print(df.describe())

df.rename(columns={
    "Invoice": "InvoiceNo",
    "Customer ID": "CustomerID",
    "Price": "UnitPrice"
}, inplace=True)

df.dropna(subset=["CustomerID", "Description"], inplace=True)

df = df[~df["InvoiceNo"].str.startswith("C", na=False)]

df = df[df["InvoiceNo"].str.match(r"^\d+$", na=False)]


df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"])

df = df[(df["Quantity"] > 0) & (df["UnitPrice"] > 0)]

df = df[df["StockCode"].str.strip() != "B"]

df["CustomerID"] = df["CustomerID"].astype("int32")
df["Quantity"] = df["Quantity"].astype("int32")
df["UnitPrice"] = df["UnitPrice"].astype("float32")

df["Amount"] = (df["Quantity"] * df["UnitPrice"]).astype("float32")

df["StockCode"] = df["StockCode"].str.strip()
df["Description"] = df["Description"].str.strip().str.upper()
df["Country"] = df["Country"].str.strip()

df.drop_duplicates(inplace=True)

df.to_csv("online_retail.clean.csv", index=False)

print(df.shape)