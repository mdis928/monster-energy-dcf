import psycopg
import pandas as pd
from config import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD


select_query = """
    SELECT  
        commentary_id, 
        fiscal_year,
        fiscal_quarter,
        speaker,
        commentary_text
    FROM management_commentary;
"""

def identify_themes(text, themes):
    matches = {}

    text = text.lower()

    for theme, phrases in themes.items():
        found = [
            phrase for phrase in phrases
            if phrase.lower() in text
        ]

        if found:
            matches[theme] = found

    return matches



try:
    with psycopg.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    ) as conn:

        with conn.cursor() as cursor:
            cursor.execute(select_query)
            rows = cursor.fetchall()

            column_names = [
                "commentary_id",
                "fiscal_year",
                "fiscal_quarter",
                "speaker",
                "commentary_text"
]

            commentary_df = pd.DataFrame(rows, columns=column_names)


            management_speakers = [
                "Hilton Schlosberg",
                "Tom Kelly",
                "Rob Gehring",
                "Guy Carling",
                "Mike Rodriguez",
                "Emelie Tirre"
            ]



        revenue_themes = {
                "consumer_demand": [
                    "consumer demand",
                    "household penetration",
                    "purchase frequency",
                    "new consumers",
                    "usage occasions"
                    "new consumer",
                    "greater acceptance",
                    "household consumption",
                ],
                "market_share": [
                    "market share",
                    "share gains",
                    "gained share",
                    "share growth"
                ],
                "category_growth": [
                    "category growth",
                    "energy drink category",
                    "category expansion",
                    "category performance"
                ],
                "distribution": [
                    "distribution expansion",
                    "new distribution",
                    "new channels",
                    "expanded availability",
                    "FSOP customers",
                ],
                "innovation": [
                    "product innovation",
                    "new product launches",
                    "innovation",
                    "new flavors"
                ],
                "pricing_revenue_mix": [
                    "pricing",
                    "price increases",
                    "revenue mix",
                    "price mix"
                ]
            }

        commentary_df = commentary_df[
            commentary_df["speaker"].isin(management_speakers)
        ].copy()

        commentary_df["theme_matches"] = commentary_df["commentary_text"].apply(
            lambda text: identify_themes(text, revenue_themes)
        )

        matched_records = commentary_df["theme_matches"].apply(bool).sum()

        total_records = len(commentary_df)

        coverage = (matched_records / total_records) * 100

        print(f"Records with matches: {matched_records}/{total_records}")
        print(f"Detection coverage: {coverage:.1f}%")

        matched_df = commentary_df[
        commentary_df["theme_matches"].apply(bool)
        ].copy()

        theme_rows = []

        for _, row in matched_df.iterrows():
            for theme, phrases in row["theme_matches"].items():
                theme_rows.append({
            "commentary_id": row["commentary_id"],
            "fiscal_year": row["fiscal_year"],
            "fiscal_quarter": row["fiscal_quarter"],
            "theme": theme,
            "matched_phrases": ", ".join(phrases),
            "commentary_text": row["commentary_text"]
        })

        theme_df = pd.DataFrame(theme_rows)

        print(
    theme_df.groupby(
        ["fiscal_year", "fiscal_quarter", "theme"]
    ).size().to_string()
)
        
        
        consumer_df = theme_df[
        theme_df["theme"] == "consumer_demand"
]
        market_df = theme_df[
    theme_df["theme"] == "market_share"
]
        category_df = theme_df[
    theme_df["theme"] == "category_growth"
]
        print(
            category_df[
                ["commentary_id", "fiscal_quarter", "matched_phrases"]
            ].to_string(index=False)
        )

        print(
    market_df[
        ["commentary_id", "fiscal_quarter", "matched_phrases"]
    ].to_string(index=False)
)

        print(
    consumer_df[
       ["commentary_id", "fiscal_quarter", "matched_phrases"]
    ].to_string(index=False)
)
        print(
    consumer_df.loc[
        consumer_df["commentary_id"] == 17,
        "commentary_text"
        ].iloc[0]
)
        print(
    category_df.loc[
        category_df["commentary_id"] == 7,
        "commentary_text"
    ].iloc[0]
)
        distribution_df = theme_df[
    theme_df["theme"] == "distribution"
]
        print(
    distribution_df.loc[
        distribution_df["commentary_id"] == 21,
        "commentary_text"
    ].iloc[0]
)
        
        print(
    distribution_df[
        ["commentary_id", "fiscal_quarter", "matched_phrases"]
    ].to_string(index=False)
) 
        innovation_df = theme_df[
        theme_df["theme"] == "innovation"
]

        print(
    innovation_df[
        ["commentary_id", "fiscal_quarter", "matched_phrases"]
    ].to_string(index=False)
)  

        for _, row in innovation_df[
                innovation_df["fiscal_quarter"] == 2
        ].iterrows():
            print(f"\nCommentary ID: {row['commentary_id']}")
            print(row["commentary_text"])
        
        pricing_df = theme_df[
            theme_df["theme"] == "pricing_revenue_mix"
]


        print(
            pricing_df[
            ["commentary_id", "fiscal_quarter", "matched_phrases"]
            ].to_string(index=False)
)

        for _, row in pricing_df[
                pricing_df["fiscal_quarter"] == 1
            ].iterrows():
            print(f"\nCommentary ID: {row['commentary_id']}")
            print(row["commentary_text"])


        print("\n========== Q2 PRICING - ID 24 ==========")
        print(
            pricing_df.loc[
                pricing_df["commentary_id"] == 24,
                "commentary_text"
            ].iloc[0]
)


        print(
        matched_df[
        ["commentary_id", "fiscal_year", "fiscal_quarter", "theme_matches"]
        ].to_string(index=False)
)
        
        unmatched_df = commentary_df[
            commentary_df["theme_matches"].apply(lambda matches: len(matches) == 0)
        ]

        print(unmatched_df[
        ["commentary_id", "fiscal_quarter", "speaker", "commentary_text"]
        ].to_string(index=False))
    

        #print(commentary_df[["commentary_id", "theme_matches"]].to_string(index=False))
        print(commentary_df.shape)   
   

        print(f"Successfully loaded {len(rows)} management commentary records.")

except Exception as error:
    print(f"Database retrieval failed: {error}")