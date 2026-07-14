import unittest
import os
from unittest.mock import MagicMock, patch
from app.services.vectordb.chroma import HybridVectorStore
from app.services.retrieval.query_router import QueryRouter

class TestRetrieval(unittest.TestCase):
    def setUp(self):
        self.test_db_path = "chroma_db/test_retrieval.pkl"
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)
        self.store = HybridVectorStore(db_path=self.test_db_path)
        
        # Seed the store with mock chunks and embeddings
        # We will add 3 chunks:
        # 1. Std9 Science (Cell powerhouse Mitochondria)
        # 2. Std10 Science (Exothermic reaction respiration)
        # 3. Std11 Physics (SI unit Force Newton)
        chunks = [
            {"text": "Mitochondria are the powerhouse of the cell.", "page_number": 2, "chunk_idx": 0},
            {"text": "Respiration is an exothermic reaction.", "page_number": 1, "chunk_idx": 0},
            {"text": "The SI unit of force is the Newton.", "page_number": 1, "chunk_idx": 0}
        ]
        
        # Simple embeddings (3-dimensional for ease)
        embeddings = [
            [1.0, 0.0, 0.0], # Cell / Mitochondria
            [0.0, 1.0, 0.0], # Respiration / Exothermic
            [0.0, 0.0, 1.0]  # Force / Newton
        ]
        
        self.store.add_chunks("mock_doc.pdf", "Std9", "Science", chunks[:1], embeddings[:1])
        self.store.add_chunks("mock_doc2.pdf", "Std10", "Science", chunks[1:2], embeddings[1:2])
        self.store.add_chunks("mock_doc3.pdf", "Std11", "Physics", chunks[2:], embeddings[2:])

    def tearDown(self):
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)

    def test_metadata_filtering(self):
        # Query matching 'Mitochondria' (vector [1,0,0]) but filtered for Std10 Science
        # It should return Chunk 2 (which is in Std10) and NOT Chunk 1 (which is in Std9)
        results = self.store.search(
            query="Mitochondria",
            query_embedding=[1.0, 0.0, 0.0],
            top_k=5,
            filter_standards=["Std10"],
            filter_subjects=["Science"]
        )
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["standard"], "Std10")
        self.assertNotIn("Mitochondria", results[0]["text"])

        # Now query filtered for Std9 Science. It should return Mitochondria!
        results_correct = self.store.search(
            query="Mitochondria",
            query_embedding=[1.0, 0.0, 0.0],
            top_k=5,
            filter_standards=["Std9"],
            filter_subjects=["Science"]
        )
        self.assertEqual(len(results_correct), 1)
        self.assertEqual(results_correct[0]["page_number"], 2)
        self.assertIn("Mitochondria", results_correct[0]["text"])

    def test_hybrid_search(self):
        # Query with TF-IDF keyword overlap but vector is orthogonal
        # It should still retrieve because of TF-IDF keyword match (Hybrid)
        results = self.store.search(
            query="Newton force",
            query_embedding=[0.0, 1.0, 0.0], # vector points to respiration
            top_k=5,
            filter_standards=None,
            filter_subjects=None
        )
        self.assertTrue(len(results) > 0)
        # The Newton force chunk should be ranked high due to keyword matching
        texts = [r["text"] for r in results]
        self.assertTrue(any("Newton" in t for t in texts))

    @patch("app.services.retrieval.query_router.settings")
    @patch("app.services.retrieval.query_router.genai.Client")
    def test_query_router(self, mock_genai_client_class, mock_settings):
        # Test that the LLM query router correctly parses JSON outputs
        mock_settings.GEMINI_API_KEY = "mock_key"
        mock_settings.CHAT_MODEL = "gemini-2.5-flash"
        
        mock_client = MagicMock()
        mock_genai_client_class.return_value = mock_client
        
        mock_response = MagicMock()
        mock_response.text = '{"standards": ["Std10"], "subjects": ["Science"]}'
        mock_client.models.generate_content.return_value = mock_response

        router = QueryRouter()
        standards, subjects = router.route_query("What is exothermic reaction in standard 10?")
        
        self.assertEqual(standards, ["Std10"])
        self.assertEqual(subjects, ["Science"])

if __name__ == "__main__":
    unittest.main()
