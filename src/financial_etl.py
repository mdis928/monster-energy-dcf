import requests
import pandas as pd

from config import FMP_API_KEY

ticker = "MNST"

url = (
    f"https://financialmodelingprep.com/stable/income-statement"
    f"?symbol={ticker}"
    f"&apikey={FMP_API_KEY}"
)

response = requests.get(url, timeout=30)
response.raise_for_status()

data = response.json()

df = pd.DataFrame(data)

financials_df = df[
    ["fiscalYear", "revenue", "netIncome", "eps"]
].copy()

financials_df = financials_df.rename(
    columns={
        "fiscalYear": "fiscal_year",
        "netIncome": "net_income"
    }
)

financials_df["company_id"] = 1
financials_df["free_cash_flow"] = None

financials_df = financials_df[
    [
        "company_id",
        "fiscal_year",
        "revenue",
        "net_income",
        "free_cash_flow",
        "eps"
    ]
]

print(financials_df)

