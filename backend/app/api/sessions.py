import json
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import crud, db, models
from app.schemas import chat as chat_schemas
from app.api.auth import get_current_user

router = APIRouter(prefix="/sessions", tags=["sessions"])

@router.get("", response_model=list[chat_schemas.SessionResponse])
def get_user_sessions(
    db_session: Session = Depends(db.get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Lists all chat sessions for the logged-in user."""
    return crud.get_sessions_by_user(db_session, current_user.id)

@router.post("", response_model=chat_schemas.SessionResponse)
def create_chat_session(
    session_in: chat_schemas.SessionCreate,
    db_session: Session = Depends(db.get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Creates a new chat session."""
    return crud.create_session(db_session, user_id=current_user.id, title=session_in.title)

@router.get("/{session_id}/messages", response_model=list[chat_schemas.MessageResponse])
def get_session_messages(
    session_id: str,
    db_session: Session = Depends(db.get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Retrieves all messages for a specific session, deserializing citation strings."""
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

    messages = crud.get_messages_by_session(db_session, session_id)
    
    # Map messages to deserialize citations JSON string
    response_messages = []
    for msg in messages:
        citations_list = None
        if msg.citations:
            try:
                citations_list = json.loads(msg.citations)
            except Exception:
                pass
                
        response_messages.append({
            "id": msg.id,
            "session_id": msg.session_id,
            "role": msg.role,
            "content": msg.content,
            "citations": citations_list,
            "created_at": msg.created_at
        })
        
    return response_messages

@router.delete("/{session_id}")
def delete_chat_session(
    session_id: str,
    db_session: Session = Depends(db.get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Deletes a chat session."""
    session = crud.get_session(db_session, session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat session not found."
        )
    if session.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this session."
        )

    crud.delete_session(db_session, session_id)
    return {"message": "Chat session successfully deleted."}
