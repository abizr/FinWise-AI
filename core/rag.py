import os
from pathlib import Path
from typing import Dict, List, Sequence

# This module handles RAG with a graceful fallback if chromadb is not installed.
# When chromadb is present, we use a persistent client. Otherwise, we fall back
# to an in-memory keyword scorer to keep the demo running.

try:  # Optional dependency
    import chromadb  # type: ignore
    from chromadb.utils import embedding_functions  # type: ignore
except Exception:  # pragma: no cover - fallback will be used
    chromadb = None
    embedding_functions = None

DEFAULT_DOCS = [
    {
        "id": "doc_dca",
        "text": "Dollar Cost Averaging (DCA) berarti membeli aset secara berkala dengan nominal sama. Strategi ini mengurangi risiko timing pasar dan menumbuhkan disiplin jangka panjang.",
    },
    {
        "id": "doc_risk",
        "text": "Atur porsi investasi sesuai profil risiko. Hindari menempatkan lebih dari 5-10% dana di aset berisiko tinggi seperti altcoin kecil.",
    },
    {
        "id": "doc_rsi",
        "text": "RSI di atas 70 sering dianggap overbought dan di bawah 30 oversold. Gunakan bersama indikator lain untuk konfirmasi sinyal.",
    },
    {
        "id": "doc_news",
        "text": "Perhatikan sentimen berita: katalis positif dapat mempercepat kenaikan, sedangkan isu regulasi dapat meningkatkan volatilitas.",
    },
    {
        "id": "doc_crypto_basics",
        "text": "Bitcoin sering dipandang sebagai 'digital gold', sementara Ethereum mendukung smart contract. Diversifikasi antar kategori kripto dapat menurunkan risiko portofolio.",
    },
]

# In-memory fallback store (used when chromadb is missing)
_FALLBACK_DOCS: List[Dict[str, str]] = DEFAULT_DOCS.copy()


def _using_chroma() -> bool:
    return chromadb is not None and embedding_functions is not None


def _get_client(persist_dir: str = "vectordb"):
    Path(persist_dir).mkdir(parents=True, exist_ok=True)
    return chromadb.PersistentClient(path=persist_dir)  # type: ignore[return-value]


def _get_embedding_function():
    model_name = os.getenv("RAG_EMBED_MODEL", "all-MiniLM-L6-v2")
    return embedding_functions.SentenceTransformerEmbeddingFunction(model_name=model_name)  # type: ignore[attr-defined]


def get_collection(name: str = "finwise_docs", persist_dir: str = "vectordb"):
    if not _using_chroma():
        return None
    client = _get_client(persist_dir)
    emb_fn = _get_embedding_function()
    collection = client.get_or_create_collection(name=name, embedding_function=emb_fn)
    if (collection.count() or 0) == 0:
        collection.add(
            documents=[d["text"] for d in DEFAULT_DOCS],
            ids=[d["id"] for d in DEFAULT_DOCS],
            metadatas=[{"source": "seed"} for _ in DEFAULT_DOCS],
        )
    return collection


def query_context(question: str, top_k: int = 3, persist_dir: str = "vectordb") -> List[str]:
    if _using_chroma():
        col = get_collection(persist_dir=persist_dir)
        res = col.query(query_texts=[question], n_results=top_k)
        docs = res.get("documents") or []
        if not docs:
            return []
        return [doc for doc in docs[0] if doc]

    # Fallback: simple keyword overlap scoring
    q_tokens = set(question.lower().split())
    scored = []
    for doc in _FALLBACK_DOCS:
        score = len(q_tokens.intersection(set(doc["text"].lower().split())))
        scored.append((score, doc["text"]))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [text for _, text in scored[:top_k]]


def ingest_documents(docs: Sequence[Dict[str, str]], persist_dir: str = "vectordb") -> int:
    if _using_chroma():
        col = get_collection(persist_dir=persist_dir)
        ids = [d.get("id") or f"doc_{i}" for i, d in enumerate(docs)]
        texts = [d.get("text", "") for d in docs]
        col.add(documents=texts, ids=ids)
        return len(texts)

    # Fallback in-memory only
    for d in docs:
        _FALLBACK_DOCS.append({"id": d.get("id") or f"doc_{len(_FALLBACK_DOCS)}", "text": d.get("text", "")})
    return len(docs)
