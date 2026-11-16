import os
import pandas as pd
import psycopg
from dotenv import load_dotenv

# Load database credentials from the .env file.
load_dotenv()

# Retrieve PostgreSQL connection settings from environment variable
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")


# Connect to PostgreSQL to retrieve Monster Beverage's financial data.
with psycopg.connect(
    host=DB_HOST,
    port=DB_PORT,
    dbname=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD
) as conn:
    print("Successfully connected to PostgreSQL.")


    # Retrieve Monster Beverage's annual revenue in chronological order.
    revenue_query = """
        SELECT fiscal_year, revenue
        FROM financials_annual
        WHERE company_id = 1
        ORDER BY fiscal_year;
    """


    # Execute the SQL query and retrieve all matching financial records.
    with conn.cursor() as cursor:
        cursor.execute(revenue_query)
        revenue_rows = cursor.fetchall()


    # Display the retrieved financial records for initial verification.
    print(revenue_rows)

        # Convert the PostgreSQL query results into a pandas DataFrame.
    revenue_df = pd.DataFrame(
        revenue_rows,
        columns=["fiscal_year", "revenue"]
    )

    # Convert PostgreSQL Decimal values into numeric values.
    revenue_df["revenue"] = pd.to_numeric(revenue_df["revenue"])


    # Display the organized annual revenue data.
    print("\nMonster Beverage Annual Revenue:")
    print(revenue_df.to_string(index=False))


    # Calculate year-over-year revenue growth as a percentage.
    revenue_df["revenue_growth_pct"] = (
        revenue_df["revenue"].pct_change() * 100
    ).round(2)


    # Display historical revenue and calculated growth rates.
    print("\nMonster Beverage Historical Revenue Growth:")
    print(revenue_df.to_string(index=False))


# Calculate historical revenue CAGR using the first and last fiscal years.
beginning_revenue = revenue_df["revenue"].iloc[0]
ending_revenue = revenue_df["revenue"].iloc[-1]

# Determine the number of annual growth periods.
years = revenue_df["fiscal_year"].iloc[-1] - revenue_df["fiscal_year"].iloc[0]

# Calculate CAGR as a percentage.
revenue_cagr = ((ending_revenue / beginning_revenue) ** (1 / years) - 1) * 100

print(f"\nMonster Beverage Historical Revenue CAGR: {revenue_cagr:.2f}%")