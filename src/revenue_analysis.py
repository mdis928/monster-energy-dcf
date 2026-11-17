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


# Establish the latest historical revenue as the starting point for future forecasts.
base_year = int(revenue_df["fiscal_year"].iloc[-1])
base_revenue = float(revenue_df["revenue"].iloc[-1]) 


# Verify the historical starting point for our revenue forecasts.
print(f"\nForecast Base Year: {base_year}")
print(f"Forecast Starting Revenue: ${base_revenue:,.0f}")


# Define the five-year revenue forecasting period.
forecast_years = range(base_year + 1, base_year + 6)

# Display the forecast years to verify the projection period.
print(f"\nForecast Years: {list(forecast_years)}")

# Convert historical CAGR from a percentage to a decimal.
historical_growth_rate = revenue_cagr / 100

# Create an empty list to store each year's projected revenue.
forecast_data = []

# Start the forecast using Monster's latest historical revenue.
projected_revenue = base_revenue

# Loop through each year in our five-year forecast period.
for year in forecast_years:
    projected_revenue = projected_revenue * (1 + historical_growth_rate)

    # Storing the forecast year and its projected revenue
    forecast_data.append({
        "fiscal_year": year,
        "projected_revenue": projected_revenue
    })


# Convert the forecast results into a pandas DataFrame
forecast_df = pd.DataFrame(forecast_data)

# Display Monster Beverage's five year revenue forecast.
print("\nMonster Beverage Historical CAGR Revenue Forecast:")
print(forecast_df.to_string(index=False, float_format="{:,.0f}".format))


# Define preliminary revenue growth assumptions for each scenario.
growth_scenarios = {
    "bear": 0.06,
    "base": historical_growth_rate,
    "bull": 0.14
}

# Create an empty list to store all scenario forecasts.
scenario_forecasts = []

# Loop through each growth scenario and its associated growth rate.
for scenario, growth_rate in growth_scenarios.items():
    projected_revenue = base_revenue

    # Calculate projected revenue for each year in this scenario.
    for year in forecast_years:
        projected_revenue = projected_revenue * (1 + growth_rate)

        # Store the scenario, year, and projected revenue.
        scenario_forecasts.append({
            "scenario": scenario,
            "fiscal_year": year,
            "projected_revenue": projected_revenue
        })

# Convert the scenario forecast results into a pandas DataFrame.
scenario_df = pd.DataFrame(scenario_forecasts)

# Display all three revenue scenarios.
print("\nMonster Beverage Revenue Scenarios:")
print(scenario_df.to_string(index=False, float_format="{:,.0f}".format))