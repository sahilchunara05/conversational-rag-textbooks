import json
import logging
from google import genai
from app.core.config import settings

logger = logging.getLogger(__name__)

class QueryRouter:
    def __init__(self):
        self.client = None
        if settings.is_gemini_configured:
            try:
                self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
            except Exception as e:
                logger.error(f"Failed to initialize GenAI client in QueryRouter: {e}")

    def route_query(self, query: str) -> tuple[list[str] | None, list[str] | None]:
        """
        Classifies the query using Gemini to find target standards and subjects.
        Returns: (standards_list, subjects_list) where empty lists represent no filter.
        """
        if not self.client:
            return None, None

        prompt = f"""
You are an AI query router for a K-12 school textbook database. 
Analyze the user's question and determine which specific Standard(s) and Subject(s) are relevant.

Available Standards: Std9, Std10, Std11, Std12
Available Subjects: Science, Physics, Chemistry, Maths, History

User Question: "{query}"

Return a JSON object with exactly two keys:
1. "standards": a list containing zero or more of: "Std9", "Std10", "Std11", "Std12"
2. "subjects": a list of subject names (e.g. "Science", "Physics", "Chemistry", "Maths", "History")

Rule: If the question does not mention a specific standard or subject, or if it is ambiguous, return an empty list for that field.

Return ONLY the raw JSON. No markdown blocks, no ```json wrappers, no extra explanation. Just the JSON object.
"""
        try:
            response = self.client.models.generate_content(
                model=settings.CHAT_MODEL,
                contents=prompt
            )
            text = response.text.strip()
            
            # Remove potential markdown block wrappers if model outputs them anyway
            if text.startswith("```json"):
                text = text[7:]
            if text.startswith("```"):
                text = text[3:]
            if text.endswith("```"):
                text = text[:-3]
                
            data = json.loads(text.strip())
            
            standards = data.get("standards", [])
            subjects = data.get("subjects", [])
            
            logger.info(f"Routed query '{query}' to Standards: {standards}, Subjects: {subjects}")
            
            # Map empty lists to None for our vector search (meaning no filter)
            standards_filter = standards if standards else None
            subjects_filter = subjects if subjects else None
            
            return standards_filter, subjects_filter
            
        except Exception as e:
            logger.error(f"Error routing query via LLM: {e}. Falling back to no filters.")
            return None, None
