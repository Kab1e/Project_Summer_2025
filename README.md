# Project_Summer_2025 - Interactive Stock Strategy Simulator

This Simulator is a Streamlit-based stock analytics dashboard designed to help individual investors simulate profit/loss outcomes and evaluate strategic options for existing stock positions. 

Built as a final project for **IS 430**, this tool combines real-time data, user-defined scenarios, and visualization to offer strategic insights on minimizing risk and maximizing return using basic options strategies.

---

## Features

- **Smart Ticker Search & Auto-Complete**  
  Streamlit sidebar is wired to Alpha Vantage’s `SYMBOL_SEARCH` endpoint.  
  Type **≥ 2** characters and pick from a live drop-down of best matches.

- **One-Click, Three-Pillar Analysis**  
  Press **Run Analysis** and get a consolidated report built from three dedicated back-ends:  
  1. **Earnings Report** – Alpha Vantage quarterly earnings & EPS-surprise tables, QoQ/YoY growth, next call date, and a qualitative outlook score.  
  2. **Sector Performance** – 1-day relative return versus predefined sector leaders (powered by `yfinance`), with traffic-light status and signal strength.  
  3. **Macro Data Dashboard** – Sector-specific indicators (e.g., Durable Goods, INDPRO, CPI) pulled from FRED/BLS, rolled up into a “Market Expectation” verdict plus narrative.

- **Interactive DataFrames & Callouts**  
  Wide, sortable tables rendered with Streamlit’s `st.dataframe`, highlighted metrics, and color-coded info/success alerts for instant insight.

- **Clean, Responsive Streamlit UI**  
  Spinners during data fetches, responsive wide layout, and a concise sidebar that keeps controls and context in one place.

- **Modular Architecture for Easy Extension**  
  Each analytical layer lives in its own file (`BackEnd_01_Earnings.py`, `BackEnd_02_Sector_Performance.py`, `BackEnd_03_Macro_Data.py`), making it straightforward to swap data sources or bolt on new analyses.

- **Environment-Friendly Configuration**  
  Alpha Vantage API key can be set via the `ALPHAVANTAGE_API_KEY` environment variable—no hard-coding required.

