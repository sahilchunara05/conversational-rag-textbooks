import fitz  # PyMuPDF
import logging
from google import genai
from google.genai import types
from app.core.config import settings

logger = logging.getLogger(__name__)

def extract_pdf_pages(filepath: str) -> list[dict]:
    """
    Extracts text from a PDF file page by page.
    Returns a list of dicts: [{'page_num': 1, 'text': '...'}, ...]
    """
    pages_data = []
    
    try:
        doc = fitz.open(filepath)
    except Exception as e:
        logger.error(f"Error opening PDF file {filepath}: {e}")
        raise ValueError(f"Failed to open PDF file: {e}")
        
    client = None
    if settings.is_gemini_configured:
        try:
            client = genai.Client(api_key=settings.GEMINI_API_KEY)
        except Exception as e:
            logger.warning(f"Failed to initialize GenAI client for OCR fallback: {e}")
            
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        text = page.get_text()
        
        # Determine if we need OCR fallback (e.g. less than 50 characters of text)
        is_scanned = len(text.strip()) < 50
        
        if is_scanned and client:
            logger.info(f"Page {page_num + 1} of {filepath} appears to be scanned. Running Gemini OCR...")
            try:
                # Render page to image
                pix = page.get_pixmap(dpi=150)
                img_bytes = pix.tobytes("png")
                
                # Send to Gemini for transcription
                response = client.models.generate_content(
                    model=settings.CHAT_MODEL,
                    contents=[
                        types.Part.from_bytes(data=img_bytes, mime_type="image/png"),
                        "You are a high-quality OCR transcriber. Transcribe all text in this school textbook page image. "
                        "Preserve the structure, paragraphs, headings, and mathematical equations. "
                        "Output ONLY the transcribed text. Do not add any introduction, headers, footers, or meta text."
                    ]
                )
                if response.text:
                    text = response.text
                    logger.info(f"Gemini OCR success for page {page_num + 1}")
                else:
                    logger.warning(f"Gemini OCR returned empty text for page {page_num + 1}")
            except Exception as e:
                logger.error(f"Error doing OCR for page {page_num + 1}: {e}")
                # Fallback to whatever text was extracted (even if empty)
                
        # page_num in fitz is 0-indexed, let's save as 1-indexed for citation clarity
        pages_data.append({
            "page_num": page_num + 1,
            "text": text.strip()
        })
        
    doc.close()
    return pages_data
