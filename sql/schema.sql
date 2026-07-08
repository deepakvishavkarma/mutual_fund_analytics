-- ============================================================
-- Bluestock MF Capstone — MySQL Star Schema (D2)
-- ============================================================
-- Run: mysql -u root -p < sql/schema.sql
-- ============================================================

CREATE DATABASE IF NOT EXISTS mf_analytics
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE mf_analytics;

-- DIMENSION: Fund
CREATE TABLE IF NOT EXISTS dim_fund (
    amfi_code     INT PRIMARY KEY,
    scheme_name   VARCHAR(255) NOT NULL,
    fund_house    VARCHAR(150),
    category      VARCHAR(100),
    sub_category  VARCHAR(100),
    scheme_type   VARCHAR(50),
    risk_grade    VARCHAR(50),
    launch_date   DATE,
    benchmark     VARCHAR(150),
    sebi_category VARCHAR(20)
);

-- DIMENSION: Date
CREATE TABLE IF NOT EXISTS dim_date (
    date_id     INT PRIMARY KEY,       -- YYYYMMDD format
    full_date   DATE NOT NULL,
    day         TINYINT,
    month       TINYINT,
    month_name  VARCHAR(20),
    quarter     TINYINT,
    year        SMALLINT,
    is_weekend  TINYINT(1)             -- 1=Sat/Sun, 0=weekday
);

-- FACT: NAV History
CREATE TABLE IF NOT EXISTS fact_nav (
    nav_id    INT AUTO_INCREMENT PRIMARY KEY,
    amfi_code INT NOT NULL,
    date_id   INT,
    nav       DECIMAL(12,4) NOT NULL CHECK (nav > 0),
    FOREIGN KEY (amfi_code) REFERENCES dim_fund(amfi_code),
    FOREIGN KEY (date_id)   REFERENCES dim_date(date_id),
    UNIQUE KEY uq_nav (amfi_code, date_id)
);

-- FACT: Investor Transactions
CREATE TABLE IF NOT EXISTS fact_transactions (
    txn_id           INT AUTO_INCREMENT PRIMARY KEY,
    amfi_code        INT,
    date_id          INT,
    investor_id      VARCHAR(50),
    transaction_type ENUM('SIP', 'Lumpsum', 'Redemption') NOT NULL,
    amount_inr       DECIMAL(15,2) CHECK (amount_inr > 0),
    units            DECIMAL(12,4),
    state            VARCHAR(50),
    city             VARCHAR(100),
    city_tier        ENUM('T30','B30'),
    age_group        VARCHAR(20),
    gender           VARCHAR(10),
    kyc_status       VARCHAR(30),
    FOREIGN KEY (amfi_code) REFERENCES dim_fund(amfi_code),
    FOREIGN KEY (date_id)   REFERENCES dim_date(date_id)
);

-- FACT: Scheme Performance
CREATE TABLE IF NOT EXISTS fact_performance (
    perf_id        INT AUTO_INCREMENT PRIMARY KEY,
    amfi_code      INT,
    return_1yr_pct DECIMAL(8,2),
    return_3yr_pct DECIMAL(8,2),
    return_5yr_pct DECIMAL(8,2),
    expense_ratio  DECIMAL(5,2),
    sharpe_ratio   DECIMAL(8,4),
    sortino_ratio  DECIMAL(8,4),
    alpha          DECIMAL(8,4),
    beta           DECIMAL(8,4),
    max_drawdown   DECIMAL(8,4),
    aum_crore      DECIMAL(15,2),
    FOREIGN KEY (amfi_code) REFERENCES dim_fund(amfi_code)
);

-- FACT: AUM by Fund House
CREATE TABLE IF NOT EXISTS fact_aum (
    aum_id          INT AUTO_INCREMENT PRIMARY KEY,
    date_id         INT,
    fund_house      VARCHAR(150),
    aum_lakh_crore  DECIMAL(10,4),      -- industry-level, e.g. 6.05
    aum_crore       DECIMAL(15,2),      -- scheme-level, e.g. 605000
    num_schemes     INT,
    FOREIGN KEY (date_id) REFERENCES dim_date(date_id)
);

-- FACT: Fund Scorecard
CREATE TABLE IF NOT EXISTS fact_scorecard (
    score_id        INT AUTO_INCREMENT PRIMARY KEY,
    amfi_code       INT,
    final_rank      INT,
    composite_score DECIMAL(6,2),
    cagr_3yr        DECIMAL(8,4),
    sharpe_ratio    DECIMAL(8,4),
    alpha           DECIMAL(8,4),
    expense_ratio   DECIMAL(5,2),
    max_drawdown    DECIMAL(8,4),
    FOREIGN KEY (amfi_code) REFERENCES dim_fund(amfi_code)
);
