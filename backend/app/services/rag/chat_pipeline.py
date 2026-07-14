import logging
from typing import List, Dict, Any, Generator
from app.services.vectordb.chroma import HybridVectorStore
from app.services.embeddings.embedding_service import EmbeddingService
from app.services.retrieval.query_router import QueryRouter
from app.services.retrieval.reranker import LLMReranker
from app.services.llm.gemini import GeminiService

logger = logging.getLogger(__name__)

class ChatPipeline:
    def __init__(
        self,
        vector_store: HybridVectorStore = None,
        embedding_service: EmbeddingService = None,
        query_router: QueryRouter = None,
        reranker: LLMReranker = None,
        gemini_service: GeminiService = None
    ):
        self.vector_store = vector_store or HybridVectorStore()
        self.embedding_service = embedding_service or EmbeddingService()
        self.query_router = query_router or QueryRouter()
        self.reranker = reranker or LLMReranker()
        self.gemini_service = gemini_service or GeminiService()

    def process_query_stream(
        self, 
        query: str, 
        history: List[Dict[str, str]],
        explicit_standards: List[str] = None,
        explicit_subjects: List[str] = None
    ) -> Generator[str, None, None]:
        """
        Coordinates the entire RAG pipeline:
        Query routing -> Hybrid search -> Reranking -> Prompt formulation -> Streaming.
        """
        logger.info(f"Processing RAG query: '{query}'")

        # 1. Query Routing (Metadata Classification)
        # If user explicitly selected filters in the UI, use them. 
        # Otherwise, fall back to LLM-based query routing.
        standards_filter = explicit_standards
        subjects_filter = explicit_subjects
        
        if not standards_filter and not subjects_filter:
            standards_filter, subjects_filter = self.query_router.route_query(query)
            logger.info(f"Query Router classified filters - Standards: {standards_filter}, Subjects: {subjects_filter}")
        else:
            logger.info(f"Using explicit UI filters - Standards: {standards_filter}, Subjects: {subjects_filter}")

        # 2. Generate Query Embedding
        query_embedding = None
        try:
            if self.embedding_service.client:
                query_embedding = self.embedding_service.get_embedding(query)
        except Exception as e:
            logger.error(f"Failed to generate query embedding: {e}")

        # 3. Hybrid Search in Vector Database (top 15 candidates)
        candidates = self.vector_store.search(
            query=query,
            query_embedding=query_embedding,
            top_k=15,
            filter_standards=standards_filter,
            filter_subjects=subjects_filter
        )
        logger.info(f"Vector store search retrieved {len(candidates)} candidate chunks")

        # 4. Rerank the Candidate Chunks (keep top 5)
        top_chunks = self.reranker.rerank(
            query=query,
            chunks=candidates,
            top_n=5
        )
        logger.info(f"Reranking selected {len(top_chunks)} chunks")

        # 5. Generate Answer Stream with Citations
        return self.gemini_service.generate_rag_stream(
            query=query,
            context_chunks=top_chunks,
            history=history
        )
