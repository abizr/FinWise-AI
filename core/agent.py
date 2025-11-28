from dataclasses import dataclass
from typing import Callable, Dict, List

from core.data import fetch_news, get_latest_crypto_price, get_stock_price
from core.explain import summarize_insights

try:  # Optional: langchain Tool if installed
    from langchain.tools import Tool  # type: ignore
except Exception:  # pragma: no cover - provide lightweight fallback
    class Tool:  # type: ignore
        def __init__(self, name: str, func: Callable, description: str = ""):
            self.name = name
            self.description = description
            self.func = func

        def run(self, *args, **kwargs):
            return self.func(*args, **kwargs)


@dataclass
class InsightResult:
    topic: str
    bullets: List[str]
    raw: Dict


def _crypto_tool(symbol: str = "bitcoin") -> str:
    price, pct = get_latest_crypto_price(symbol)
    return f"{symbol} ${price:,.2f} ({pct*100:.2f}% 24h)"


def _stock_tool(ticker: str = "^GSPC") -> str:
    price, pct = get_stock_price(ticker)
    return f"{ticker} {price:,.2f} ({pct*100:.2f}%)"


def _news_tool(topic: str = "crypto") -> str:
    items = fetch_news(topic, limit=3)
    return "; ".join(f"{item['title']}" for item in items)


def build_tools():
    return [
        Tool(name="crypto_price", func=_crypto_tool, description="Get latest crypto price % change."),
        Tool(name="stock_price", func=_stock_tool, description="Get latest stock price % change."),
        Tool(name="news", func=_news_tool, description="Get brief news headlines."),
    ]


def generate_market_insights(topic: str = "crypto") -> InsightResult:
    tools = build_tools()
    raw: Dict[str, str] = {}
    bullets: List[str] = []

    if topic in ("crypto", "mix"):
        raw["crypto"] = tools[0].run(topic if topic != "mix" else "bitcoin")
        bullets.append(f"Pasar kripto: {raw['crypto']}.")
    if topic in ("stocks", "mix"):
        raw["stock"] = tools[1].run("^GSPC")
        bullets.append(f"Indeks saham: {raw['stock']}.")

    raw["news"] = tools[2].run(topic)
    bullets.append(f"Berita utama: {raw['news'] or 'stabil'}")

    bullets.append("Risiko: perhatikan volatilitas harian, gunakan posisi kecil untuk aset berisiko.")
    bullets.append("Saran: catat level support/resistance dan gunakan DCA untuk akumulasi.")

    return InsightResult(topic=topic, bullets=summarize_insights(bullets), raw=raw)
