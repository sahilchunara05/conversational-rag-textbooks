import datetime
from pydantic import BaseModel

class DocumentResponse(BaseModel):
    id: int
    filename: str
    standard: str
    subject: str
    uploaded_at: datetime.datetime

    class Config:
        from_attributes = True
