import json
import logging
from google import genai
from app.core.config import settings

logger = logging.getLogger(__name__)

class LLMReranker:
    def __init__(self):
        self.client = None
        if settings.is_gemini_configured:
            try:
                self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
            except Exception as e:
                logger.error(f"Failed to initialize GenAI client in LLMReranker: {e}")

    def rerank(self, query: str, chunks: list[dict], top_n: int = 5) -> list[dict]:
        """
        Reranks the chunks using Gemini based on their relevance to the query.
        Returns the top_n most relevant chunks.
        """
        if not chunks:
            return []
        if not self.client or len(chunks) <= 1:
            return chunks[:top_n]

        # Prepare formatted list of chunks for the prompt
        formatted_chunks = ""
        for idx, chunk in enumerate(chunks):
            formatted_chunks += f"--- CHUNK {idx} (Source: {chunk['filename']}, Page: {chunk['page_number']}) ---\n"
            formatted_chunks += f"{chunk['text']}\n\n"

        prompt = f"""
You are a K-12 textbook teaching assistant. Evaluate the relevance of the following textbook chunks to answer the student's question.

Student Question: "{query}"

Retrieved Chunks:
{formatted_chunks}

For each chunk, assign a relevance score between 0 and 10 (10 being extremely helpful and direct, 0 being completely irrelevant).

Return a JSON array of objects. Each object must have:
1. "index": the 0-based chunk index (e.g. 0, 1, 2...) matching the index above.
2. "score": the relevance score (0 to 10).

Format:
[
  {{"index": 0, "score": 8}},
  {{"index": 1, "score": 2}},
  ...
]

Return ONLY the raw JSON array. No markdown blocks, no ```json formatting, no commentary.
"""
        try:
            response = self.client.models.generate_content(
                model=settings.CHAT_MODEL,
                contents=prompt
            )
            text = response.text.strip()
            
            # Remove markdown backticks if any
            if text.startswith("```json"):
                text = text[7:]
            if text.startswith("```"):
                text = text[3:]
            if text.endswith("```"):
                text = text[:-3]
                
            scores_data = json.loads(text.strip())
            
            # Map index to score
            score_map = {item["index"]: item["score"] for item in scores_data}
            
            # Update scores in our chunks
            reranked_chunks = []
            for idx, chunk in enumerate(chunks):
                score = score_map.get(idx, 0)
                chunk_copy = chunk.copy()
                chunk_copy["rerank_score"] = score
                reranked_chunks.append(chunk_copy)
                
            # Sort by rerank score descending
            reranked_chunks.sort(key=lambda x: x.get("rerank_score", 0), reverse=True)
            
            logger.info(f"Reranked {len(chunks)} chunks down to top {top_n}")
            return reranked_chunks[:top_n]
            
        except Exception as e:
            logger.error(f"Error during LLM reranking: {e}. Falling back to default search order.")
            return chunks[:top_n]
