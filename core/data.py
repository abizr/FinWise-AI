import datetime as dt
import math
from functools import lru_cache
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd
import requests

try:
    import yfinance as yf  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    yf = None

COINGECKO_BASE = "https://api.coingecko.com/api/v3"


@lru_cache(maxsize=16)
def fetch_crypto_ohlc(coin_id: str = "bitcoin", days: int = 90) -> pd.DataFrame:
    """Fetch OHLC data from CoinGecko with graceful fallbacks."""
    days = max(7, min(int(days or 90), 365))
    try:
        url = f"{COINGECKO_BASE}/coins/{coin_id}/ohlc"
        resp = requests.get(
            url,
            params={"vs_currency": "usd", "days": days},
            timeout=12,
        )
        resp.raise_for_status()
        payload = resp.json()
        if payload:
            frame = pd.DataFrame(payload, columns=["timestamp", "open", "high", "low", "close"])
            frame["date"] = pd.to_datetime(frame["timestamp"], unit="ms")
            frame = frame.sort_values("date").reset_index(drop=True)
            return frame[["date", "open", "high", "low", "close"]]
    except Exception:
        # CoinGecko can rate-limit; fall back to yfinance or synthetic data.
        pass

    return fetch_crypto_ohlc_yf(coin_id, days)


def fetch_crypto_ohlc_yf(coin_id: str, days: int = 90) -> pd.DataFrame:
    if yf is None:
        return build_synthetic_ohlc(days)

    symbol_map = {
        "bitcoin": "BTC-USD",
        "ethereum": "ETH-USD",
        "solana": "SOL-USD",
        "dogecoin": "DOGE-USD",
    }
    ticker = symbol_map.get(coin_id.lower(), f"{coin_id.upper()}-USD")
    period = f"{days}d" if days <= 365 else "max"
    data = yf.download(ticker, period=period, interval="1d", progress=False)
    if not data.empty:
        data = data.reset_index().rename(
            columns={
                "Date": "date",
                "Open": "open",
                "High": "high",
                "Low": "low",
                "Close": "close",
            }
        )
        return data[["date", "open", "high", "low", "close"]]

    return build_synthetic_ohlc(days)


def build_synthetic_ohlc(days: int = 90) -> pd.DataFrame:
    """Offline-friendly synthetic series to keep demos working."""
    days = max(30, days)
    today = dt.datetime.utcnow()
    base = np.linspace(0, math.pi * 2, days)
    noise = np.random.normal(scale=0.5, size=days)
    trend = np.linspace(0, 3, days)
    close = 100 + 5 * np.sin(base) + trend + noise
    open_price = close + np.random.normal(scale=0.6, size=days)
    high = np.maximum(open_price, close) + np.random.uniform(0.2, 1.2, size=days)
    low = np.minimum(open_price, close) - np.random.uniform(0.2, 1.2, size=days)
    dates = [today - dt.timedelta(days=i) for i in range(days)][::-1]
    df = pd.DataFrame(
        {
            "date": pd.to_datetime(dates),
            "open": open_price,
            "high": high,
            "low": low,
            "close": close,
        }
    )
    return df.reset_index(drop=True)


def fetch_news(topic: str = "crypto", limit: int = 5) -> List[Dict[str, str]]:
    """Lightweight news fetch with a static fallback."""
    try:
        resp = requests.get(
            "https://gnews.io/api/v4/search",
            params={"q": topic, "token": "demo", "lang": "en", "max": limit},
            timeout=8,
        )
        if resp.ok:
            payload = resp.json()
            articles = payload.get("articles") or []
            return [
                {"title": item.get("title", ""), "description": item.get("description", "")}
                for item in articles[:limit]
            ]
    except Exception:
        pass

    fallback = [
        {
            "title": "Volume pasar kripto stabil",
            "description": "Trader menunggu rilis data makro saat volatilitas menurun.",
        },
        {
            "title": "Adopsi institusi meningkat",
            "description": "Beberapa manajer aset melaporkan peningkatan minat pada BTC dan ETH.",
        },
    ]
    return fallback[:limit]


def get_latest_crypto_price(coin_id: str = "bitcoin") -> Tuple[float, float]:
    """Return last close and day percent change if available."""
    df = fetch_crypto_ohlc(coin_id, days=30)
    if df.empty:
        return 0.0, 0.0
    last = df.iloc[-1]["close"]
    prev = df.iloc[-2]["close"] if len(df) > 1 else last
    pct = (last - prev) / prev if prev else 0.0
    return float(last), float(pct)


def get_stock_price(ticker: str = "^GSPC") -> Tuple[float, float]:
    """Fetch stock close and daily pct change from yfinance with fallback."""
    if yf is None:
        base = 4300.0 if ticker.upper() == "^GSPC" else 150.0
        return base, 0.003

    data = yf.download(ticker, period="5d", interval="1d", progress=False)
    if not data.empty:
        last = data["Close"].iloc[-1]
        prev = data["Close"].iloc[-2] if len(data) > 1 else last
        pct = (last - prev) / prev if prev else 0.0
        return float(last), float(pct)

    # Simple fallback for offline demo.
    base = 4300.0 if ticker.upper() == "^GSPC" else 150.0
    return base, 0.003
