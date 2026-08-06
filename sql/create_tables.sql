-- =====================================================
-- Monster Energy DCF Database Schema
-- =====================================================

CREATE TABLE company_master (
    company_id SERIAL PRIMARY KEY,
    ticker VARCHAR(10) NOT NULL,
    company_name VARCHAR(225) NOT NULL,
    sector VARCHAR(100),
    industry_name VARCHAR(100)
);

CREATE TABLE financials_annual (
    financial_id SERIAL PRIMARY KEY,
    company_id INTEGER NOT NULL,
    fiscal_year INTEGER NOT NULL,
    revenue NUMERIC,
    net_income NUMERIC,
    free_cash_flow NUMERIC,
    eps NUMERIC,

    CONSTRAINT fk_company
        FOREIGN KEY (company_id)
        REFERENCES company_master(company_id)
);

CREATE TABLE trend_data_monthly (
    trend_id SERIAL PRIMARY KEY,
    company_id INTEGER NOT NULL,
    trend_date DATE NOT NULL,
    search_term VARCHAR(100) NOT NULL,
    trend_score NUMERIC,
    data_source VARCHAR(100),

    CONSTRAINT fk_trend_company
        FOREIGN KEY (company_id)
        REFERENCES company_master(company_id)
);

CREATE TABLE store_observations (
    observation_id SERIAL PRIMARY KEY,
    company_id INTEGER NOT NULL,
    observation_date DATE NOT NULL,
    store_name TEXT,
    store_location VARCHAR(255),
    shelf_stock_level INTEGER,
    restock_frequency_days INTEGER,
    notes TEXT,

    CONSTRAINT fk_store_company
        FOREIGN KEY (company_id)
        REFERENCES company_master(company_id)
);

CREATE TABLE management_commentary (
    commentary_id SERIAL PRIMARY KEY,
    company_id INTEGER NOT NULL,
    commentary_date DATE NOT NULL,
    commentary_source VARCHAR(255),
    sentiment VARCHAR(20),
    commentary_text TEXT,

    CONSTRAINT fk_management_commentary
        FOREIGN KEY (company_id)
        REFERENCES company_master(company_id)
);