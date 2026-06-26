-- DIMENSION: Fund
CREATE TABLE IF NOT EXISTS dim_fund (
    amfi_code       INTEGER PRIMARY KEY,
    scheme_name     TEXT NOT NULL,
    fund_house      TEXT,
    category        TEXT,
    sub_category    TEXT,
    scheme_type     TEXT,
    risk_grade      TEXT,
    launch_date     DATE
);

-- DIMENSION: Date
CREATE TABLE IF NOT EXISTS dim_date (
    date_id         INTEGER PRIMARY KEY,  -- format: YYYYMMDD
    full_date       DATE NOT NULL,
    day             INTEGER,
    month           INTEGER,
    month_name      TEXT,
    quarter         INTEGER,
    year            INTEGER,
    is_weekend      INTEGER               -- 0 or 1
);

-- FACT: NAV History
CREATE TABLE IF NOT EXISTS fact_nav (
    nav_id          INTEGER PRIMARY KEY AUTOINCREMENT,
    amfi_code       INTEGER REFERENCES dim_fund(amfi_code),
    date_id         INTEGER REFERENCES dim_date(date_id),
    nav             REAL NOT NULL CHECK(nav > 0)
);

-- FACT: Investor Transactions
CREATE TABLE IF NOT EXISTS fact_transactions (
    txn_id              INTEGER PRIMARY KEY AUTOINCREMENT,
    amfi_code           INTEGER REFERENCES dim_fund(amfi_code),
    date_id             INTEGER REFERENCES dim_date(date_id),
    investor_id         TEXT,
    transaction_type    TEXT CHECK(transaction_type IN ('SIP','Lumpsum','Redemption')),
    amount              REAL CHECK(amount > 0),
    units               REAL,
    state               TEXT,
    kyc_status          TEXT
);

-- FACT: Scheme Performance
CREATE TABLE IF NOT EXISTS fact_performance (
    perf_id         INTEGER PRIMARY KEY AUTOINCREMENT,
    amfi_code       INTEGER REFERENCES dim_fund(amfi_code),
    as_of_date_id   INTEGER REFERENCES dim_date(date_id),
    return_1yr      REAL,
    return_3yr      REAL,
    return_5yr      REAL,
    expense_ratio   REAL,
    sharpe_ratio    REAL,
    alpha           REAL,
    beta            REAL
);

-- FACT: AUM
CREATE TABLE IF NOT EXISTS fact_aum (
    aum_id          INTEGER PRIMARY KEY AUTOINCREMENT,
    amfi_code       INTEGER REFERENCES dim_fund(amfi_code),
    date_id         INTEGER REFERENCES dim_date(date_id),
    aum_crore       REAL CHECK(aum_crore >= 0),
    net_inflow      REAL,
    net_outflow     REAL
);