import unittest
import os
from unittest.mock import MagicMock, patch
from app.services.pdf import extractor, chunker
from app.services.rag.ingest_pipeline import IngestPipeline
from app.services.vectordb.chroma import HybridVectorStore

class TestIngestion(unittest.TestCase):
    def setUp(self):
        # Create a mock vector store path for testing
        self.test_db_path = "chroma_db/test_store.pkl"
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)
            
        self.vector_store = HybridVectorStore(db_path=self.test_db_path)
        
    def tearDown(self):
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)

    def test_chunker_sliding_window(self):
        # Test the chunker handles text appropriately
        mock_pages = [
            {"page_num": 1, "text": "This is page one. It has some text. We want to test chunking."},
            {"page_num": 2, "text": "This is page two. More text is here. Keep adding characters to make it longer."}
        ]
        
        # Set chunk_size to 100 so that generated chunks are not discarded by size filter
        chunks = chunker.chunk_text(mock_pages, chunk_size=100, chunk_overlap=20)
        self.assertTrue(len(chunks) > 0)
        self.assertEqual(chunks[0]["page_number"], 1)
        self.assertIn("text", chunks[0])

    @patch("app.services.embeddings.embedding_service.EmbeddingService.get_embeddings")
    def test_ingestion_pipeline(self, mock_get_embeddings):
        # Mock get_embeddings to return mock embedding vectors based on input length
        mock_get_embeddings.side_effect = lambda texts: [[0.1] * 768 for _ in texts]

        # Instantiate pipeline with test store
        pipeline = IngestPipeline(vector_store=self.vector_store)
        
        # Test PDF filepath (we will point to one of our generated mock PDFs)
        mock_pdf_path = "backend/uploads/Std9/Science_Class_9.pdf"
        
        if not os.path.exists(mock_pdf_path):
            # Create a simple file if it doesn't exist
            os.makedirs(os.path.dirname(mock_pdf_path), exist_ok=True)
            with open(mock_pdf_path, "w") as f:
                f.write("mock")
                
        result = pipeline.ingest_document(mock_pdf_path, "Std9", "Science")
        
        self.assertEqual(result["status"], "success")
        self.assertTrue(len(self.vector_store.chunks) > 0)
        self.assertEqual(self.vector_store.chunks[0]["standard"], "Std9")
        self.assertEqual(self.vector_store.chunks[0]["subject"], "Science")

if __name__ == "__main__":
    unittest.main()
