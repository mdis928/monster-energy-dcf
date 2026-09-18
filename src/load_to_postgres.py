import psycopg

from config import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD
from financial_etl import financials_df
from management_etl import management_df


insert_query = """
    INSERT INTO financials_annual (
        company_id,
        fiscal_year,
        revenue,
        net_income,
        free_cash_flow,
        eps
    )
    VALUES (%s, %s, %s, %s, %s, %s)
    ON CONFLICT (company_id, fiscal_year)
    DO UPDATE SET
        revenue = EXCLUDED.revenue,
        net_income = EXCLUDED.net_income,
        free_cash_flow = EXCLUDED.free_cash_flow,
        eps = EXCLUDED.eps;
"""

management_insert_query  = """
    INSERT INTO management_commentary (
        company_id,
        call_date,
        commentary_source,
        commentary_text,
        commentary_hash,
        fiscal_year,
        fiscal_quarter,
        speaker  
)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
   ON CONFLICT (
    company_id,
    fiscal_year,
    fiscal_quarter,
    speaker,
    commentary_hash
)
DO NOTHING
"""

try:
    with psycopg.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    ) as conn:

        with conn.cursor() as cursor:
            for row in financials_df.itertuples(index=False, name=None):
                cursor.execute(insert_query, row)

        conn.commit()

        with conn.cursor() as cursor:
            for row in management_df.itertuples(index=False, name=None):
                cursor.execute(management_insert_query, row)

        conn.commit()

    print(f"Successfully loaded {len(financials_df)} financial records.")

except Exception as error:
    print(f"Database load failed: {error}")