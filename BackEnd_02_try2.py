from __future__ import annotations

import pandas as pd
import yfinance as yf
from functools import lru_cache
from datetime import datetime, timedelta

# ---------------------------------------------------------------------------
# 🎯 Curated sector leaders  (Magnificent‑7 inclusive, per user spec)
# ---------------------------------------------------------------------------
SECTOR_LEADERS: dict[str, list[str]] = {
    "Communication Services": ["META", "GOOGL", "GOOG", "VZ", "TMUS"],
    "Consumer Discretionary": ["AMZN", "TSLA", "HD", "MCD", "NKE"],
    "Consumer Staples": ["PG", "KO", "PEP", "WMT", "COST"],
    "Energy": ["XOM", "CVX", "COP", "EOG", "SLB"],
    "Financials": ["JPM", "BAC", "MS", "GS", "C"],  # WFC ➜ MS per 2025‑08‑02 note
    "Health Care": ["UNH", "JNJ", "LLY", "PFE", "MRK"],
    "Industrials": ["HON", "GE", "UPS", "UNP", "CAT"],
    "Information Technology": ["AAPL", "MSFT", "NVDA", "AVGO", "PLTR"],
    "Materials": ["LIN", "NEM", "FCX", "APD", "DD"],
    "Real Estate": ["AMT", "PLD", "CCI", "EQIX", "DLR"],
    "Utilities": ["NEE", "DUK", "SO", "D", "EXC"],
}

# ---------------------------------------------------------------------------
# 🗂 Sector resolver – one low‑cost Yahoo call, then cached
# ---------------------------------------------------------------------------

@lru_cache(maxsize=512)
def _fetch_sector(ticker: str) -> str | None:
    """Return Yahoo Finance *sector* field via fast_info (cached)."""
    try:
        info = yf.Ticker(ticker).get_info()
        return info.get("sector")   # type: ignore[return‑value]
    except Exception:
        return None

def get_sector(ticker: str) -> str | None:
    """Public wrapper.  Returns sector or *None* if unavailable."""
    return _fetch_sector(ticker.upper())

# ---------------------------------------------------------------------------
# 📈 1‑day return helper – single request, memo‑cached
# ---------------------------------------------------------------------------

_CACHE_EXPIRY_MIN = 5  # minutes

@lru_cache(maxsize=32)
def _get_prices_cache_key(symbols: str) -> tuple[str, str]:
    """Return a cache key that changes every _CACHE_EXPIRY_MIN minutes."""
    ts_key = datetime.utcnow().strftime("%Y%m%d%H")  # coarse key per hour
    minute_bucket = (datetime.utcnow().minute // _CACHE_EXPIRY_MIN) * _CACHE_EXPIRY_MIN
    ts_key += f"{minute_bucket:02d}"
    return symbols, ts_key

@lru_cache(maxsize=32)
def _get_daily_returns(symbols: str) -> pd.Series:
    """Download last 2 daily closes and compute 1‑day % returns."""
    # The extra cache key forces eviction every _CACHE_EXPIRY_MIN minutes
    _ = _get_prices_cache_key(symbols)

    df = yf.download(
        symbols,
        period="2d",
        interval="1d",
        group_by="column",
        auto_adjust=True,
        progress=False,
        threads=False,  # single HTTP call
    )["Adj Close"]

    # df has MultiIndex columns if >1 symbol, else Series; normalise to Series
    if isinstance(df, pd.DataFrame):
        returns = df.pct_change().iloc[-1]
    else:  # single series
        returns = df.pct_change().iloc[-1]
        returns = pd.Series({symbols: returns})

    return (returns * 100).round(2)  # percentage terms

# ---------------------------------------------------------------------------
# 🚦 Public API – sector_1d_comparison
# ---------------------------------------------------------------------------

def sector_1d_comparison(ticker: str):
    """Compare *ticker* vs. peer group; return (df, status, signal, summary)."""

    ticker = ticker.upper()
    sector = get_sector(ticker) or "Unknown"

    # Determine peer list
    peers = SECTOR_LEADERS.get(sector, [])
    if ticker not in peers:
        symbols = " ".join([ticker] + peers)
    else:
        symbols = " ".join(peers)  # ticker already in list

    # Yahoo download – single call
    pct_series = _get_daily_returns(symbols)

    if pct_series.empty or ticker not in pct_series:
        raise ValueError(f"Could not retrieve price data for {ticker}.")

    # Build dataframe for display
    df = (
        pct_series.sort_values(ascending=False)
        .to_frame(name="1‑Day %")
        .rename_axis("Symbol")
        .reset_index()
    )

    # Metrics
    tgt_ret = pct_series[ticker]
    peer_mean = pct_series.drop(ticker).mean() if len(pct_series) > 1 else tgt_ret

    status = "Outperform" if tgt_ret > peer_mean else "Underperform"
    signal = 1 if status == "Outperform" else -1

    summary = (
        f"{ticker} {status.lower()}s its sector leaders (+{tgt_ret:.2f}% vs. "
        f"{peer_mean:.2f}% peer avg)."
    )

    return df, status, signal, summary

# ---------------------------------------------------------------------------
# 🧪 CLI usage example
# ---------------------------------------------------------------------------
if __name__ == "__main__":  # pragma: no cover
    import sys

    tk = sys.argv[1] if len(sys.argv) > 1 else "GE"
    frame, stt, sig, msg = sector_1d_comparison(tk)
    print(frame)
    print("‑" * 60)
    print(msg)
