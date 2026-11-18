import psycopg
import pandas as pd
from dotenv import load_dotenv
import os
load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_PORT = os.getenv("DB_PORT")


# Connect to PostgreSQL to retrieve Monster Beverage's financial cash flows data.
with psycopg.connect(
    host=DB_HOST,
    port=DB_PORT,
    dbname=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD
) as conn:
    print("Successfully connected to PostgreSQL.")


    with conn.cursor() as cur:
        cur.execute("""
            SELECT fiscal_year, revenue, free_cash_flow
            FROM financials_annual
            WHERE company_id = 1
            ORDER BY fiscal_year;
        """)

        financials_rows = cur.fetchall()

print(financials_rows)


#Converting historical financial data retrieving from DB into a pandas DataFrame
financial_df = pd.DataFrame(
    financials_rows,
    columns=["fiscal_year", "revenue", "free_cash_flow"]
)

# To display the historical financial data in a table.
print(financial_df)


# Convert revenue and free cash flow columns into numeric values for calculations.
financial_df["revenue"] = pd.to_numeric(financial_df["revenue"])
financial_df["free_cash_flow"] / financial_df["free_cash_flow"]

# Calculate annual free cash flow margin as a percentage of revenue.
financial_df["fcf_margin_pct"] = (
    financial_df["free_cash_flow"] / financial_df["revenue"]
) * 100