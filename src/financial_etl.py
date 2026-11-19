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

