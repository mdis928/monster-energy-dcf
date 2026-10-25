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

        #Quaterly mangement commentary scoring
        quarterly_scores = []
        quarterly_scores.append({
            "fiscal_year": 2026,
            "fiscal_quarter": 1,
            "theme": "distribution",
            "score": None,
            "commentary_ids": [],
            "rationale": "No distribution-related commentary detected in Q1"
        })

        quarterly_scores.append({
            "fiscal_year": 2026,
            "fiscal_quarter": 2,
            "theme": "distribution",
            "score": 0,
            "commentary_ids": [21],
            "rationale": "Management identified potential food-service distribution opportunities, but did not establish realized revenue growth from those opportunities."
        })

        quarterly_scores.append({
            "fiscal_year": 2026,
            "fiscal_quarter": 1,
            "theme": "innovation",
            "score": 1,
            "commentary_ids": [70, 75, 76, 77, 78, 79],
            "rationale": "Management reported successful product launches, innovation-driven sales growth, and positive performance from existing products."
            })


        quarterly_scores.append({
            "fiscal_year": 2026,
            "fiscal_quarter": 2,
            "theme": "innovation",
            "score": 1,
            "commentary_ids": [7, 14, 15, 16, 20],
            "rationale": "Management reported successful product launches, innovation-driven consumer recruitment, and positive sales contributions from new products."
            })  

        quarterly_scores.append({
            "fiscal_year": 2026,
            "fiscal_quarter": 1,
            "theme": "pricing_revenue_mix",
            "score": 1,
            "commentary_ids": [70, 71, 72, 74],
            "rationale": "Management reported effective pricing actions alongside continued volume growth and market-share gains, supporting revenue growth despite input-cost pressures."
            })

        quarterly_scores.append({
            "fiscal_year": 2026,
            "fiscal_quarter": 2,
            "theme": "pricing_revenue_mix",
            "score": 1,
            "commentary_ids": [7, 10, 11, 24],
            "rationale": "Management reported effective pricing strategies and low-single-digit price increases in EMEA, supporting revenue growth despite continued cost pressures."
            })

        quarterly_scores.append({
            "fiscal_year": 2026,
            "fiscal_quarter": 1,
            "theme": "consumer_demand",
            "score": 1,
            "commentary_ids": [70, 74, 79, 81],
            "rationale": "Management commentary indicated continued consumer demand and positive sales momentum, supporting revenue growth."
            })

        quarterly_scores.append({
            "fiscal_year": 2026,
            "fiscal_quarter": 2,
            "theme": "consumer_demand",
            "score": 1,
            "commentary_ids": [7, 17],
            "rationale": "Management reported double-digit sales growth, increasing household penetration, and recruitment of new consumers, supporting continued revenue demand."
            })

        quarterly_scores.append({
            "fiscal_year": 2026,
            "fiscal_quarter": 1,
            "theme": "market_share",
            "score": 1,
            "commentary_ids": [70, 82],
            "rationale": "Management reported market-share gains and competitive performance supporting Monster's revenue-growth outlook."
            })

        quarterly_scores.append({
            "fiscal_year": 2026,
            "fiscal_quarter": 2,
            "theme": "market_share",
            "score": 1,
            "commentary_ids": [7, 14],
            "rationale": "Management reported market-share gains and strong competitive performance across key markets, supporting revenue growth."
            })

        quarterly_scores.append({
            "fiscal_year": 2026,
            "fiscal_quarter": 1,
            "theme": "category_growth",
            "score": 1,
            "commentary_ids": [70, 79],
            "rationale": "Management reported continued growth in the energy drink category, providing a favorable environment for Monster's revenue expansion."
            })

        quarterly_scores.append({
            "fiscal_year": 2026,
            "fiscal_quarter": 2,
            "theme": "category_growth",
            "score": 1,
            "commentary_ids": [7, 14, 17],
            "rationale": "Management reported continued energy drink category expansion, particularly in international markets, supporting Monster's revenue-growth outlook."
            })

        # Convert quarterly scores into a DataFrame
        quarterly_scores_df = pd.DataFrame(quarterly_scores)

        print("\nQuarterly Management Commentary Scores:")
        print(
            quarterly_scores_df[
                ["fiscal_year", "fiscal_quarter", "theme", "score"]
            ].to_string(index=False)
        )

        # Calculate quarterly composite scores
        quarterly_composite_df = (
            quarterly_scores_df
            .groupby(["fiscal_year", "fiscal_quarter"])["score"]
            .agg(["mean", "count"])
            .reset_index()
        )

        print("\nQuarterly Composite Scores:")
        print(quarterly_composite_df.to_string(index=False))


        # Validate one score per theme per quarter
        duplicates = quarterly_scores_df.duplicated(
            subset=["fiscal_year", "fiscal_quarter", "theme"]
        )

        print("\nDuplicate scoring records:", duplicates.sum())

        # Validate supporting commentary IDs
        valid_ids = set(commentary_df["commentary_id"])

        referenced_ids = {
            commentary_id
            for ids in quarterly_scores_df["commentary_ids"]
            for commentary_id in ids
        }

        missing_ids = referenced_ids - valid_ids

        print("\nMissing commentary IDs:", missing_ids)

        quarter_mismatches = []

    for _, row in quarterly_scores_df.iterrows():
        for commentary_id in row["commentary_ids"]:
            source = commentary_df[
                commentary_df["commentary_id"] == commentary_id
            ]

            if not source.empty:
                record = source.iloc[0]

                if (
                    record["fiscal_year"] != row["fiscal_year"]
                    or record["fiscal_quarter"] != row["fiscal_quarter"]
                ):
                    quarter_mismatches.append(commentary_id)
        print("\nQuarter mismatches:", quarter_mismatches)


        

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