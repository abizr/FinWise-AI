import os
from pathlib import Path
import dotenv
import fastapi
import pydantic 
from typing import Any, Dict, List, Literal

try:  # optional dependency
    from dotenv import load_dotenv
except Exception:  # pragma: no cover - keep app running if python-dotenv missing
    def load_dotenv():
        return None

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from core.agent import generate_market_insights
from core.data import fetch_crypto_ohlc
from core.explain import craft_chat_answer, generate_signal_bullets
from core.rag import query_context
from core.signal import SignalResult, hybrid_signal


load_dotenv()

app = FastAPI(
    title="FinWise AI API",
    version="0.2.0",
    description="Backend API untuk FinWise AI (MVP).",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------- Schemas ----------
class HealthResponse(BaseModel):
    status: str
    message: str


class PricePoint(BaseModel):
    date: str
    close: float


class SignalResponse(BaseModel):
    coin: str
    signal: str
    predicted_price: float
    predicted_change_pct: float
    indicators: Dict[str, float]
    explanation: List[str]
    model_meta: Dict[str, Any] = Field(default_factory=dict)
    fallback: bool = False
    history: List[PricePoint] = Field(default_factory=list)


class ChatRequest(BaseModel):
    question: str = Field(..., min_length=3, description="Pertanyaan finansial dalam bahasa Indonesia/Inggris.")
    top_k: int = Field(3, ge=1, le=5)
    show_context: bool = False


class ChatResponse(BaseModel):
    answer: str
    context: List[str] = Field(default_factory=list)


class InsightResponse(BaseModel):
    topic: Literal["crypto", "stocks", "mix"] = "crypto"
    insights: List[str]
    raw: Dict[str, Any] = Field(default_factory=dict)


# ---------- Routes ----------
@app.get("/health", response_model=HealthResponse)
def health_check():
    return HealthResponse(status="ok", message="FinWise API is running")


@app.get("/signal/{coin_id}", response_model=SignalResponse)
def get_signal(
    coin_id: str,
    days: int = Query(120, ge=30, le=365, description="Rentang hari OHLC yang diambil."),
):
    try:
        df = fetch_crypto_ohlc(coin_id, days=days)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal mengambil data harga: {e}")

    if df is None or df.empty:
        raise HTTPException(status_code=500, detail="Data harga tidak tersedia.")

    try:
        signal_res: SignalResult = hybrid_signal(df, coin_id=coin_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal menghitung sinyal: {e}")

    explanation = generate_signal_bullets(
        signal_res.signal, signal_res.indicators, signal_res.predicted_change_pct, coin_id
    )
    history = [PricePoint(date=str(row["date"])[:10], close=float(row["close"])) for _, row in df.tail(180).iterrows()]

    return SignalResponse(
        coin=signal_res.coin,
        signal=signal_res.signal,
        predicted_price=signal_res.predicted_price,
        predicted_change_pct=signal_res.predicted_change_pct,
        indicators=signal_res.indicators,
        explanation=explanation,
        model_meta=signal_res.model_meta,
        fallback=signal_res.fallback,
        history=history,
    )


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    contexts = query_context(req.question, top_k=req.top_k)
    answer = craft_chat_answer(req.question, contexts if req.show_context else [])
    return ChatResponse(answer=answer, context=contexts if req.show_context else [])


@app.get("/insights", response_model=InsightResponse)
def insights(topic: Literal["crypto", "stocks", "mix"] = "crypto"):
    result = generate_market_insights(topic)
    return InsightResponse(topic=topic, insights=result.bullets, raw=result.raw)
