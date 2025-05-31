import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # AssemblyAI Configuration
    ASSEMBLYAI_API_KEY: str = os.getenv("ASSEMBLYAI_API_KEY", "")
    
    # File Upload Configuration
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "./temp_uploads")
    MAX_FILE_SIZE: int = int(os.getenv("MAX_FILE_SIZE", "1000000000"))  # 1000MB default
    ALLOWED_EXTENSIONS: set = {".mp3", ".mp4", ".mkv", ".wav", ".m4a"}
    
    # CORS Configuration
    CORS_ORIGINS: list = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:3000").split(",")
    
    # API Configuration
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))
    
    # Cleanup Configuration
    CLEANUP_INTERVAL: int = int(os.getenv("CLEANUP_INTERVAL", "3600"))  # 1 hour
    FILE_RETENTION: int = int(os.getenv("FILE_RETENTION", "1800"))  # 30 minutes

settings = Settings()

# Validate required settings
if not settings.ASSEMBLYAI_API_KEY:
    raise ValueError("ASSEMBLYAI_API_KEY environment variable is required")

# Create upload directory if it doesn't exist
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
