import os
import shutil
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.orm import Session
from app.database import crud, db, models
from app.schemas import upload as upload_schemas
from app.api.auth import get_current_user
from app.services.rag.ingest_pipeline import IngestPipeline
from app.services.vectordb.chroma import HybridVectorStore
from app.core.config import settings

router = APIRouter(prefix="/upload", tags=["upload"])

@router.post("", response_model=upload_schemas.DocumentResponse)
def upload_textbook(
    file: UploadFile = File(...),
    standard: str = Form(...), # e.g. 'Std9', 'Std10', 'Std11', 'Std12'
    subject: str = Form(...),  # e.g. 'Science', 'Maths', 'Physics'
    db_session: Session = Depends(db.get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Uploads a textbook PDF, runs RAG ingestion, and indexes its content."""
    # 1. Validation
    if not file.filename.endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are supported."
        )
        
    valid_standards = ["Std9", "Std10", "Std11", "Std12"]
    if standard not in valid_standards:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid standard. Must be one of: {', '.join(valid_standards)}"
        )

    # Clean filename
    safe_filename = "".join(c for c in file.filename if c.isalnum() or c in (".", "_", "-")).strip()
    
    # Check if document already exists
    existing_doc = crud.get_document_by_name_and_meta(db_session, safe_filename, standard, subject)
    if existing_doc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"A textbook with name '{safe_filename}' already exists for {standard} - {subject}."
        )

    # 2. Save file to standard-specific directory
    dest_dir = os.path.join(settings.UPLOAD_DIR, standard)
    os.makedirs(dest_dir, exist_ok=True)
    dest_path = os.path.join(dest_dir, safe_filename)
    
    try:
        with open(dest_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Could not save file to disk: {str(e)}"
        )

    # 3. Add database record
    db_doc = crud.create_ingested_document(
        db_session, 
        filename=safe_filename, 
        filepath=dest_path, 
        standard=standard, 
        subject=subject
    )

    # 4. Trigger Ingestion Pipeline (chunks & embeddings)
    try:
        pipeline = IngestPipeline()
        result = pipeline.ingest_document(dest_path, standard, subject)
        if result["status"] == "warning_empty":
            # If no content was ingested (e.g. empty or corrupted PDF), raise error
            raise ValueError("No text content could be extracted from this PDF.")
    except Exception as e:
        # Cleanup file and DB record on failure
        if os.path.exists(dest_path):
            os.remove(dest_path)
        crud.delete_ingested_document(db_session, db_doc.id)
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to ingest PDF into vector database: {str(e)}"
        )

    return db_doc

@router.get("/list", response_model=list[upload_schemas.DocumentResponse])
def list_textbooks(
    db_session: Session = Depends(db.get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Lists all uploaded textbooks."""
    return crud.get_ingested_documents(db_session)

@router.delete("/{doc_id}")
def delete_textbook(
    doc_id: int,
    db_session: Session = Depends(db.get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Deletes a textbook, removing its file from disk and purging its index in the vector store."""
    doc = crud.get_document(db_session, doc_id)
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Textbook not found."
        )

    # 1. Delete physical file
    if os.path.exists(doc.filepath):
        try:
            os.remove(doc.filepath)
        except Exception as e:
            # log warning but continue
            pass

    # 2. Delete chunks from vector database
    try:
        vector_store = HybridVectorStore()
        vector_store.delete_document(doc.filename, doc.standard, doc.subject)
    except Exception as e:
        # log warning but continue
        pass

    # 3. Delete DB record
    crud.delete_ingested_document(db_session, doc_id)

    return {"message": f"Successfully deleted textbook: {doc.filename}"}
