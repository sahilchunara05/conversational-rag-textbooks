import json
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.database import crud, db, models
from app.schemas import chat as chat_schemas
from app.api.auth import get_current_user
from app.services.rag.chat_pipeline import ChatPipeline

router = APIRouter(prefix="/chat", tags=["chat"])

@router.post("/sessions/{session_id}/query")
def send_chat_query(
    session_id: str,
    query_in: chat_schemas.ChatQuery,
    standards: list[str] = Query(None, alias="standard"), # optional filters from UI
    subjects: list[str] = Query(None, alias="subject"),   # optional filters from UI
    db_session: Session = Depends(db.get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Sends a query to the textbook RAG chatbot for a given session.
    Returns a Server-Sent Events (SSE) streaming response.
    """
    # 1. Verify session ownership
    session = crud.get_session(db_session, session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat session not found."
        )
    if session.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this session."
        )

    # 2. Get past message history (limit to last 10 messages for context)
    past_messages = crud.get_messages_by_session(db_session, session_id)
    history_list = []
    # Take last 10 messages
    for msg in past_messages[-10:]:
        history_list.append({
            "role": msg.role,
            "content": msg.content
        })

    # 3. Save User message to database immediately
    crud.create_message(
        db_session, 
        session_id=session_id, 
        role="user", 
        content=query_in.message
    )

    # 4. Stream response generator
    def sse_generator():
        pipeline = ChatPipeline()
        full_assistant_content = ""
        citation_metadata = []
        
        try:
            # Stream the generator chunks
            stream = pipeline.process_query_stream(
                query=query_in.message,
                history=history_list,
                explicit_standards=standards,
                explicit_subjects=subjects
            )
            
            for chunk_str in stream:
                yield chunk_str
                
                # Extract content for database persistence
                if chunk_str.startswith("data: "):
                    try:
                        data_json = chunk_str[6:].strip()
                        data = json.loads(data_json)
                        if data["type"] == "metadata":
                            citation_metadata = data["citations"]
                        elif data["type"] == "text":
                            full_assistant_content += data["content"]
                    except Exception:
                        pass
                        
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'content': f'Internal pipeline error: {str(e)}'})}\n\n"
        finally:
            # Save Assistant response to database once stream completes
            if full_assistant_content:
                # Update session title if it was the default title
                if session.title == "New Conversation":
                    # Title based on first 5 words of user query
                    title_words = query_in.message.split()[:5]
                    new_title = " ".join(title_words) + ("..." if len(query_in.message.split()) > 5 else "")
                    crud.update_session_title(db_session, session_id, new_title)
                    
                crud.create_message(
                    db_session,
                    session_id=session_id,
                    role="assistant",
                    content=full_assistant_content,
                    citations=citation_metadata
                )

    return StreamingResponse(sse_generator(), media_type="text/event-stream")
