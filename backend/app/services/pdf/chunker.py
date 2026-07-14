def chunk_text(pages_data: list[dict], chunk_size: int = 800, chunk_overlap: int = 150) -> list[dict]:
    """
    Splits page texts into overlapping chunks.
    Ensures chunks do not break words where possible.
    """
    chunks = []
    
    for page in pages_data:
        text = page["text"]
        page_num = page["page_num"]
        
        if not text:
            continue
            
        start = 0
        chunk_idx = 0
        text_len = len(text)
        
        while start < text_len:
            # End of current window
            end = start + chunk_size
            
            # If we aren't at the end, find a natural boundary (newline or space)
            if end < text_len:
                # Search backwards in the overlap region
                boundary = -1
                search_start = max(start, end - chunk_overlap)
                
                # Check for paragraph boundary first
                boundary = text.rfind("\n\n", search_start, end)
                if boundary == -1:
                    # Check for sentence boundary
                    boundary = text.rfind(". ", search_start, end)
                    if boundary != -1:
                        boundary += 1 # split after period
                    else:
                        # Check for space boundary
                        boundary = text.rfind(" ", search_start, end)
                        
                if boundary != -1 and boundary > start:
                    end = boundary
            
            chunk_content = text[start:end].strip()
            
            if len(chunk_content) > 30: # ignore very small fragments
                chunks.append({
                    "text": chunk_content,
                    "page_number": page_num,
                    "chunk_idx": chunk_idx
                })
                chunk_idx += 1
                
            # Set next start based on current end minus overlap
            next_start = end - chunk_overlap
            
            # Prevent infinite loops if progress isn't made
            if next_start <= start:
                start = end
            else:
                start = next_start
                
    return chunks
