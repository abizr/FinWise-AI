import os
from typing import Any, Dict, Optional

import pandas as pd
import plotly.express as px
import requests
import streamlit as st

# ---------- Page Config ----------
st.set_page_config(
    page_title="FinWise AI",
    page_icon="💹",  # simple finance icon
    layout="wide",
)

# ---------- Logo Path ----------
BASE_DIR = os.path.dirname(__file__)
ASSETS_DIR = os.path.join(BASE_DIR, "assets")

LOGO_PATH = os.path.join(ASSETS_DIR, "finwise_logo.png")
if not os.path.exists(LOGO_PATH):
    LOGO_PATH = os.path.join(ASSETS_DIR, "finwise_primary.png")
if not os.path.exists(LOGO_PATH):
    LOGO_PATH = os.path.join(ASSETS_DIR, "finwise_primary.jpg")

# ---------- Global Styling ----------
st.markdown(
    """
<style>
:root {
    --bg: #050816;
    --panel: #0b1220;
    --panel-2: #0f172a;
    --text: #e5e7eb;
    --muted: #9ca3af;
    --accent: #06b6d4;
    --accent-2: #22d3ee;
}
html, body, .main, [class*="block-container"] {
    background: radial-gradient(90% 130% at 0% 0%, #111827 0%, #020617 40%, #020617 100%) !important;
    color: var(--text);
    font-family: "Segoe UI", "Inter", system-ui, -apple-system, sans-serif;
}
.stButton>button, .stDownloadButton>button {
    background: linear-gradient(90deg, var(--accent) 0%, var(--accent-2) 100%);
    color: #020617; 
    border: none; 
    border-radius: 10px; 
    padding: 0.6rem 1rem; 
    font-weight: 600;
}
.stButton>button:hover {
    filter: brightness(1.05);
}
.metric-card {
    background: var(--panel); 
    padding: 12px 16px; 
    border-radius: 14px;
    border: 1px solid rgba(148,163,184,0.25); 
    box-shadow: 0 16px 40px rgba(15,23,42,0.7);
}
.metric-card-label {
    font-size: 13px;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: var(--muted);
    margin-bottom: 4px;
}
.panel {
    background: var(--panel-2); 
    padding: 16px 18px; 
    border-radius: 14px;
    border: 1px solid rgba(148,163,184,0.35);
}
.panel p, .panel li {
    line-height: 1.5;
}
.footer {
    margin-top: 28px; 
    padding: 14px 0; 
    text-align: center;
    color: var(--muted); 
    font-size: 13px;
}
a.footer-link { 
    color: var(--accent-2); 
    text-decoration: none; 
}
a.footer-link:hover { 
    text-decoration: underline; 
}
</style>
""",
    unsafe_allow_html=True,
)

# ---------- API Base (default + session) ----------
default_api_base = (
    f"http://{os.getenv('API_HOST', '127.0.0.1')}:{os.getenv('API_PORT', '8000')}"
)
if "api_base" not in st.session_state:
    st.session_state["api_base"] = default_api_base


def get_api_base() -> str:
    return st.session_state.get("api_base", default_api_base)


