-- ============================================================
-- Bluestock MF Capstone — 10 Analytical SQL Queries (D2)
-- ============================================================
-- Run individual queries in MySQL Workbench or:
-- mysql -u root -p mf_analytics < sql/queries.sql
-- ============================================================

USE mf_analytics;

-- Q1: Top 5 Fund Houses by Total AUM (lakh crore)
SELECT
    fund_house,
    ROUND(SUM(aum_lakh_crore), 2)  AS total_aum_lakh_crore,
    ROUND(SUM(aum_crore), 0)       AS total_aum_crore,
    COUNT(DISTINCT num_schemes)    AS scheme_count
FROM fact_aum
GROUP BY fund_house
ORDER BY total_aum_lakh_crore DESC
LIMIT 5;

-- Q2: Average NAV per Month (all funds)
SELECT
    d.year,
    d.month_name,
    ROUND(AVG(n.nav), 2) AS avg_nav,
    COUNT(*)             AS data_points
FROM fact_nav n
JOIN dim_date d ON n.date_id = d.date_id
GROUP BY d.year, d.month, d.month_name
ORDER BY d.year, d.month;

-- Q3: SIP Inflow YoY Growth
SELECT
    year,
    total_sip_crore,
    LAG(total_sip_crore) OVER (ORDER BY year)  AS prev_year_crore,
    ROUND(
        (total_sip_crore - LAG(total_sip_crore) OVER (ORDER BY year))
        / LAG(total_sip_crore) OVER (ORDER BY year) * 100,
    2) AS yoy_growth_pct
FROM (
    SELECT
        YEAR(STR_TO_DATE(d.full_date, '%Y-%m-%d'))  AS year,
        ROUND(SUM(t.amount_inr) / 10000000, 2)      AS total_sip_crore
    FROM fact_transactions t
    JOIN dim_date d ON t.date_id = d.date_id
    WHERE t.transaction_type = 'SIP'
    GROUP BY year
) yearly;

-- Q4: Transaction Amount by State (Top 10)
SELECT
    state,
    COUNT(*)                              AS txn_count,
    ROUND(SUM(amount_inr) / 10000000, 2) AS total_amount_crore,
    ROUND(AVG(amount_inr), 0)            AS avg_amount_inr
FROM fact_transactions
GROUP BY state
ORDER BY total_amount_crore DESC
LIMIT 10;

-- Q5: Funds with Expense Ratio < 1% (Value picks)
SELECT
    f.scheme_name,
    f.fund_house,
    f.category,
    p.expense_ratio,
    p.return_3yr_pct,
    p.sharpe_ratio
FROM fact_performance p
JOIN dim_fund f ON p.amfi_code = f.amfi_code
WHERE p.expense_ratio < 1.0
ORDER BY p.expense_ratio ASC;

-- Q6: Top 10 Funds by 3-Year Return
SELECT
    f.scheme_name,
    f.fund_house,
    f.category,
    p.return_3yr_pct,
    p.return_1yr_pct,
    p.expense_ratio
FROM fact_performance p
JOIN dim_fund f ON p.amfi_code = f.amfi_code
WHERE p.return_3yr_pct IS NOT NULL
ORDER BY p.return_3yr_pct DESC
LIMIT 10;

-- Q7: Monthly SIP Inflow Trend
SELECT
    d.year,
    d.month,
    d.month_name,
    ROUND(SUM(t.amount_inr) / 10000000, 2) AS sip_inflow_crore,
    COUNT(DISTINCT t.investor_id)           AS unique_investors
FROM fact_transactions t
JOIN dim_date d ON t.date_id = d.date_id
WHERE t.transaction_type = 'SIP'
GROUP BY d.year, d.month, d.month_name
ORDER BY d.year, d.month;

-- Q8: KYC Status Breakdown with Percentage
SELECT
    kyc_status,
    COUNT(*) AS investor_count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) AS percentage
FROM fact_transactions
GROUP BY kyc_status
ORDER BY investor_count DESC;

-- Q9: Category-wise Average Returns Comparison
SELECT
    f.category,
    COUNT(DISTINCT p.amfi_code)      AS num_funds,
    ROUND(AVG(p.return_1yr_pct), 2) AS avg_return_1yr,
    ROUND(AVG(p.return_3yr_pct), 2) AS avg_return_3yr,
    ROUND(AVG(p.return_5yr_pct), 2) AS avg_return_5yr,
    ROUND(AVG(p.expense_ratio),  2) AS avg_expense_ratio
FROM fact_performance p
JOIN dim_fund f ON p.amfi_code = f.amfi_code
GROUP BY f.category
ORDER BY avg_return_3yr DESC;

-- Q10: Top 10 Risk-Adjusted Funds (Sharpe Ratio)
SELECT
    f.scheme_name,
    f.fund_house,
    f.category,
    p.sharpe_ratio,
    p.return_3yr_pct,
    p.expense_ratio,
    p.max_drawdown_pct
FROM fact_performance p
JOIN dim_fund f ON p.amfi_code = f.amfi_code
WHERE p.sharpe_ratio IS NOT NULL
ORDER BY p.sharpe_ratio DESC
LIMIT 10;
