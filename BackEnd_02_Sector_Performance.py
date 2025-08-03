import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

# Part 2 of Project IS 430:

YF_TO_GICS = {
    "basic-materials":       "Materials",
    "communication-services":"Communication Services",
    "consumer-cyclical":     "Consumer Discretionary",
    "consumer-defensive":    "Consumer Staples",
    "energy":                "Energy",
    "financial-services":    "Financials",
    "healthcare":            "Health Care",
    "industrials":           "Industrials",
    "real-estate":           "Real Estate",
    "technology":            "Information Technology",
    "utilities":             "Utilities"
}

SECTOR_LEADERS = {
    "Communication Services": ["META", "GOOGL", "TMUS", "VZ"],
    "Consumer Discretionary": ["AMZN", "TSLA", "F", "HD"],
    "Consumer Staples": ["COST", "PG", "WMT", "KO"],
    "Energy": ["XOM", "CVX", "COP", "SLB"],
    "Financials": ["JPM", "BAC", "GS", "MS"],
    "Health Care": ["JNJ", "PFE", "UNH", "ABBV"],
    "Industrials": ["GE", "HON", "UPS", "CAT"],
    "Information Technology": ["AAPL", "MSFT", "NVDA", "PLTR"], 
    "Materials": ["NEM", "LIN", "APD", "FCX"],
    "Real Estate": ["PLD", "SPG", "CCI", "O"],
    "Utilities": ["NEE", "DUK", "SO", "EXC"] 
}

def get_sector(ticker):
    Target_ticker_info = yf.Ticker(ticker).info
    YF_sector_key = Target_ticker_info.get("sectorKey")
    GICS_sector_key = YF_TO_GICS.get(YF_sector_key, None)
    return GICS_sector_key

def Companies_in_Same_Sector_for_comparison(ticker):
    GICS_sector_key = get_sector(ticker)

    if GICS_sector_key in SECTOR_LEADERS:
        companies_in_same_sector = SECTOR_LEADERS[GICS_sector_key]
        if ticker in companies_in_same_sector:
            companies_to_compare =  [t for t in companies_in_same_sector if t != ticker]
        else:
            companies_to_compare = companies_in_same_sector[:3]
        return companies_to_compare
    else:
        return f"SOMETHING WENT WRONG"

def sector_1d_comparison(ticker):
    same_sector = Companies_in_Same_Sector_for_comparison(ticker)
    tickers = [ticker] + same_sector
    end = datetime.now()
    start = end - timedelta(days=1)
    raw = yf.download(
        tickers,
        start=start.strftime("%Y-%m-%d"),
        end=end.strftime("%Y-%m-%d"),
        interval="1m",
        group_by="ticker",
        progress=False
    )
    
    rows = []
    rows_compare = []
    for sym in tickers:
        df = raw[sym] if isinstance(raw.columns, pd.MultiIndex) else raw

        open_p = df["Open"].dropna().iloc[0]
        last_p = df["Close"].dropna().iloc[-1]
        pct = (last_p - open_p) / open_p * 100

        group = (
            "Target"         if sym == ticker else
            "Same Sector"    if sym in same_sector else
            "ERROR!!!"
        )
        rows.append((group, sym, open_p, last_p, f"{pct:+.3f}"))
        rows_compare.append((group, sym, pct))
    
    result = pd.DataFrame(rows, columns=["Group", "Ticker", "Open", "Last", "1D % Change"])
    result = result.sort_values(["Group","1D % Change"], ascending=[True, False]).reset_index(drop=True)

    for_analysis = pd.DataFrame(rows_compare, columns=["Group", "Ticker", "1D % Change"])

    target_pct = for_analysis.loc[for_analysis["Ticker"] == ticker, "1D % Change"].iat[0]
    comparison_pct = for_analysis[for_analysis["Group"] == "Same Sector"]

    q75 = comparison_pct["1D % Change"].quantile(0.75)
    q25 = comparison_pct["1D % Change"].quantile(0.25)

    if target_pct >= q75:
        status = "Leading"
        same_sector_performance = +3
        text = (
            f"{ticker} is outperforming its same‐sector peers with a 1D return of "
            f"{target_pct:.2f}%, placing it in the top quartile of sector performance."
        )
    elif target_pct <= q25:
        status = "Underperforming"
        same_sector_performance = -3
        text = (
            f"{ticker} is underperforming its same‐sector peers with a 1D return of "
            f"{target_pct:.2f}%, ranking in the bottom quartile."
        )
    else:
        status = "In-Line"
        same_sector_performance = 0
        text = (
            f"{ticker} is moving in‐line with its same‐sector peers, with a 1D return "
            f"of {target_pct:.2f}% (between the 25th and 75th percentile)."
        )

    return result, status, same_sector_performance, text