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

    # Retrieve management commentary scores for Q1 and Q2 2026.
        cursor.execute("""
        SELECT fiscal_year, fiscal_quarter, theme, score
        FROM management_commentary_scores
        WHERE fiscal_year = 2026
        ORDER BY fiscal_quarter, theme;
        """)

        # Store the retrieved commentary records.
        commentary_rows = cursor.fetchall()

        # Retrieve Monster Beverage store observations from PostgreSQL.
        cursor.execute("""
        SELECT observation_date,
               store_name,
               store_location,
               restock_signal,
               restock_frequency_days,
               notes
        FROM store_observations
        WHERE company_id = 1
        ORDER BY observation_date, store_name;
        """)

        # Store the retrieved retail observation records.
        store_rows = cursor.fetchall()

    # Verify the number of store observations retrieved.
    print(f"Store Observations Retrieved: {len(store_rows)}")


    # Convert store observations into a pandas DataFrame.
    store_df = pd.DataFrame(
        store_rows,
        columns=[
            "observation_date",
            "store_name",
            "store_location",
            "restock_signal",
            "restock_frequency_days",
            "notes"
        ]
    )

    # Display our store observations.
    print("\nMonster Beverage Store Observations:")
    print(store_df.to_string(index=False))


    # Convert restocking frequency values into numeric data
    store_df["restock_frequency_days"] = pd.to_numeric(
        store_df["restock_frequency_days"]
    )

    # Calculate the average restocking interval across our store observation.
    average_restock_days = store_df["restock_frequency_days"].mean()

    # Displaying the average restocking interval.
    print(f"\nAverage Restocking Interval: {average_restock_days:2f} days")


    # Select the columns needed for our retail demand analysis.
    store_summary = store_df[
        ["store_name", "store_location", "restock_signal", "restock_frequency_days"]
    ]

    # Display a simplified store observation table.
    print("\nMonster Beverage Store Restocking Summary:")
    print(store_summary.to_string(index=False))

    # Identify whether each observation has a confirmed restocking schedule.
    store_summary = store_summary.copy()


    # Create an initial data-quality classification.
    store_summary["evidence_quality"] = "Review Required"


        # Check whether pandas can identify the Walmart KOP location.
    walmart_match = (
        (store_summary["store_name"] == "Walmart") &
        (store_summary["store_location"].str.contains("275 N Gulph Rd"))
    )

        # Classify Walmart KOP's restocking frequency as estimated.
    store_summary.loc[walmart_match, "evidence_quality"] = "Estimated"


    evidence_map = {
        "310 S Henderson Rd": "Reported",
        "160 W DeKalb Pike": "Reported",
        "145 W DeKalb Pike": "Reported",
        "100 W DeKalb Pike": "Reported",
        "312 S Henderson Rd": "Estimated",
        "1 Village Dr": "Proxy",
        "2670 Egypt Rd": "Reported",
        "650 S Trooper Rd": "Reported"
    }

    for address, quality in evidence_map.items():
        store_summary.loc[
            store_summary["store_location"].str.contains(address),
            "evidence_quality"
        ] = quality

    print(store_summary.to_string(index=False))
    print(store_summary["evidence_quality"].value_counts())
    
    
    # Classifying Walmart's KoP's Restocking frequency as estimated
    # store_summary.loc[
        #(store_summary["store_name"] == "Walmary") &
        #(store_summary["store_location"].str.contains("275 N Gulph Rd")),
        #"evidence_quality"
    #] = "Estimated"


    # Display the store observations with their evidence-quality classifications.
    print("\nStore Observation Evidence Quality:")
    print(store_summary.to_string(index=False))


    # Display the retrieved financial records for initial verification.
    print(revenue_rows)


    # Verify the number of management commentary records retrieved.
    print(f"Management Commentary Records Retrieved: {len(commentary_rows)}")


    # Convert management commentary records into a pandas DataFrame.
    commentary_df = pd.DataFrame(
        commentary_rows,
        columns=["fiscal_year", "fiscal_quarter", "theme", "score"]
    )

    # Display the management commentary records.
    print("\nMonster Beverage Management Commentary Scores:")
    print(commentary_df.to_string(index=False))

    # Convert management commentary scores to numeric values.
    commentary_df["score"] = pd.to_numeric(commentary_df["score"])

    # Calculating the average management commentaryt score for each quarter.
    quarterly_scores = commentary_df.groupby("fiscal_quarter")["score"].mean()
    

    # To display the quarterly management commentary averages
    print("\nQuarterly Management Commentary Averages:")
    print(quarterly_scores)


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


# Calculate the average annual revenue growth, excluding the first year
average_growth_rate = revenue_df["revenue_growth_pct"].dropna().mean()

# Display the average annual revenue growth.
print(f"Average Annual Revenue Growth: {average_growth_rate:.2f}%")


