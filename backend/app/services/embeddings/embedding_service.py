import logging
from typing import List, Union
from google import genai
from google.genai import types
from app.core.config import settings

logger = logging.getLogger(__name__)

class EmbeddingService:
    def __init__(self):
        self.client = None
        if settings.is_gemini_configured:
            try:
                self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
            except Exception as e:
                logger.error(f"Failed to initialize GenAI client: {e}")
        else:
            logger.warning("GEMINI_API_KEY is not configured or is the default placeholder! Embeddings cannot be generated.")

    def get_embedding(self, text: str) -> List[float]:
        """Generates a dense embedding for a single text string."""
        if not self.client:
            raise ValueError("GenAI client is not initialized. Please configure GEMINI_API_KEY.")
            
        try:
            response = self.client.models.embed_content(
                model=settings.EMBEDDING_MODEL,
                contents=text
            )
            return response.embeddings[0].values
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            raise e

    def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generates dense embeddings for a list of text strings with batching."""
        if not self.client:
            raise ValueError("GenAI client is not initialized. Please configure GEMINI_API_KEY.")
            
        if not texts:
            return []
            
        # The embedding API has a batch limit (usually 100 texts per request)
        batch_size = 100
        all_embeddings = []
        
        try:
            for i in range(0, len(texts), batch_size):
                batch_texts = texts[i:i + batch_size]
                logger.info(f"Generating embeddings for batch of size {len(batch_texts)} ({i} to {i + len(batch_texts)})...")
                
                # Wrap each text in a Content object to generate separate embeddings
                contents = [types.Content(parts=[types.Part.from_text(text=t)]) for t in batch_texts]
                
                response = self.client.models.embed_content(
                    model=settings.EMBEDDING_MODEL,
                    contents=contents
                )
                
                batch_embeddings = [emb.values for emb in response.embeddings]
                all_embeddings.extend(batch_embeddings)
                
            return all_embeddings
        except Exception as e:
            logger.error(f"Error generating batch embeddings: {e}")
            raise e
