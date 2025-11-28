from typing import Dict, List, Sequence


def generate_signal_bullets(signal: str, indicators: Dict[str, float], pct_change: float, coin_id: str) -> List[str]:
    pct_txt = f"{pct_change*100:.2f}%"
    ma_gap = indicators.get("ma50", 0) - indicators.get("ma200", 0)
    tone = "konservatif" if signal == "HOLD" else "agresif" if abs(pct_change) > 0.02 else "moderat"
    return [
        f"Analisis teknikal untuk {coin_id} condong ke {signal}.",
        f"RSI {indicators.get('rsi', 0):.1f} dan spread MACD {indicators.get('macd', 0)-indicators.get('macd_signal', 0):.4f}.",
        f"Perbandingan MA50-MA200 {'positif' if ma_gap > 0 else 'negatif'} → tren {'menguat' if ma_gap > 0 else 'melemah'}.",
        f"Model LSTM memproyeksikan perubahan {pct_txt} dari harga terakhir.",
        f"Gaya rekomendasi: {tone}, selalu pertimbangkan profil risiko Anda.",
    ]


def craft_chat_answer(question: str, contexts: Sequence[str]) -> str:
    if not contexts:
        return (
            "Berikut jawaban ringkas:\n"
            f"- {question}\n"
            "- Gunakan prinsip diversifikasi, disiplin DCA, dan batasi risiko per posisi."
        )
    joined = "; ".join(ctx.strip() for ctx in contexts if ctx)
    return (
        "Ringkasan (Bahasa Indonesia): "
        + joined
        + f" | Pertanyaan: {question}. "
        "Gunakan informasi ini secara bijak dan sesuaikan dengan profil risiko pribadi."
    )


def summarize_insights(bullets: List[str]) -> List[str]:
    if not bullets:
        return ["Pasar relatif tenang hari ini.", "Tidak ada berita utama yang signifikan."]
    return bullets[:5]
