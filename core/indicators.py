import pandas as pd


def compute_ma(series: pd.Series, window: int = 14) -> pd.Series:
    return series.rolling(window=window, min_periods=1).mean()


def compute_rsi(series: pd.Series, window: int = 14) -> pd.Series:
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(window=window, min_periods=window).mean()
    avg_loss = loss.rolling(window=window, min_periods=window).mean()
    rs = avg_gain / avg_loss.replace(0, float("inf"))
    rsi = 100 - (100 / (1 + rs))
    return rsi.fillna(50)


def compute_macd(series: pd.Series) -> pd.DataFrame:
    ema12 = series.ewm(span=12, adjust=False).mean()
    ema26 = series.ewm(span=26, adjust=False).mean()
    macd = ema12 - ema26
    signal = macd.ewm(span=9, adjust=False).mean()
    hist = macd - signal
    return pd.DataFrame({"macd": macd, "signal": signal, "hist": hist})
