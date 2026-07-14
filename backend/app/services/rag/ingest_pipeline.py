import logging
import os
from app.services.pdf import extractor, chunker
from app.services.embeddings.embedding_service import EmbeddingService
from app.services.vectordb.chroma import HybridVectorStore

logger = logging.getLogger(__name__)

class IngestPipeline:
    def __init__(self, vector_store: HybridVectorStore = None, embedding_service: EmbeddingService = None):
        self.vector_store = vector_store or HybridVectorStore()
        self.embedding_service = embedding_service or EmbeddingService()

    def ingest_document(self, filepath: str, standard: str, subject: str) -> dict:
        """
        Runs the full ingestion pipeline for a given PDF file.
        Extracts, chunks, embeds, and saves to the hybrid vector store.
        """
        filename = os.path.basename(filepath)
        logger.info(f"Starting ingestion pipeline for {filename} ({standard}/{subject})...")
        
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"File not found: {filepath}")

        # 1. Extract Pages (text + OCR fallback)
        pages_data = extractor.extract_pdf_pages(filepath)
        total_pages = len(pages_data)
        logger.info(f"Extracted {total_pages} pages from {filename}")

        # 2. Chunk Text
        chunks = chunker.chunk_text(pages_data)
        total_chunks = len(chunks)
        logger.info(f"Generated {total_chunks} chunks from {filename}")

        if total_chunks == 0:
            logger.warning(f"No text extracted or chunks generated for document: {filename}")
            return {
                "filename": filename,
                "pages": total_pages,
                "chunks": 0,
                "status": "warning_empty"
            }

        # 3. Generate Embeddings for Chunks
        chunk_texts = [c["text"] for c in chunks]
        embeddings = self.embedding_service.get_embeddings(chunk_texts)
        logger.info(f"Generated embeddings for {len(embeddings)} chunks")

        # 4. Add to Vector Store
        # Remove any existing chunks for this document first to avoid duplicates
        self.vector_store.delete_document(filename, standard, subject)
        self.vector_store.add_chunks(filename, standard, subject, chunks, embeddings)
        
        logger.info(f"Ingestion successful for {filename}")
        
        return {
            "filename": filename,
            "pages": total_pages,
            "chunks": total_chunks,
            "status": "success"
        }
