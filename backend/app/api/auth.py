import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.database import crud, db, models
from app.schemas import auth as auth_schemas
from app.core import security
from app.core.config import settings

router = APIRouter(prefix="/auth", tags=["auth"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login-form")

def get_current_user(
    db_session: Session = Depends(db.get_db), 
    token: str = Depends(oauth2_scheme)
) -> models.User:
    """Dependency to retrieve the currently authenticated user from the JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = security.decode_access_token(token)
    if payload is None:
        raise credentials_exception
    username: str = payload.get("sub")
    if username is None:
        raise credentials_exception
        
    user = crud.get_user_by_username(db_session, username)
    if user is None:
        raise credentials_exception
    return user

@router.post("/register", response_model=auth_schemas.UserResponse)
def register(user_in: auth_schemas.UserCreate, db_session: Session = Depends(db.get_db)):
    """Registers a new user."""
    db_user = crud.get_user_by_username(db_session, username=user_in.username)
    if db_user:
        raise HTTPException(
            status_code=400,
            detail="Username already registered"
        )
    hashed_pwd = security.get_password_hash(user_in.password)
    new_user = crud.create_user(db_session, username=user_in.username, hashed_password=hashed_pwd)
    return new_user

@router.post("/login", response_model=auth_schemas.Token)
def login_json(user_in: auth_schemas.UserLogin, db_session: Session = Depends(db.get_db)):
    """Authenticates a user via JSON payload and returns a JWT access token."""
    user = crud.get_user_by_username(db_session, username=user_in.username)
    if not user or not security.verify_password(user_in.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = datetime.timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/login-form", response_model=auth_schemas.Token)
def login_form(form_data: OAuth2PasswordRequestForm = Depends(), db_session: Session = Depends(db.get_db)):
    """Authenticates a user via standard form data (required for OpenAPI UI compatibility)."""
    user = crud.get_user_by_username(db_session, username=form_data.username)
    if not user or not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = datetime.timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=auth_schemas.UserResponse)
def get_me(current_user: models.User = Depends(get_current_user)):
    """Returns the profile of the currently logged-in user."""
    return current_user
