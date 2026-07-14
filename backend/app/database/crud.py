import json
from sqlalchemy.orm import Session
from app.database import models

# User CRUD
def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def create_user(db: Session, username: str, hashed_password: str):
    db_user = models.User(username=username, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# Session CRUD
def get_session(db: Session, session_id: str):
    return db.query(models.ChatSession).filter(models.ChatSession.id == session_id).first()

def get_sessions_by_user(db: Session, user_id: int):
    return db.query(models.ChatSession).filter(models.ChatSession.user_id == user_id).order_by(models.ChatSession.created_at.desc()).all()

def create_session(db: Session, user_id: int, title: str = "New Conversation"):
    db_session = models.ChatSession(user_id=user_id, title=title)
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return db_session

def update_session_title(db: Session, session_id: str, title: str):
    db_session = get_session(db, session_id)
    if db_session:
        db_session.title = title
        db.commit()
        db.refresh(db_session)
    return db_session

def delete_session(db: Session, session_id: str):
    db_session = get_session(db, session_id)
    if db_session:
        db.delete(db_session)
        db.commit()
        return True
    return False

# Message CRUD
def get_messages_by_session(db: Session, session_id: str):
    return db.query(models.ChatMessage).filter(models.ChatMessage.session_id == session_id).order_by(models.ChatMessage.created_at.asc()).all()

def create_message(db: Session, session_id: str, role: str, content: str, citations: list = None):
    citations_json = json.dumps(citations) if citations else None
    db_message = models.ChatMessage(
        session_id=session_id,
        role=role,
        content=content,
        citations=citations_json
    )
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message

# IngestedDocument CRUD
def get_document(db: Session, doc_id: int):
    return db.query(models.IngestedDocument).filter(models.IngestedDocument.id == doc_id).first()

def get_document_by_name_and_meta(db: Session, filename: str, standard: str, subject: str):
    return db.query(models.IngestedDocument).filter(
        models.IngestedDocument.filename == filename,
        models.IngestedDocument.standard == standard,
        models.IngestedDocument.subject == subject
    ).first()

def create_ingested_document(db: Session, filename: str, filepath: str, standard: str, subject: str):
    db_doc = models.IngestedDocument(
        filename=filename,
        filepath=filepath,
        standard=standard,
        subject=subject
    )
    db.add(db_doc)
    db.commit()
    db.refresh(db_doc)
    return db_doc

def get_ingested_documents(db: Session):
    return db.query(models.IngestedDocument).all()

def delete_ingested_document(db: Session, doc_id: int):
    db_doc = get_document(db, doc_id)
    if db_doc:
        db.delete(db_doc)
        db.commit()
        return True
    return False
