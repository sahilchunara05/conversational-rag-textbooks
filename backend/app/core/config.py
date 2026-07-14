import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "Conversational RAG Textbook Board"
    API_V1_STR: str = "/api"
    DATABASE_URL: str = "sqlite:///./sql_app.db"
    
    # JWT security settings
    SECRET_KEY: str = "supersecretjwtkeythatneedstochangeinproduction"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440 # 24 hours
    
    # Gemini configurations
    GEMINI_API_KEY: str = ""
    EMBEDDING_MODEL: str = "gemini-embedding-2"
    CHAT_MODEL: str = "gemini-3.1-flash-lite"
    
    # Folder settings
    UPLOAD_DIR: str = "uploads"
    CHROMA_DB_DIR: str = "chroma_db"

    @property
    def is_gemini_configured(self) -> bool:
        return bool(self.GEMINI_API_KEY and self.GEMINI_API_KEY.strip() and self.GEMINI_API_KEY != "PASTE_YOUR_GEMINI_API_KEY_HERE")
    
    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()

# Make sure upload directories exist
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(settings.CHROMA_DB_DIR, exist_ok=True)
for std in ["Std9", "Std10", "Std11", "Std12"]:
    os.makedirs(os.path.join(settings.UPLOAD_DIR, std), exist_ok=True)
