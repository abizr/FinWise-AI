# FinWise AI

Proyek Final Bootcamp:
**FinWise AI: AI-Powered Personal Investment & Crypto Advisory System**

Struktur:
- Virtual environment setup script (Windows .bat)
- FastAPI backend minimal (`/health`)
- Streamlit UI dengan 3 tab (Crypto Signal, Market Insights, Financial Q&A)
- Struktur folder siap untuk dikembangkan (core modules, data, vectordb)

## Fitur
- `/signal/{coin}`: Hybrid signal BUY/SELL/HOLD; indikator RSI/MACD/MA, prediksi LSTM ringan, bullet explanation.
- `/chat`: RAG chatbot (Chroma + SentenceTransformer) menjawab dalam bahasa Indonesia, opsional tampilkan konteks.
- `/insights`: Ringkasan pasar (crypto/stocks/mix) memakai tool LangChain + berita ringan (fallback statis).
- Streamlit dashboard:
  - Tab **Crypto Signal**: pilih koin, lihat sinyal, grafik harga, detail indikator.
  - Tab **Market Insights**: pilih topik dan hasilkan 3–5 bullet insight.
  - Tab **Financial Q&A**: tanya jawab dengan chatbot berbasis RAG.

## Cara Pakai (Windows)

1. Ekstrak ZIP ini.
2. Buka Command Prompt di folder `finwise_win`.
3. Jalankan:

scripts\setup_env.bat

4. Setelah selesai, aktifkan environment (jika belum):

.venv\Scripts\activate

5. Jalankan API:

scripts\run_api.bat

6. Di Command Prompt lain, jalankan UI:

scripts\run_ui.bat

7. Buka di browser:
- API Docs: http://127.0.0.1:8000/docs
- UI: http://localhost:8501

## Catatan
- `.env.example` berisi placeholder API key. Untuk demo offline sistem akan memakai fallback data.
- Vector store disimpan di folder `vectordb` saat endpoint `/chat` pertama kali dipanggil.

## Demo Video
[klik demo video](https://drive.google.com/drive/folders/1oyU7eAL5vf9aNAvGuFNoelZqtq9eRxR2?usp=drive_link)

## Connect with me
[LinkedIn](https://www.linkedin.com/in/abizar-al-gifari/)
