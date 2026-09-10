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
#print(response.json())


earnings_call_url = f"{url}/{ticker}"

earnings_call_params = {
    "fiscal_year": 2026,
    "fiscal_quarter": 2
}

earnings_call_response = requests.get(
    earnings_call_url,
    headers=headers,
    params=earnings_call_params
)

print(earnings_call_response.status_code)
# print(earnings_call_response.json())

call_data = earnings_call_response.json()
transcript_data = call_data["transcript"]
earnings_call_df = pd.DataFrame(transcript_data)

#print(earnings_call_df)

management_speakers = [
    "Hilton Schlosberg",
    "Tom Kelly",
    "Rob Gehring",
    "Guy Carling",
    "Mike Rodriguez",
    "Emelie Tirre",
    "Mark Astrachan"
]

management_df = earnings_call_df[
    earnings_call_df["speaker"].isin(management_speakers)
]

print(management_df)