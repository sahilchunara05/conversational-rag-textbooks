import logging
from typing import Generator, List, Dict, Any
from google import genai
from app.core.config import settings

logger = logging.getLogger(__name__)

class GeminiService:
    def __init__(self):
        self.client = None
        if settings.is_gemini_configured:
            try:
                self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
            except Exception as e:
                logger.error(f"Failed to initialize GenAI client in GeminiService: {e}")

    def generate_rag_stream(
        self, 
        query: str, 
        context_chunks: List[Dict[str, Any]], 
        history: List[Dict[str, str]]
    ) -> Generator[str, None, None]:
        """
        Generates a streaming response for RAG.
        Yields strings in SSE format.
        """
        if not self.client:
            yield "data: {\"type\": \"error\", \"content\": \"Gemini API key is not configured.\"}\n\n"
            return

        # 1. Format the context
        context_str = ""
        if context_chunks:
            for idx, chunk in enumerate(context_chunks):
                context_str += f"[{idx + 1}] Textbook: {chunk['filename']} | Page: {chunk['page_number']} | Subject: {chunk['subject']}\n"
                context_str += f"Context: {chunk['text']}\n\n"
        else:
            context_str = "No relevant context found in the textbook database."

        # 2. Format history
        history_str = ""
        for msg in history:
            role = "Student" if msg["role"] == "user" else "Teacher"
            history_str += f"{role}: {msg['content']}\n"

        # 3. Construct System Instructions & prompt
        prompt = f"""
You are a conversational AI tutor answering questions based strictly on the provided school textbooks.

SYSTEM INSTRUCTIONS:
- You must answer the student's question based ONLY on the provided Textbook Context below.
- Cite the source context in your response using bracket numbers corresponding to the context blocks (e.g. [1], [2], or [1][3]).
- Do not use any outside knowledge or general knowledge. If the answer cannot be found in the provided Textbook Context, you must reply EXACTLY with:
  "I am sorry, but the information to answer this question is unavailable in the provided textbook database."
  Do not explain why or add any extra commentary if not found. Just output that exact sentence.
- Maintain a helpful, polite, and educational tone.
- Do not mention 'textbook context' or 'provided sources' directly to the user; speak naturally as if explaining from the textbook.

--- TEXTBOOK CONTEXT ---
{context_str}

--- CONVERSATION HISTORY ---
{history_str}

--- CURRENT STUDENT QUESTION ---
Student: {query}
Teacher:
"""

        try:
            # First, yield the metadata containing citations
            citations = []
            for idx, chunk in enumerate(context_chunks):
                citations.append({
                    "source": chunk["filename"],
                    "page": chunk["page_number"],
                    "subject": chunk["subject"],
                    "standard": chunk["standard"],
                    "snippet": chunk["text"]
                })
                
            import json
            yield f"data: {json.dumps({'type': 'metadata', 'citations': citations})}\n\n"

            # Call the streaming API
            response_stream = self.client.models.generate_content_stream(
                model=settings.CHAT_MODEL,
                contents=prompt
            )
            
            for chunk in response_stream:
                if chunk.text:
                    yield f"data: {json.dumps({'type': 'text', 'content': chunk.text})}\n\n"
                    
            yield "data: {\"type\": \"done\"}\n\n"
            
        except Exception as e:
            logger.error(f"Error during Gemini stream generation: {e}")
            yield f"data: {json.dumps({'type': 'error', 'content': f'Gemini model error: {str(e)}'})}\n\n"
