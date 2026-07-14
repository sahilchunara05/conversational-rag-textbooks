import datetime
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class Citation(BaseModel):
    source: str
    page: int
    snippet: str

class MessageResponse(BaseModel):
    id: int
    session_id: str
    role: str
    content: str
    citations: Optional[List[Dict[str, Any]]] = None
    created_at: datetime.datetime

    class Config:
        from_attributes = True

class SessionResponse(BaseModel):
    id: str
    title: str
    created_at: datetime.datetime
    user_id: int

    class Config:
        from_attributes = True

class SessionCreate(BaseModel):
    title: Optional[str] = "New Conversation"

class ChatQuery(BaseModel):
    message: str
