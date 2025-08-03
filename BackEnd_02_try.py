from __future__ import annotations

import os
import time
from datetime import datetime
from functools import lru_cache
from typing import Tuple, List, Dict

import pandas as pd
import requests

# ---------------------------------------------------------------------------
# 🔑 Alpha Vantage setup
# ---------------------------------------------------------------------------
API_KEY = os.getenv("ALPHAVANTAGE_API_KEY", "demo")
BASE_URL = "https://www.alphavantage.co/query"
RATE_SLEEP = 12  # seconds to wait on throttling (free tier: 5 req/min)

# ---------------------------------------------------------------------------
# 📋 Sector leaders (Magnificent‑7 inclusive – 2025‑08‑02 user version)
# ---------------------------------------------------------------------------
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

# ---------------------------------------------------------------------------
# 🛠 Thin wrapper around Alpha Vantage requests with caching & back‑off
# ---------------------------------------------------------------------------

@lru_cache(maxsize=256)
def _av_request(**params) -> dict:
    """GET JSON from Alpha Vantage, retrying on rate‑limit."""
    params["apikey"] = API_KEY
    while True:
        r = requests.get(BASE_URL, params=params, timeout=10)
        r.raise_for_status()
        data = r.json()
        # Rate‑limit notice ➜ wait & retry
        if "Note" in data or "Information" in data:
            time.sleep(RATE_SLEEP)
            continue
        # Hard error (e.g. invalid call)
        if "Error Message" in data:
            raise ValueError(data["Error Message"])
        return data

# ---------------------------------------------------------------------------
# 🗂 Sector resolver via OVERVIEW endpoint (cached 12 h)
# ---------------------------------------------------------------------------

@lru_cache(maxsize=512)
def get_sector(ticker: str) -> str | None:
    """Return GICS sector for *ticker* using OVERVIEW endpoint."""
    data = _av_request(function="OVERVIEW", symbol=ticker.upper())
    sector = data.get("Sector")
    return sector if sector else None

# ---------------------------------------------------------------------------
# 📈 Daily close helper – cached 3 h
# ---------------------------------------------------------------------------

@lru_cache(maxsize=512)
def _get_latest_two_closes(ticker: str) -> Tuple[float, float, str, str]:
    """Fetch last two daily closes; return (prev_close, last_close, prev_date, last_date)."""
    data = _av_request(function="TIME_SERIES_DAILY_ADJUSTED", symbol=ticker.upper(), outputsize="compact")
    ts: dict = data["Time Series (Daily)"]
    dates = sorted(ts.keys(), reverse=True)[:2]
    if len(dates) < 2:
        raise ValueError(f"Not enough daily data for {ticker}")
    last_close = float(ts[dates[0]]["5. adjusted close"])
    prev_close = float(ts[dates[1]]["5. adjusted close"])
    return prev_close, last_close, dates[1], dates[0]

# ---------------------------------------------------------------------------
# 🚦 Public function – sector_1d_comparison
# ---------------------------------------------------------------------------

def sector_1d_comparison(ticker: str):
    """Compare *ticker* vs. up to 4 sector leaders (Alpha Vantage)."""

    ticker = ticker.upper()
    sector = get_sector(ticker) or "Unknown"

    peers = SECTOR_LEADERS.get(sector, [])
    peers = [p for p in peers if p != ticker][:4]  # ensure ≤4
    tickers = [ticker] + peers

    rows: list[tuple] = []
    pct_list: list[float] = []

    for sym in tickers:
        prev_c, last_c, prev_d, last_d = _get_latest_two_closes(sym)
        pct = (last_c - prev_c) / prev_c * 100
        pct_list.append(pct) if sym != ticker else None
        rows.append(
            (
                "Target" if sym == ticker else "Same Sector",
                sym,
                prev_c,
                last_c,
                f"{pct:+.2f}",
            )
        )

    result = (
        pd.DataFrame(rows, columns=["Group", "Ticker", f"Close {prev_d}", f"Close {last_d}", "1‑Day %"])
        .sort_values(["Group", "1‑Day %"], ascending=[True, False])
        .reset_index(drop=True)
    )

    # Quartile logic
    tgt_pct = float(result.loc[result["Ticker"] == ticker, "1‑Day %"].str.replace("+", "").astype(float))
    q75 = pd.Series(pct_list).quantile(0.75) if pct_list else tgt_pct
    q25 = pd.Series(pct_list).quantile(0.25) if pct_list else tgt_pct

    if tgt_pct >= q75:
        status = "Leading"
        signal = +3
        text = (
            f"{ticker} is outperforming its same‑sector peers with a 1‑Day return of "
            f"{tgt_pct:.2f}%, placing it in the top quartile of sector performance."
        )
    elif tgt_pct <= q25:
        status = "Underperforming"
        signal = -3
        text = (
            f"{ticker} is underperforming its same‑sector peers with a 1‑Day return of "
            f"{tgt_pct:.2f}%, ranking in the bottom quartile.".
        )
    else:
        status = "In‑Line"
        signal = 0
        text = (
            f"{ticker} is moving in‑line with its same‑sector peers, with a 1‑Day return "
            f"of {tgt_pct:.2f}% (between the 25th and 75th percentile)."
        )

    return result, status, signal, text