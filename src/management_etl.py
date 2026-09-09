import requests
import pandas as pd

from config import ROIC_API_KEY

ticker = "NASDAQ:MNST"

url = "https://api.roic.ai/v3.0.0/earnings-calls"

headers = {
    "Authorization": f"Bearer {ROIC_API_KEY}"
}

params = {
    "identifier": ticker
}

response = requests.get(url, headers=headers, params=params)

print(response.status_code)
print(response.json())


