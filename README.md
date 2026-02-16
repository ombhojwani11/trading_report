# Quantitative Audit: Discretionary F&O Strategy (FY25-26)

### Project Overview
A quantitative performance audit of my discretionary trading account for Fiscal Year 2025-26. 
This repository contains the Python scripts used to audit execution efficiency, risk-adjusted returns, and time-series performance across **4,182 executions**.

### 1. Performance Statistics
*(Metrics calculated via `audit_script.py` using ledger data from Aug '25 - Feb '26)*

| Metric | Value | Note |
| :--- | :--- | :--- |
| **Net Profit (Realized)** | **₹1,20,290** | Verified Ledger P&L. |
| **Profit Factor** | **4.53** | Gross Profit / Gross Loss. |
| **Win Rate** | **47.2%** | Daily closing basis. |
| **Risk/Reward Ratio** | **1 : 5.08** | Avg Win (₹3,087) vs. Avg Loss (₹608). |
| **Max Drawdown** | **₹3,909** | < 4% of Net Profit. |

### 2. Performance Visualization
![Trading Dashboard](trading_performance_dashboard.png)

### 3. Trading Infrastructure
* **Screening Platforms:** FoxNet, TX3, TradeTiger (Sharekhan)
* **Charting & Analysis:** TradingView, Python Scripts
* **Brokers Used:** Zerodha, Dhan

### 4. Technical Workflow & AI Integration
* **Data Analysis:** Python (Pandas/Seaborn) used for post-trade analysis and performance attributions.
* **AI & Automation:** Utilized LLMs (Gemini, Grok, Claude) to accelerate Python scripting for backtesting frameworks and data visualization of multi-year historical data (~8,800+ trades over last 2 years).

### 5. Strategy Methodology
* **Approach:** Discretionary, News-based momentum.
* **Risk Profile:** Asymmetric Risk/Reward. The Profit Factor of 4.53 indicates a strategy dependent on outlier wins rather than high-frequency accuracy.
* **Execution Efficiency:** Time-series analysis identifies the **09:15 – 12:00** window as the period of highest statistical expectancy.
