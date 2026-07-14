import re

def clean_text(text: str) -> str:
    """Cleans up redundant whitespace and formatting from extracted text."""
    # Replace multiple spaces/newlines with a single space
    cleaned = re.sub(r'\s+', ' ', text)
    return cleaned.strip()
