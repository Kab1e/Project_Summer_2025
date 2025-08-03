from __future__ import annotations

import os
import time
from functools import lru_cache
from typing import List, Dict, Tuple

import pandas as pd
import requests
import yfinance as yf

API_KEY = os.getenv("ALPHAVANTAGE_API_KEY", "9THYPTW9AE1DRHYJ")
BASE_URL = "https://www.alphavantage.co/query"
RATE_SLEEP = 0.3  # tuned for 75 req/min

SECTOR_LEADERS: Dict[str, List[str]] = {
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
    "Utilities": ["NEE", "DUK", "SO", "EXC"],
}

YF_TO_GICS: Dict[str, str] = {
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
    "utilities":             "Utilities",
}

@lru_cache(maxsize=512)
def get_sector(ticker: str) -> str | None:
    """Return canonical GICS sector for *ticker* using **yfinance**."""
    try:
        info = yf.Ticker(ticker).get_info()
        raw_key = info.get("sectorKey") or info.get("sector")
        if raw_key is None:
            return None
        return YF_TO_GICS.get(str(raw_key).lower(), raw_key)
    except Exception:
        return None

@lru_cache(maxsize=256)
def _av_request(**params) -> dict:
    params["apikey"] = API_KEY
    while True:
        r = requests.get(BASE_URL, params=params, timeout=10)
        r.raise_for_status()
        data = r.json()
        if "Note" in data or "Information" in data:
            time.sleep(RATE_SLEEP)
            continue
        if "Error Message" in data:
            raise ValueError(data["Error Message"])
        return data

@lru_cache(maxsize=512)
def _get_latest_two_closes(ticker: str) -> Tuple[float, float, str, str]:
    ts = _av_request(
        function="TIME_SERIES_DAILY_ADJUSTED",
        symbol=ticker.upper(),
        outputsize="compact",
    )["Time Series (Daily)"]
    dates = sorted(ts.keys(), reverse=True)[:2]
    last_c = float(ts[dates[0]]["5. adjusted close"])
    prev_c = float(ts[dates[1]]["5. adjusted close"])
    return prev_c, last_c, dates[1], dates[0]

def sector_1d_comparison(ticker: str):
    ticker = ticker.upper()
    sector = get_sector(ticker) or "Unknown"

    peers = [p for p in SECTOR_LEADERS.get(sector, []) if p != ticker][:4]
    tickers = [ticker] + peers

    rows, peer_pct = [], []
    for sym in tickers:
        prev_c, last_c, prev_d, last_d = _get_latest_two_closes(sym)
        pct = (last_c - prev_c) / prev_c * 100
        if sym != ticker:
            peer_pct.append(pct)
        rows.append(("Target" if sym == ticker else "Same Sector", sym, prev_c, last_c, f"{pct:+.2f}"))

    df = (
        pd.DataFrame(rows, columns=["Group", "Ticker", f"Close {prev_d}", f"Close {last_d}", "1-Day %"])
        .sort_values(["Group", "1-Day %"], ascending=[True, False])
        .reset_index(drop=True)
    )

    tgt_pct = float(df.loc[df["Ticker"] == ticker, "1-Day %"].str.replace("+", "").astype(float))
    series = pd.Series(peer_pct) if peer_pct else pd.Series([tgt_pct])
    q75, q25 = series.quantile(0.75), series.quantile(0.25)

    if tgt_pct >= q75:
        status, signal = "Leading", +3
        text = (
            f"{ticker} is outperforming its same-sector peers with a 1-Day return of "
            f"{tgt_pct:.2f}%, placing it in the top quartile of sector performance."
        )
    elif tgt_pct <= q25:
        status, signal = "Underperforming", -3
        text = (
            f"{ticker} is underperforming its same-sector peers with a 1-Day return of "
            f"{tgt_pct:.2f}%, ranking in the bottom quartile."
        )
    else:
        status, signal = "In-Line", 0
        text = (
            f"{ticker} is moving in-line with its same-sector peers, with a 1-Day return "
            f"of {tgt_pct:.2f}% (between the 25th and 75th percentile)."
        )

    return df, status, signal, text