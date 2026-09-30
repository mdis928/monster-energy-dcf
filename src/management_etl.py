import requests
import pandas as pd
import hashlib

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

available_calls_data = response.json()
available_calls = available_calls_data["data"]

print(response.status_code)
#print(response.json())
print(available_calls)

management_dfs = []

management_speakers = [
    "Hilton Schlosberg",
    "Tom Kelly",
    "Rob Gehring",
    "Guy Carling",
    "Mike Rodriguez",
    "Emelie Tirre",
    "Mark Astrachan"
]

for call in available_calls:
    fiscal_year = call["fiscal_year"]
    fiscal_quarter = call ["fiscal_quarter"]
    print(fiscal_year, fiscal_quarter)


    earnings_call_url = f"{url}/{ticker}"

    earnings_call_params = {
    "fiscal_year": fiscal_year,
    "fiscal_quarter": fiscal_quarter
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

    management_df = earnings_call_df[
        earnings_call_df["speaker"].isin(management_speakers)
    ]

    fiscal_year = call_data["fiscal_year"]
    management_df["fiscal_year"] = fiscal_year

    fiscal_quarter = call_data["fiscal_quarter"]
    management_df["fiscal_quarter"] = fiscal_quarter

    call_date = call_data["date"]
    management_df["call_date"] = call_date


    management_df["company_id"] = 1

    management_df["commentary_source"] = "ROIC.ai Earnings Call"


    management_df = management_df.rename(
        columns={
            "text": "commentary_text",
    
        }
    )

    management_df["commentary_hash"] = management_df["commentary_text"].apply(
        lambda text: hashlib.sha256(text.encode("utf-8")).hexdigest()
    )


    management_df = management_df[
        [
        "company_id",
        "call_date",
        "commentary_source",
        "commentary_text",
        "commentary_hash",
        "fiscal_year",
        "fiscal_quarter",
        "speaker"
        ]
        ]

    management_dfs.append(management_df)


management_df = pd.concat(management_dfs, ignore_index=True)


print(management_df.columns)
print(management_df.head())
print(management_df["fiscal_quarter"].value_counts())

