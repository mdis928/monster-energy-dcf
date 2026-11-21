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
            SELECT
            fiscal_year,
            revenue,
            free_cash_flow,
            operating_income,
            depreciation_amortization,
            capital_expenditure,
            change_in_working_capital
            FROM financials_annual
            WHERE company_id = 1
            ORDER BY fiscal_year;
        """)

        financial_rows = cur.fetchall()

print(financial_rows)



# Convert historical financial records from PostgreSQL into a pandas DataFrame.
# Column names must match the order of the SQL SELECT statement.
financial_df = pd.DataFrame(
    financial_rows,
    columns=[
        "fiscal_year",
        "revenue",
        "free_cash_flow",
        "operating_income",
        "depreciation_amortization",
        "capital_expenditure",
        "change_in_working_capital"
    ]
)


# Define the financial columns that need numeric conversion.
numeric_columns = [
    "revenue",
    "free_cash_flow",
    "operating_income",
    "depreciation_amortization",
    "capital_expenditure",
    "change_in_working_capital"
]

# Convert PostgreSQL Decimal values into floats for financial calculations.
financial_df[numeric_columns] = financial_df[numeric_columns].astype(float)


# Convert PostgreSQL Decimal values into floats for financial calculations.
#financial_df["revenue"] = financial_df["revenue"].astype(float)
#financial_df["free_cash_flow"] = financial_df["free_cash_flow"].astype(float)

# Calculate annual free cash flow margin as a percentage of revenue.
financial_df["fcf_margin_pct"] = (
    financial_df["free_cash_flow"] / financial_df["revenue"]
) * 100

# To display the historical financial data in a table.
print(financial_df)


# Calculate the average historical free cash flow margin from 2021 through 2025.
average_fcf_margin = financial_df["fcf_margin_pct"].mean()

# Display the average historical margin rounded to two decimal places.
print(f"Average Historical FCF Margin: {average_fcf_margin:.2f}%")


# Set an initial normalized corporate tax rate assumption.
tax_rate = 0.25

# Calculate net operating profit after taxes (NOPAT).
financial_df["nopat"] = (
    financial_df["operating_income"] * (1 - tax_rate)
)

# Calculate historical unlevered free cash flow (FCFF).
# FMP reports capital expenditure as a negative cash flow.
# The working capital field represents a signed cash flow adjustment.
financial_df["fcff"] = (
    financial_df["nopat"]
    + financial_df["depreciation_amortization"]
    + financial_df["capital_expenditure"]
    + financial_df["change_in_working_capital"]
)

# Display historical operating profit, NOPAT, and FCFF.
print(
    financial_df[
        ["fiscal_year", "operating_income", "nopat", "fcff"]
    ]
)

# Calculate historical unlevered free cash flow as a percentage of revenue.
financial_df["fcff_margin_pct"] = (
    financial_df["fcff"] / financial_df["revenue"]
) * 100

# Calculate the five-year average FCFF margin.
average_fcff_margin = financial_df["fcff_margin_pct"].mean()

# Display historical FCFF margins.
print(financial_df[["fiscal_year", "fcff_margin_pct"]])

# Display the average FCFF margin rounded to two decimal places.
print(f"Average Historical FCFF Margin: {average_fcff_margin:.2f}%")


# Calculate year-over-year growth in historical unlevered free cash flow.
financial_df["fcff_growth_pct"] = (
    financial_df["fcff"].pct_change()
) * 100

# Display historical FCFF growth alongside annual FCFF margins.
print(
    financial_df[
        ["fiscal_year", "fcff_margin_pct", "fcff_growth_pct"]
    ]
)


# Calculate FCFF before changes in working capital.
# This helps isolate the effect of working capital movements.
financial_df["fcff_before_wc"] = (
    financial_df["nopat"]
    + financial_df["depreciation_amortization"]
    + financial_df["capital_expenditure"]
)

# Compare FCFF before and after working capital adjustments.
print(
    financial_df[
        [
            "fiscal_year",
            "fcff_before_wc",
            "change_in_working_capital",
            "fcff"
        ]
    ]
)


# Define the five fiscal years used in our DCF forecast.
forecast_years = [2026, 2027, 2028, 2029, 2030]

# Create a pandas DataFrame to organize our forecast assumptions.
forecast_df = pd.DataFrame({
    "fiscal_year": forecast_years
})

# Display the forecast period.
print(forecast_df)


# Retrieve Monster Beverage's 2025 revenue as the starting point for our forecast.
base_revenue = financial_df.loc[
    financial_df["fiscal_year"] == 2025,
    "revenue"
].iloc[0]

# Display the starting revenue used in our DCF.
print(f"2025 Base Revenue: ${base_revenue:,.2f}")


# Set the preliminary base-case annual revenue growth assumption.
base_growth_rate = 0.1061

# Calculate how many years each forecast period is beyond 2025.
forecast_df["years_forward"] = forecast_df["fiscal_year"] - 2025

# Forecast revenue using compound annual growth.
forecast_df["base_revenue"] = (
    base_revenue * (1 + base_growth_rate) ** forecast_df["years_forward"]
)

# Display the five-year base-case revenue forecast.
print(forecast_df[["fiscal_year", "base_revenue"]])


# Define preliminary bear-case and bull-case revenue growth assumptions.
bear_growth_rate = 0.06
bull_growth_rate = 0.14


# Calculate the annual growth rate implied by our existing base-case forecast.
base_growth_rate = forecast_df.loc[
    forecast_df["years_forward"] == 1, "base_revenue"
].iloc[0] / base_revenue - 1

# Define hypothetical growth adjustments for sensitivity testing.
alt_low_growth = base_growth_rate + 0.01
alt_mid_growth = base_growth_rate + 0.02
alt_high_growth = base_growth_rate + 0.03


# Display the growth rates used in our alternative sensitivity scenarios.
print(f"Base Growth Rate: {base_growth_rate:.2%}")
print(f"Alternative Low Growth: {alt_low_growth:.2%}")
print(f"Alternative Mid Growth: {alt_mid_growth:.2%}")
print(f"Alternative High Growth: {alt_high_growth:.2%}")

# Forecast revenue under the bear-case growth assumption.
forecast_df["bear_revenue"] = (
    base_revenue * (1 + bear_growth_rate) ** forecast_df["years_forward"]
)

# Forecast revenue under the bull-case growth assumption.
forecast_df["bull_revenue"] = (
    base_revenue * (1 + bull_growth_rate) ** forecast_df["years_forward"]
)

# Compare all three revenue scenarios for 2026 through 2030.
print(
    forecast_df[
        ["fiscal_year", "bear_revenue", "base_revenue", "bull_revenue"]
    ]
)



# Forecast revenue using the alternative low-growth assumption.
forecast_df["alt_low_revenue"] = (
    base_revenue * (1 + alt_low_growth) ** forecast_df["years_forward"]
)

# Forecast revenue using the alternative mid-growth assumption.
forecast_df["alt_mid_revenue"] = (
    base_revenue * (1 + alt_mid_growth) ** forecast_df["years_forward"]
)

# Forecast revenue using the alternative high-growth assumption.
forecast_df["alt_high_revenue"] = (
    base_revenue * (1 + alt_high_growth) ** forecast_df["years_forward"]
)




# Calculate historical operating income as a percentage of revenue.
financial_df["operating_margin_pct"] = (
    financial_df["operating_income"] / financial_df["revenue"]
) * 100

# Calculate the average historical operating margin.
average_operating_margin = financial_df["operating_margin_pct"].mean()

# Display historical operating margins.
print(financial_df[["fiscal_year", "operating_margin_pct"]])

# Display the average operating margin rounded to two decimal places.
print(f"Average Historical Operating Margin: {average_operating_margin:.2f}%")


# Convert the average historical operating margin from a percentage to a decimal.
forecast_operating_margin = average_operating_margin / 100

# Calculate forecast operating income for each revenue scenario.
forecast_df["bear_operating_income"] = (
    forecast_df["bear_revenue"] * forecast_operating_margin
)

forecast_df["base_operating_income"] = (
    forecast_df["base_revenue"] * forecast_operating_margin
)

forecast_df["bull_operating_income"] = (
    forecast_df["bull_revenue"] * forecast_operating_margin
)


# Calculate operating income for the alternative low-growth scenario.
forecast_df["alt_low_operating_income"] = (
    forecast_df["alt_low_revenue"] * forecast_operating_margin
)

# Calculate operating income for the alternative mid-growth scenario.
forecast_df["alt_mid_operating_income"] = (
    forecast_df["alt_mid_revenue"] * forecast_operating_margin
)

# Calculate operating income for the alternative high-growth scenario.
forecast_df["alt_high_operating_income"] = (
    forecast_df["alt_high_revenue"] * forecast_operating_margin
)




# Display projected operating income for all three scenarios.
print(
    forecast_df[
        [
            "fiscal_year",
            "bear_operating_income",
            "base_operating_income",
            "bull_operating_income"
        ]
    ]
)


# Calculate forecast net operating profit after taxes (NOPAT).
# Apply the preliminary 25% normalized tax rate to operating income.

forecast_df["bear_nopat"] = (
    forecast_df["bear_operating_income"] * (1 - tax_rate)
)

forecast_df["base_nopat"] = (
    forecast_df["base_operating_income"] * (1 - tax_rate)
)

forecast_df["bull_nopat"] = (
    forecast_df["bull_operating_income"] * (1 - tax_rate)
)

# Display projected NOPAT for all three scenarios.
print(
    forecast_df[
        [
            "fiscal_year",
            "bear_nopat",
            "base_nopat",
            "bull_nopat"
        ]
    ]
)


# Calculate after-tax operating profit for alternative low growth.
forecast_df["alt_low_nopat"] = (
    forecast_df["alt_low_operating_income"] * (1 - tax_rate)
)

# Calculate after-tax operating profit for alternative mid growth.
forecast_df["alt_mid_nopat"] = (
    forecast_df["alt_mid_operating_income"] * (1 - tax_rate)
)

# Calculate after-tax operating profit for alternative high growth.
forecast_df["alt_high_nopat"] = (
    forecast_df["alt_high_operating_income"] * (1 - tax_rate)
)



# Calculate historical depreciation and amortization as a percentage of revenue.
financial_df["da_margin_pct"] = (
    financial_df["depreciation_amortization"] / financial_df["revenue"]
) * 100

# Calculate historical capital expenditure as a percentage of revenue.
# Use a negative sign to convert FMP's negative cash outflow into a positive spending ratio.
financial_df["capex_margin_pct"] = (
    -financial_df["capital_expenditure"] / financial_df["revenue"]
) * 100

# Calculate the historical average of both ratios.
average_da_margin = financial_df["da_margin_pct"].mean()
average_capex_margin = financial_df["capex_margin_pct"].mean()

# Display the historical ratios.
print(financial_df[["fiscal_year", "da_margin_pct", "capex_margin_pct"]])

# Display the averages.
print(f"Average D&A Margin: {average_da_margin:.2f}%")
print(f"Average CapEx Margin: {average_capex_margin:.2f}%")


# Convert historical percentage averages into decimal assumptions.
forecast_da_margin = average_da_margin / 100
forecast_capex_margin = average_capex_margin / 100

# Forecast depreciation and amortization for each revenue scenario.
for scenario in ["bear", "base", "bull", "alt_low", "alt_mid", "alt_high"]:
    forecast_df[f"{scenario}_da"] = (
        forecast_df[f"{scenario}_revenue"] * forecast_da_margin
    )

    # Forecast capital expenditures as negative cash flows.
    forecast_df[f"{scenario}_capex"] = (
        -forecast_df[f"{scenario}_revenue"] * forecast_capex_margin
    )

# Display the base-case reinvestment forecast.
print(
    forecast_df[
        ["fiscal_year", "base_da", "base_capex"]
    ]
)


# Calculate historical working capital cash flow adjustments as a percentage of revenue.
financial_df["wc_margin_pct"] = (
    financial_df["change_in_working_capital"] / financial_df["revenue"]
) * 100

# Calculate the average historical working capital adjustment.
average_wc_margin = financial_df["wc_margin_pct"].mean()

# Display historical working capital adjustments.
print(
    financial_df[
        ["fiscal_year", "wc_margin_pct"]
    ]
)

# Display the five-year historical average.
print(f"Average Working Capital Adjustment: {average_wc_margin:.2f}%")


# Convert the historical working capital percentage into a decimal.
forecast_wc_margin = average_wc_margin / 100

# Forecast working capital cash flow adjustments for each scenario.
for scenario in ["bear", "base", "bull", "alt_low", "alt_mid", "alt_high"]:
    forecast_df[f"{scenario}_wc"] = (
        forecast_df[f"{scenario}_revenue"] * forecast_wc_margin
    )

# Display the base-case working capital forecast.
print(
    forecast_df[
        ["fiscal_year", "base_wc"]
    ]
)


# Calculate projected Free Cash Flow to the Firm for all three scenarios.
for scenario in ["bear", "base", "bull", "alt_low", "alt_mid", "alt_high"]:
    forecast_df[f"{scenario}_fcff"] = (
        forecast_df[f"{scenario}_nopat"]
        + forecast_df[f"{scenario}_da"]
        + forecast_df[f"{scenario}_capex"]
        + forecast_df[f"{scenario}_wc"]
    )

# Display the five-year FCFF forecast for all three scenarios.
print(
    forecast_df[
        [
            "fiscal_year",
            "bear_fcff",
            "base_fcff",
            "bull_fcff",
            "alt_low_fcff",
            "alt_mid_fcff",
            "alt_high_fcff"
        ]
    ]
)


# Set preliminary DCF valuation assumptions.
# WACC represents the required return on invested capital.
wacc = 0.09

# Assume a preliminary 3% perpetual growth rate.
terminal_growth_rate = 0.03

# Calculate the number of years beyond our 2025 base year.
forecast_df["discount_period"] = forecast_df["fiscal_year"] - 2025

# Calculate the present value discount factor for each forecast year.
forecast_df["discount_factor"] = (
    1 / (1 + wacc) ** forecast_df["discount_period"]
)

# Display the discount factors.
print(forecast_df[["fiscal_year", "discount_period", "discount_factor"]])


# Calculate the present value of forecast FCFF for each scenario.
for scenario in ["bear", "base", "bull", "alt_low", "alt_mid", "alt_high"]:
    forecast_df[f"{scenario}_pv_fcff"] = (
        forecast_df[f"{scenario}_fcff"] * forecast_df["discount_factor"]
    )

# Display discounted free cash flows for all three scenarios.
print(
    forecast_df[
        [
            "fiscal_year",
            "bear_pv_fcff",
            "base_pv_fcff",
            "bull_pv_fcff"
        ]
    ]
)


# Create a dictionary to store the present value of forecast cash flows.
pv_forecast = {}

# Sum the discounted cash flows for each scenario.
for scenario in ["bear", "base", "bull", "alt_low", "alt_mid", "alt_high"]:
    pv_forecast[scenario] = forecast_df[f"{scenario}_pv_fcff"].sum()

# Display the total present value of forecast cash flows.
for scenario, value in pv_forecast.items():
    print(f"{scenario.capitalize()} PV of Forecast FCFF: ${value:,.2f}")


# Create a dictionary to store terminal values for each scenario.
terminal_values = {}

# Calculate terminal value using the final forecast year's FCFF.
for scenario in ["bear", "base", "bull", "alt_low", "alt_mid", "alt_high"]:

    # Retrieve projected FCFF for 2030.
    final_fcff = forecast_df[f"{scenario}_fcff"].iloc[-1]

    # Calculate the value of cash flows beyond 2030.
    terminal_values[scenario] = (
        final_fcff * (1 + terminal_growth_rate)
        / (wacc - terminal_growth_rate)
    )

# Display terminal values for all three scenarios.
for scenario, value in terminal_values.items():
    print(f"{scenario.capitalize()} Terminal Value: ${value:,.2f}")


# Create dictionaries to store discounted terminal values and enterprise values.
pv_terminal_values = {}
enterprise_values = {}

# Retrieve the discount factor for the final forecast year (2030).
final_discount_factor = forecast_df["discount_factor"].iloc[-1]

# Calculate enterprise value for each scenario.
for scenario in ["bear", "base", "bull", "alt_low", "alt_mid", "alt_high"]:

    # Discount terminal value from 2030 to the 2025 valuation base date.
    pv_terminal_values[scenario] = (
        terminal_values[scenario] * final_discount_factor
    )

    # Add the present value of forecast FCFF and terminal value.
    enterprise_values[scenario] = (
        pv_forecast[scenario] + pv_terminal_values[scenario]
    )

# Display the preliminary enterprise valuations.
for scenario, value in enterprise_values.items():
    print(f"{scenario.capitalize()} Enterprise Value: ${value:,.2f}")


# Set 2025 cash, short-term investments, and debt assumptions.
cash = 2088117000
short_term_investments = 677084000
total_debt = 0

# Calculate net cash available to shareholders.
net_cash = cash + short_term_investments - total_debt

# Create a dictionary to store equity values for each scenario.
equity_values = {}

# Calculate equity value from enterprise value.
for scenario in ["bear", "base", "bull", "alt_low", "alt_mid", "alt_high"]:
    equity_values[scenario] = enterprise_values[scenario] + net_cash

# Display the preliminary equity valuations.
for scenario, value in equity_values.items():
    print(f"{scenario.capitalize()} Equity Value: ${value:,.2f}")


# Set Monster Beverage's outstanding share count from FMP.
shares_outstanding = 1957511922

# Create a dictionary to store intrinsic values per share.
intrinsic_values = {}

# Calculate intrinsic value per share for each scenario.
for scenario in ["bear", "base", "bull", "alt_low", "alt_mid", "alt_high"]:
    intrinsic_values[scenario] = (
        equity_values[scenario] / shares_outstanding
    )

# Display the preliminary intrinsic value per share.
for scenario, value in intrinsic_values.items():
    print(f"{scenario.capitalize()} Intrinsic Value Per Share: ${value:,.2f}")