# ---------- API Helpers ----------
def api_get(path: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    base = get_api_base()
    resp = requests.get(f"{base}{path}", params=params, timeout=20)
    resp.raise_for_status()
    return resp.json()


def api_post(path: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    base = get_api_base()
    resp = requests.post(f"{base}{path}", json=payload, timeout=20)
    resp.raise_for_status()
    return resp.json()


# ---------- Header ----------
def render_header() -> None:
    left, right = st.columns([1, 3])
    with left:
        if os.path.exists(LOGO_PATH):
            st.image(LOGO_PATH, width=140)
        else:
            st.markdown("### 💹")
    with right:
        st.markdown(
            """
            <div style="padding: 4px 0 4px 0;">
                <div style="font-size: 30px; font-weight: 700;">
                    Fin <span style="color:#22d3ee;">Wise</span> AI
                </div>
                <div style="color: var(--muted); font-size: 14px; margin-top: 2px;">
                    AI • CRYPTO • INSIGHTS
                </div>
                <div style="color: var(--text); font-size: 13px; margin-top: 6px; max-width: 560px;">
                    AI-powered crypto signals, market insights, and financial Q&A —
                    designed to be clear, explainable, and friendly for retail investors.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


# ---------- Tabs ----------
def render_signal_tab() -> None:
    st.subheader("Crypto Smart Signal (Hybrid)", divider="gray")

    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        coin = st.selectbox(
            "Pilih Coin",
            ["bitcoin", "ethereum", "solana", "dogecoin"],
            index=0,
        )
    with col2:
        days = st.slider(
            "Rentang data (hari)",
            min_value=30,
            max_value=180,
            value=120,
            step=10,
        )
    with col3:
        st.write("")
        st.write("")
        run = st.button("Dapatkan Signal", use_container_width=True)

    if not run:
        st.info("Pilih koin lalu klik tombol untuk menghitung sinyal.")
        return

    try:
        with st.spinner("Mengambil data dan menghitung sinyal..."):
            data = api_get(f"/signal/{coin}", params={"days": days})
    except Exception as e:
        st.error(f"Gagal mengambil sinyal: {e}")
        return

    # Metrics
    metric_col1, metric_col2, metric_col3 = st.columns(3)
    with metric_col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown('<div class="metric-card-label">Signal</div>', unsafe_allow_html=True)
        st.metric(label="", value=data.get("signal", "-"))
        st.markdown("</div>", unsafe_allow_html=True)

    with metric_col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown(
            '<div class="metric-card-label">Prediksi %</div>',
            unsafe_allow_html=True,
        )
        pct = data.get("predicted_change_pct", 0.0) * 100
        st.metric(label="", value=f"{pct:.2f}%")
        st.markdown("</div>", unsafe_allow_html=True)

    with metric_col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown(
            '<div class="metric-card-label">Harga Terakhir</div>',
            unsafe_allow_html=True,
        )
        last_close = data.get("indicators", {}).get("latest_close", 0)
        try:
            last_close_val = float(last_close)
            price_str = f"${last_close_val:,.2f}"
        except Exception:
            price_str = str(last_close)
        st.metric(label="", value=price_str)
        st.markdown("</div>", unsafe_allow_html=True)

    # Explanation
    st.markdown("**Penjelasan**")
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    explanation = data.get("explanation") or []
    if isinstance(explanation, list):
        for line in explanation:
            st.write(f"- {line}")
    else:
        st.write(explanation)
    st.markdown("</div>", unsafe_allow_html=True)

    # Price history chart
    history = data.get("history", [])
    if history:
        df_hist = pd.DataFrame(history)
        if not df_hist.empty and "date" in df_hist.columns and "close" in df_hist.columns:
            fig = px.line(
                df_hist,
                x="date",
                y="close",
                title=f"Riwayat Harga {coin.upper()}",
                markers=True,
                template="plotly_dark",
            )
            fig.update_layout(
                margin=dict(l=10, r=10, t=40, b=10),
                xaxis_title="Date",
                yaxis_title="Price (USD)",
            )
            st.plotly_chart(fig, use_container_width=True)

    # Details
    with st.expander("Detail indikator & model"):
        st.json(data.get("indicators", {}))
        st.json(
            {
                "model_meta": data.get("model_meta", {}),
                "fallback": data.get("fallback", False),
            }
        )


def render_insight_tab() -> None:
    st.subheader("Market Insights (Agentic)", divider="gray")
    topic = st.radio("Topik", ["crypto", "stocks", "mix"], horizontal=True, index=0)

    if st.button("Generate Insight", use_container_width=True):
        try:
            with st.spinner("Menyusun insight pasar..."):
                resp = api_get("/insights", params={"topic": topic})

            st.markdown('<div class="panel">', unsafe_allow_html=True)
            insights = resp.get("insights", [])
            if not insights:
                st.write("Tidak ada insight yang tersedia.")
            else:
                for bullet in insights:
                    st.write(f"- {bullet}")
            st.markdown("</div>", unsafe_allow_html=True)

            with st.expander("Data mentah"):
                st.json(resp.get("raw", {}))
        except Exception as e:
            st.error(f"Gagal membuat insight: {e}")
    else:
        st.info("Pilih topik dan tekan tombol untuk membuat ringkasan pasar.")


def render_chat_tab() -> None:
    st.subheader("Financial Q&A (RAG Chatbot)", divider="gray")

    question = st.text_area(
        "Tulis pertanyaan finansial/crypto Anda",
        height=140,
        placeholder="Contoh: Apa itu DCA? atau Apakah BTC saat ini overbought?",
    )
    col1, col2 = st.columns([1, 1])
    with col1:
        top_k = st.slider("Jumlah konteks", 1, 5, 3, step=1)
    with col2:
        show_ctx = st.checkbox("Tampilkan konteks yang dipakai")

    if st.button("Tanyakan", use_container_width=True):
        if not question.strip():
            st.warning("Pertanyaan tidak boleh kosong.")
            return

        try:
            with st.spinner("Menjawab dengan RAG..."):
                payload = {
                    "question": question,
                    "top_k": top_k,
                    "show_context": show_ctx,
                }
                resp = api_post("/chat", payload)

            st.markdown("**Jawaban**")
            st.markdown('<div class="panel">', unsafe_allow_html=True)
            st.write(resp.get("answer", ""))
            st.markdown("</div>", unsafe_allow_html=True)

            if show_ctx and resp.get("context"):
                st.markdown("**Konteks yang digunakan**")
                ctx_list = resp["context"]
                if isinstance(ctx_list, list):
                    for ctx in ctx_list:
                        st.write(f"- {ctx}")
        except Exception as e:
            st.error(f"Gagal mendapatkan jawaban: {e}")
    else:
        st.info("Masukkan pertanyaan kemudian klik tombol Tanyakan.")


def render_footer() -> None:
    st.markdown(
        """
        <div class="footer">
            Developed by Abizar Al Gifari Rahman 😎 —
            <a class="footer-link" href="https://www.linkedin.com/in/abizar-al-gifari" target="_blank">
                LinkedIn
            </a>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ---------- API Connection Section (pengganti sidebar) ----------
def render_api_connection() -> None:
    with st.expander("⚙️ API Connection (Optional)", expanded=False):
        st.write(
            "Base URL digunakan untuk menghubungkan UI dengan backend FastAPI "
            "(misal: `http://127.0.0.1:8000`)."
        )
        api_input = st.text_input(
            "API Base URL",
            value=get_api_base(),
            help="Ubah ini jika backend FastAPI berjalan di host/port lain.",
        )
        st.session_state["api_base"] = api_input

        col1, col2 = st.columns([1, 2])
        with col1:
            check = st.button("Cek Koneksi API")
        with col2:
            st.caption("Gunakan tombol ini saat demo untuk menunjukkan health-check backend.")

        if check:
            try:
                health = api_get("/health")
                st.success(f"API OK: {health.get('status')} — {health.get('message', '')}")
            except Exception as e:
                st.error(f"Health check gagal: {e}")


# ---------- Main Layout ----------
render_header()
render_api_connection()

tab1, tab2, tab3 = st.tabs(["Crypto Signal", "Market Insights", "Financial Q&A"])

with tab1:
    render_signal_tab()
with tab2:
    render_insight_tab()
with tab3:
    render_chat_tab()

render_footer()
