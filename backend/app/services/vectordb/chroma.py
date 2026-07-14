import os
import pickle
import logging
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from app.core.config import settings

logger = logging.getLogger(__name__)

class HybridVectorStore:
    def __init__(self, db_path: str = None):
        self.db_path = db_path or os.path.join(settings.CHROMA_DB_DIR, "vector_store.pkl")
        self.chunks = []      # list of dicts with text and metadata
        self.embeddings = []  # list of floats (embeddings)
        self.vectorizer = None
        self.tfidf_matrix = None
        self.load()

    def load(self):
        """Loads the vector store from the pickle file if it exists."""
        if os.path.exists(self.db_path):
            try:
                with open(self.db_path, "rb") as f:
                    data = pickle.load(f)
                    self.chunks = data.get("chunks", [])
                    self.embeddings = data.get("embeddings", [])
                    
                # Rebuild TF-IDF vectorizer and matrix if we have chunks
                self._rebuild_tfidf()
                logger.info(f"Loaded vector store with {len(self.chunks)} chunks from {self.db_path}")
            except Exception as e:
                logger.error(f"Error loading vector store from {self.db_path}: {e}")
                self.chunks = []
                self.embeddings = []
        else:
            logger.info("No existing vector store found. Initializing empty store.")

    def save(self):
        """Saves the vector store chunks and embeddings to the pickle file."""
        try:
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            with open(self.db_path, "wb") as f:
                pickle.dump({
                    "chunks": self.chunks,
                    "embeddings": self.embeddings
                }, f)
            logger.info(f"Saved vector store with {len(self.chunks)} chunks to {self.db_path}")
        except Exception as e:
            logger.error(f"Error saving vector store: {e}")

    def _rebuild_tfidf(self):
        """Rebuilds the TF-IDF vectorizer and matrix based on current chunks."""
        if not self.chunks:
            self.vectorizer = None
            self.tfidf_matrix = None
            return

        texts = [chunk["text"] for chunk in self.chunks]
        try:
            self.vectorizer = TfidfVectorizer(stop_words='english', lowercase=True)
            self.tfidf_matrix = self.vectorizer.fit_transform(texts)
        except Exception as e:
            logger.error(f"Error building TF-IDF index: {e}")
            self.vectorizer = None
            self.tfidf_matrix = None

    def add_chunks(self, filename: str, standard: str, subject: str, chunks: list[dict], embeddings: list[list[float]]):
        """
        Adds text chunks and their embeddings to the store.
        `chunks` is a list of dicts: [{'text': '...', 'page_number': 1, 'chunk_idx': 0}, ...]
        """
        if len(chunks) != len(embeddings):
            raise ValueError("The number of chunks and embeddings must match.")

        for chunk, emb in zip(chunks, embeddings):
            full_chunk = {
                "text": chunk["text"],
                "page_number": chunk["page_number"],
                "chunk_idx": chunk["chunk_idx"],
                "filename": filename,
                "standard": standard,
                "subject": subject
            }
            self.chunks.append(full_chunk)
            self.embeddings.append(emb)

        self._rebuild_tfidf()
        self.save()

    def delete_document(self, filename: str, standard: str, subject: str):
        """Deletes all chunks associated with a specific document."""
        initial_count = len(self.chunks)
        new_chunks = []
        new_embeddings = []

        for chunk, emb in zip(self.chunks, self.embeddings):
            if chunk["filename"] == filename and chunk["standard"] == standard and chunk["subject"] == subject:
                continue
            new_chunks.append(chunk)
            new_embeddings.append(emb)

        self.chunks = new_chunks
        self.embeddings = new_embeddings
        
        deleted_count = initial_count - len(self.chunks)
        logger.info(f"Deleted {deleted_count} chunks for document: {filename} ({standard}/{subject})")
        
        self._rebuild_tfidf()
        self.save()

    def search(self, query: str, query_embedding: list[float], top_k: int = 10, 
               filter_standards: list[str] = None, filter_subjects: list[str] = None) -> list[dict]:
        """
        Performs hybrid search combining dense semantic similarity and sparse TF-IDF keyword match.
        Applies metadata filters prior to computing scores.
        """
        if not self.chunks:
            return []

        # 1. Apply Metadata Filters
        candidate_indices = []
        for idx, chunk in enumerate(self.chunks):
            if filter_standards and chunk["standard"] not in filter_standards:
                continue
            if filter_subjects and chunk["subject"] not in filter_subjects:
                continue
            candidate_indices.append(idx)

        if not candidate_indices:
            return []

        # 2. Dense Semantic Search
        dense_scores = {}
        if self.embeddings and query_embedding:
            # Gather candidate embeddings
            cand_embs = np.array([self.embeddings[idx] for idx in candidate_indices])
            q_emb = np.array(query_embedding)
            
            # Compute cosine similarities
            dot_product = np.dot(cand_embs, q_emb)
            cand_norms = np.linalg.norm(cand_embs, axis=1)
            q_norm = np.linalg.norm(q_emb)
            
            # Avoid division by zero
            denom = cand_norms * q_norm
            denom[denom == 0] = 1e-9
            cos_sims = dot_product / denom
            
            # Rank dense results
            dense_ranks = np.argsort(cos_sims)[::-1]
            for rank, rank_idx in enumerate(dense_ranks):
                chunk_original_idx = candidate_indices[rank_idx]
                dense_scores[chunk_original_idx] = rank + 1 # 1-based rank

        # 3. Sparse TF-IDF Search
        sparse_scores = {}
        if self.vectorizer and self.tfidf_matrix is not None:
            query_sparse = self.vectorizer.transform([query])
            
            # Extract candidate sparse vectors
            # transform query_sparse and compute similarity
            similarities = (self.tfidf_matrix[candidate_indices] * query_sparse.T).toarray().flatten()
            
            # Rank sparse results
            sparse_ranks = np.argsort(similarities)[::-1]
            for rank, rank_idx in enumerate(sparse_ranks):
                chunk_original_idx = candidate_indices[rank_idx]
                sparse_scores[chunk_original_idx] = rank + 1 # 1-based rank

        # 4. Reciprocal Rank Fusion (RRF)
        # RRF Score(d) = sum_{m in models} 1 / (60 + rank_m(d))
        rrf_scores = []
        for idx in candidate_indices:
            score = 0.0
            if idx in dense_scores:
                score += 1.0 / (60 + dense_scores[idx])
            else:
                score += 1.0 / (60 + 9999) # penalty for not being ranked
                
            if idx in sparse_scores:
                score += 1.0 / (60 + sparse_scores[idx])
            else:
                score += 1.0 / (60 + 9999)
                
            rrf_scores.append((idx, score))

        # Sort by RRF score descending
        rrf_scores.sort(key=lambda x: x[1], reverse=True)
        
        # Format and return the top_k results
        results = []
        for rank_pos, (idx, rrf_score) in enumerate(rrf_scores[:top_k]):
            chunk = self.chunks[idx].copy()
            chunk["score"] = rrf_score
            chunk["rank"] = rank_pos + 1
            results.append(chunk)

        return results
