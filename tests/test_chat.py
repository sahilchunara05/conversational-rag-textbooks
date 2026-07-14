import unittest
import json
from unittest.mock import MagicMock, patch
from app.services.rag.chat_pipeline import ChatPipeline

class TestChatPipeline(unittest.TestCase):

    @patch("app.services.rag.chat_pipeline.QueryRouter")
    @patch("app.services.rag.chat_pipeline.EmbeddingService")
    @patch("app.services.rag.chat_pipeline.HybridVectorStore")
    @patch("app.services.rag.chat_pipeline.LLMReranker")
    @patch("app.services.rag.chat_pipeline.GeminiService")
    def test_chat_pipeline_execution(
        self,
        mock_gemini_service_class,
        mock_reranker_class,
        mock_store_class,
        mock_embed_class,
        mock_router_class
    ):
        # 1. Setup Mocks
        mock_router = MagicMock()
        mock_router.route_query.return_value = (["Std10"], ["Science"])
        mock_router_class.return_value = mock_router
        
        mock_embed = MagicMock()
        mock_embed.get_embedding.return_value = [0.1] * 768
        mock_embed_class.return_value = mock_embed
        
        mock_store = MagicMock()
        mock_chunks = [{"text": "Respiration is exothermic.", "filename": "Sci_10.pdf", "page_number": 3, "subject": "Science", "standard": "Std10"}]
        mock_store.search.return_value = mock_chunks
        mock_store_class.return_value = mock_store
        
        mock_reranker = MagicMock()
        mock_reranker.rerank.return_value = mock_chunks
        mock_reranker_class.return_value = mock_reranker
        
        mock_gemini = MagicMock()
        def mock_stream(*args, **kwargs):
            yield "data: " + json.dumps({"type": "metadata", "citations": []}) + "\n\n"
            yield "data: " + json.dumps({"type": "text", "content": "Respiration is exothermic."}) + "\n\n"
            yield "data: " + json.dumps({"type": "done"}) + "\n\n"
        mock_gemini.generate_rag_stream.side_effect = mock_stream
        mock_gemini_service_class.return_value = mock_gemini

        # 2. Run Chat Pipeline
        pipeline = ChatPipeline(
            vector_store=mock_store,
            embedding_service=mock_embed,
            query_router=mock_router,
            reranker=mock_reranker,
            gemini_service=mock_gemini
        )
        
        generator = pipeline.process_query_stream(
            query="Explain respiration.",
            history=[]
        )
        
        chunks = list(generator)
        self.assertEqual(len(chunks), 3)
        self.assertIn("metadata", chunks[0])
        self.assertIn("Respiration is exothermic.", chunks[1])
        
        # Verify routing was called
        mock_router.route_query.assert_called_once_with("Explain respiration.")
        # Verify search was called with correct parameters
        mock_store.search.assert_called_once()
        # Verify rerank was called
        mock_reranker.rerank.assert_called_once()

if __name__ == "__main__":
    unittest.main()
