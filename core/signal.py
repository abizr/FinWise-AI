from dataclasses import dataclass
from typing import Dict, List

import pandas as pd

from core.indicators import compute_macd, compute_ma, compute_rsi
from core.model import predict_next_price


@dataclass
class SignalResult:
    coin: str
    signal: str
    predicted_price: float
    predicted_change_pct: float
    indicators: Dict[str, float]
    explanation: List[str]
    model_meta: Dict
    fallback: bool = False


def hybrid_signal(df: pd.DataFrame, coin_id: str = "bitcoin") -> SignalResult:
    """Compute hybrid signal using RSI, MACD, MA50/MA200, and LSTM prediction with safe fallbacks."""
    if df is None or df.empty or "close" not in df.columns:
        return _fallback_result(coin_id, reason="no_data")

    close = pd.to_numeric(df["close"], errors="coerce").fillna(method="ffill")
    if close.isna().all():
        return _fallback_result(coin_id, reason="invalid_close_series")

    rsi_series = compute_rsi(close)
    macd_frame = compute_macd(close)
    ma50 = compute_ma(close, 50)
    ma200 = compute_ma(close, 200)

    latest = df.iloc[-1]
    latest_rsi = float(rsi_series.iloc[-1])
    latest_macd = float(macd_frame["macd"].iloc[-1])
    latest_signal = float(macd_frame["signal"].iloc[-1])
    latest_ma50 = float(ma50.iloc[-1])
    latest_ma200 = float(ma200.iloc[-1])

    try:
        pred_price, pct_change, model_meta = predict_next_price(close)
    except Exception as e:  # pragma: no cover - safety net
        pred_price, pct_change, model_meta = float(latest["close"]), 0.0, {"fallback": True, "reason": str(e)}

    score = 0
    if latest_rsi < 30:
        score += 1
    if latest_rsi > 70:
        score -= 1

    if latest_macd > latest_signal:
        score += 1
    if latest_macd < latest_signal:
        score -= 1

    if latest_ma50 > latest_ma200:
        score += 1
    if latest_ma50 < latest_ma200:
        score -= 1

    base_signal = "HOLD"
    if score >= 2:
        base_signal = "BUY"
    elif score <= -2:
        base_signal = "SELL"

    final_signal = base_signal
    if pct_change >= 0.01 and base_signal != "SELL":
        final_signal = "BUY"
    elif pct_change <= -0.01 and base_signal != "BUY":
        final_signal = "SELL"

    indicators = {
        "rsi": latest_rsi,
        "macd": latest_macd,
        "macd_signal": latest_signal,
        "ma50": latest_ma50,
        "ma200": latest_ma200,
        "latest_close": float(latest["close"]),
    }

    explain_lines = _build_explanation_lines(final_signal, indicators, pct_change)

    return SignalResult(
        coin=coin_id,
        signal=final_signal,
        predicted_price=pred_price,
        predicted_change_pct=pct_change,
        indicators=indicators,
        explanation=explain_lines,
        model_meta=model_meta,
        fallback=model_meta.get("fallback", False),
    )


def _fallback_result(coin_id: str, reason: str) -> SignalResult:
    return SignalResult(
        coin=coin_id,
        signal="HOLD",
        predicted_price=0.0,
        predicted_change_pct=0.0,
        indicators={"rsi": 50.0, "macd": 0.0, "macd_signal": 0.0, "ma50": 0.0, "ma200": 0.0, "latest_close": 0.0},
        explanation=[f"Data harga tidak tersedia ({reason}) -> fallback HOLD."],
        model_meta={"fallback": True, "reason": reason},
        fallback=True,
    )


def _build_explanation_lines(signal: str, indicators: Dict[str, float], pct_change: float) -> List[str]:
    pct_txt = f"{pct_change*100:.2f}%"
    rsi = indicators["rsi"]
    macd_rel = indicators["macd"] - indicators["macd_signal"]
    trend = "bullish" if indicators["ma50"] > indicators["ma200"] else "bearish"
    lines = [
        f"RSI {rsi:.1f} -> momentum {'oversold' if rsi < 30 else 'overbought' if rsi > 70 else 'netral'}.",
        f"MACD spread {macd_rel:.4f} -> {'positif' if macd_rel > 0 else 'negatif'} dibanding sinyal.",
        f"MA50 vs MA200 menunjukkan tren {trend}.",
        f"Model LSTM memperkirakan perubahan {pct_txt}.",
        f"Rekomendasi akhir: {signal}.",
    ]
    return lines
