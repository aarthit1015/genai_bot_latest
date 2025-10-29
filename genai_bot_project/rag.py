# rag.py
import numpy as np
from sentence_transformers import SentenceTransformer
from transformers import pipeline
from typing import List, Tuple
import os
import time
from db import save_doc, load_all_embeddings, cache_get, cache_set, init_db, list_docs
from utils import setup_logger
import warnings
warnings.filterwarnings("ignore", category=FutureWarning)

logger = setup_logger(__name__)

EMBED_MODEL = os.environ.get("EMBED_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
GEN_MODEL = os.environ.get("GEN_MODEL", "google/flan-t5-base")  # small, runs on CPU

class MiniRAG:
    def __init__(self, embed_model_name=EMBED_MODEL, gen_model_name=GEN_MODEL):
        self.embedder = SentenceTransformer(embed_model_name)
        self.generator = pipeline("text2text-generation", model=gen_model_name, truncation=True)
        init_db()
        self.rebuild_index()

    def embed(self, texts: List[str]) -> np.ndarray:
        return self.embedder.encode(texts, convert_to_numpy=True, normalize_embeddings=True).astype(np.float32)

    def add_documents(self, docs: List[Tuple[str,str]]):
        """docs: list of (title, text). Save to DB and index."""
        for title, text in docs:
            emb = self.embed([text])[0]
            save_doc(title, text, emb)
        self.rebuild_index()

    def rebuild_index(self):
        rows = load_all_embeddings()
        if not rows:
            self.ids = []
            self.titles = []
            self.texts = []
            self.embeddings = np.zeros((0, 1), dtype=np.float32)
            return
        self.ids = [r[0] for r in rows]
        self.titles = [r[1] for r in rows]
        self.texts = [r[2] for r in rows]
        embs = [r[3] for r in rows]
        self.embeddings = np.vstack(embs).astype(np.float32)
        logger.info("Index rebuilt: %d docs", len(self.ids))

    def retrieve(self, query: str, k=3):
        """Return top-k (title, text, score)."""
        cached = cache_get(query)
        if cached is not None:
            qvec = cached
        else:
            qvec = self.embed([query])[0]
            cache_set(query, qvec)
        if self.embeddings.shape[0] == 0:
            return []
        # cosine similarity since embeddings are normalized
        scores = np.dot(self.embeddings, qvec)
        idxs = np.argsort(-scores)[:k]
        results = []
        for i in idxs:
            results.append((self.titles[i], self.texts[i], float(scores[i])))
        return results

    def answer(self, query: str, k=3) -> str:
        hits = self.retrieve(query, k=k)
        # build context
        context_parts = []
        for t, text, score in hits:
            context_parts.append(f"Source: {t}\n{text}\n")
        context = "\n---\n".join(context_parts)
        prompt = (
            "You are a helpful assistant. Use the context below to answer the user's question.\n\n"
            f"Context:\n{context}\n\nQuestion: {query}\n\nAnswer concisely, and if the answer is not in the context say so."
        )
        # generator pipeline returns list with 'generated_text'
        out = self.generator(prompt, max_length=256, do_sample=False)[0]["generated_text"]
        # add source snippet (top 1) with score for transparency
        if hits:
            top = hits[0]
            out += f"\n\n(Top source: {top[0]} — score {top[2]:.3f})"
        return out
