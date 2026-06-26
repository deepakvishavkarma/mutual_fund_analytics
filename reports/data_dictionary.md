# Data Dictionary — Mutual Fund Analytics

## fact_nav
| Column    | Type           | Description                  | Source           |
|-----------|----------------|------------------------------|------------------|
| nav_id    | INT (PK)       | Auto-increment primary key   | Generated        |
| amfi_code | INT (FK)       | AMFI scheme identifier       | nav_history.csv  |
| date_id   | INT (FK)       | Date reference               | nav_history.csv  |
| nav       | DECIMAL(10,4)  | Net Asset Value in INR       | nav_history.csv  |

## fact_transactions
| Column           | Type           | Description                    | Source                    |
|------------------|----------------|--------------------------------|---------------------------|
| txn_id           | INT (PK)       | Auto-increment primary key     | Generated                 |
| amfi_code        | INT (FK)       | Fund scheme code               | investor_transactions.csv |
| transaction_type | ENUM           | SIP / Lumpsum / Redemption     | investor_transactions.csv |
| amount_inr       | DECIMAL(15,2)  | Transaction value in INR       | investor_transactions.csv |
| state            | VARCHAR(50)    | Indian state of investor       | investor_transactions.csv |
| kyc_status       | VARCHAR(30)    | KYC Verified/Pending/Rejected  | investor_transactions.csv |

## fact_performance
| Column        | Type          | Description                   | Source                 |
|---------------|---------------|-------------------------------|------------------------|
| expense_ratio | DECIMAL(5,2)  | Annual fund cost (%)          | scheme_performance.csv |
| return_1yr_pct| DECIMAL(8,2)  | 1-year trailing return (%)    | scheme_performance.csv |
| return_3yr_pct| DECIMAL(8,2)  | 3-year CAGR (%)               | scheme_performance.csv |
| sharpe_ratio  | DECIMAL(8,4)  | Risk-adjusted return metric   | scheme_performance.csv |
| beta          | DECIMAL(8,4)  | Volatility vs market          | scheme_performance.csv |

## dim_fund
| Column      | Type          | Description                  | Source          |
|-------------|---------------|------------------------------|-----------------|
| amfi_code   | INT (PK)      | AMFI scheme code             | fund_master.csv |
| scheme_name | VARCHAR(255)  | Full scheme name             | fund_master.csv |
| fund_house  | VARCHAR(150)  | AMC name (HDFC, SBI, etc.)  | fund_master.csv |
| risk_grade  | VARCHAR(50)   | Low / Moderate / High        | fund_master.csv |

## dim_date
| Column     | Type        | Description                    |
|------------|-------------|--------------------------------|
| date_id    | INT (PK)    | YYYYMMDD format                |
| full_date  | DATE        | Calendar date                  |
| quarter    | INT         | 1=Jan-Mar, 4=Oct-Dec           |
| is_weekend | TINYINT(1)  | 1=weekend, 0=weekday           |