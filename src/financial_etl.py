import requests
import pandas as pd

from config import FMP_API_KEY

ticker = "MNST"

income_statement_url = (
    f"https://financialmodelingprep.com/stable/income-statement"
    f"?symbol={ticker}"
    f"&apikey={FMP_API_KEY}"
)

cash_flow_url = (
    f"https://financialmodelingprep.com/stable/cash-flow-statement"
    f"?symbol={ticker}"
    f"&apikey={FMP_API_KEY}"
)

income_statement_response = requests.get(income_statement_url, timeout=30)
income_statement_response.raise_for_status()

cash_flow_response = requests.get(cash_flow_url, timeout=30)
cash_flow_response.raise_for_status()

income_statement_data = income_statement_response.json()
cash_flow_data = cash_flow_response.json()

income_statement_df = pd.DataFrame(income_statement_data)
cash_flow_df = pd.DataFrame(cash_flow_data)



# Select income statement metrics required for financial analysis and DCF modeling
income_df = income_statement_df[
    ["fiscalYear", "revenue", "netIncome", "eps", "operatingIncome"]
].copy()

# Select cash flow statement metrics needed for our DCF valuation
cash_df = cash_flow_df[
    [
        "fiscalYear",
        "freeCashFlow",
        "depreciationAndAmortization",
        "capitalExpenditure",
        "changeInWorkingCapital",
    ]
].copy()
 
financials_df = income_df.merge(
    cash_df,
    on="fiscalYear",
    how="left"
)

# Rename FMP financial statement fields to match our PostgreSQL naming convention.
financials_df = financials_df.rename(
    columns={
        "fiscalYear": "fiscal_year",
        "netIncome": "net_income",
        "freeCashFlow": "free_cash_flow",
        "operatingIncome": "operating_income",
        "depreciationAndAmortization": "depreciation_amortization",
        "capitalExpenditure": "capital_expenditure",
        "changeInWorkingCapital": "change_in_working_capital"
    }
)

financials_df["company_id"] = 1

# Select and organize the financial metrics for PostgreSQL and DCF analysis
financials_df = financials_df[
    [
        "company_id",
        "fiscal_year",
        "revenue",
        "net_income",
        "free_cash_flow",
        "eps",
        "operating_income",
        "depreciation_amortization",
        "capital_expenditure",
        "change_in_working_capital"
    ]
]

# Display the expanded historical financial dataset.
print(financials_df)


# Define the FMP balance sheet endpoint for Monster Beverage.
balance_sheet_url = (
    "https://financialmodelingprep.com/stable/balance-sheet-statement"
    f"?symbol={ticker}"
    f"&apikey={FMP_API_KEY}"
)


# Send a GET request to FMP to retrieve Monster Beverage's balance sheet.
balance_sheet_response = requests.get(balance_sheet_url, timeout=30)

# Raise an error if the API request was unsuccessful.
balance_sheet_response.raise_for_status()

# Convert the API's JSON response into Python data.
balance_sheet_data = balance_sheet_response.json()

# Convert the balance sheet data into a pandas DataFrame.
balance_sheet_df = pd.DataFrame(balance_sheet_data)

# Display the available columns and the latest balance sheet records.
print(balance_sheet_df.columns.tolist())
print(balance_sheet_df.head(3))


# Select the 2025 balance sheet to match our DCF base year.
balance_2025 = balance_sheet_df.loc[
    balance_sheet_df["date"] == "2025-12-31"
].iloc[0]

# Extract cash, short-term investments, and total debt.
cash = balance_2025["cashAndCashEquivalents"]
short_term_investments = balance_2025["shortTermInvestments"]
total_debt = balance_2025["totalDebt"]

# Display the financial figures needed for equity valuation.
print(f"2025 Cash: ${cash:,.2f}")
print(f"2025 Short-Term Investments: ${short_term_investments:,.2f}")
print(f"2025 Total Debt: ${total_debt:,.2f}")


# Display share-count-related fields available in the income statement.
share_columns = [
    column for column in income_statement_df.columns
    if "share" in column.lower()
]

print("Available share columns:", share_columns)



# Define the FMP endpoint for historical shares outstanding.
shares_url = (
    "https://financialmodelingprep.com/stable/shares-float"
    f"?symbol={ticker}"
    f"&apikey={FMP_API_KEY}"
)

# Request Monster Beverage's share count data.
shares_response = requests.get(shares_url, timeout=30)

# Check whether the API request was successful.
shares_response.raise_for_status()

# Convert the JSON response into a pandas DataFrame.
shares_df = pd.DataFrame(shares_response.json())

# Display the available share count fields.
print(shares_df.columns.tolist())
print(shares_df.head())


