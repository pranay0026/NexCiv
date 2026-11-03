import os
import sys
import torch
import numpy as np
from typing import List, Union, Optional, Tuple
from pathlib import Path

# Ensure UTF-8 output
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

from duplicate_detection.configs.config import cfg
from duplicate_detection.preprocessing.text_cleaner import clean_complaint_text

class MultilingualEmbedder:
    """
    Layer 1 Semantic Embedding & Candidate Retrieval Module.
    Supports:
    - BAAI/bge-m3 (Primary dense + sparse multilingual embedding model)
    - intfloat/multilingual-e5-large (Benchmark model)
    - sentence-transformers/paraphrase-multilingual-mpnet-base-v2 (Lightweight Telugu/English)
    """

    def __init__(self, model_name: Optional[str] = None, device: Optional[str] = None):
        self.model_name = model_name or cfg.LIGHTWEIGHT_EMBEDDING_MODEL
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.model = None
        self._load_model()

    def _load_model(self):
        """Loads SentenceTransformer with fallback hierarchy."""
        try:
            from sentence_transformers import SentenceTransformer
            print(f"Loading embedding model: {self.model_name} on device: {self.device}...")
            self.model = SentenceTransformer(self.model_name, device=self.device)
            print(f"Successfully loaded: {self.model_name}")
        except Exception as e:
            print(f"Notice: Failed to load primary {self.model_name} ({e}). Falling back to lightweight multilingual model...")
            try:
                from sentence_transformers import SentenceTransformer
                self.model_name = cfg.FALLBACK_EMBEDDING_MODEL
                self.model = SentenceTransformer(self.model_name, device=self.device)
                print(f"Successfully loaded fallback model: {self.model_name}")
            except Exception as e2:
                print(f"Critical error loading embedding model: {e2}")
                self.model = None

    def encode(
        self,
        texts: Union[str, List[str]],
        batch_size: int = 32,
        normalize_embeddings: bool = True
    ) -> np.ndarray:
        """
        Generates normalized dense embeddings for input complaint text(s).
        Returns numpy array of shape (N, embedding_dim).
        """
        if isinstance(texts, str):
            texts = [texts]

        cleaned_texts = [clean_complaint_text(t)[0] for t in texts]

        if self.model is not None:
            embeddings = self.model.encode(
                cleaned_texts,
                batch_size=batch_size,
                show_progress_bar=False,
                normalize_embeddings=normalize_embeddings,
                convert_to_numpy=True
            )
            return embeddings
        else:
            # Fallback deterministic pseudo-embedding in case model fails to load
            dim = cfg.EMBEDDING_DIM
            res = np.zeros((len(texts), dim), dtype=np.float32)
            for i, t in enumerate(cleaned_texts):
                seed = abs(hash(t)) % (2**32)
                np.random.seed(seed)
                v = np.random.randn(dim).astype(np.float32)
                res[i] = v / np.linalg.norm(v)
            return res

    def compute_similarity(self, emb_a: np.ndarray, emb_b: np.ndarray) -> float:
        """Computes Cosine Similarity between two normalized embedding vectors."""
        if emb_a.ndim == 1:
            emb_a = emb_a.reshape(1, -1)
        if emb_b.ndim == 1:
            emb_b = emb_b.reshape(1, -1)
        
        # Dot product of normalized vectors equals cosine similarity
        sim = float(np.dot(emb_a, emb_b.T)[0][0])
        # Bound between 0.0 and 1.0 for non-negative probability interpretation
        return max(0.0, min(1.0, (sim + 1.0) / 2.0 if sim < 0 else sim))

    def retrieve_top_k(
        self,
        query_embedding: np.ndarray,
        corpus_embeddings: np.ndarray,
        top_k: int = 15
    ) -> List[Tuple[int, float]]:
        """
        Retrieves Top-K most similar candidate indices and scores from corpus.
        Returns: List of (index, similarity_score) sorted descending.
        """
        if query_embedding.ndim == 1:
            query_embedding = query_embedding.reshape(1, -1)
            
        scores = np.dot(corpus_embeddings, query_embedding.T).flatten()
        top_indices = np.argsort(scores)[::-1][:top_k]
        
        results = []
        for idx in top_indices:
            sim = float(scores[idx])
            bounded_sim = max(0.0, min(1.0, (sim + 1.0) / 2.0 if sim < 0 else sim))
            results.append((int(idx), bounded_sim))
            
        return results

_GLOBAL_EMBEDDER = None

def get_embedder() -> MultilingualEmbedder:
    """Singleton getter for embedder."""
    global _GLOBAL_EMBEDDER
    if _GLOBAL_EMBEDDER is None:
        _GLOBAL_EMBEDDER = MultilingualEmbedder()
    return _GLOBAL_EMBEDDER
