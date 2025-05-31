import os
import aiofiles
import uuid
from pathlib import Path
from typing import Optional
from fastapi import UploadFile, HTTPException
from config import settings
import asyncio
import time

class FileService:
    def __init__(self):
        self.upload_dir = Path(settings.UPLOAD_DIR)
        self.upload_dir.mkdir(exist_ok=True)
    
    def validate_file(self, file: UploadFile) -> bool:
        """Validate uploaded file type and size"""
        if not file.filename:
            raise HTTPException(status_code=400, detail="No filename provided")
        
        # Check file extension
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in settings.ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported file type. Allowed: {', '.join(settings.ALLOWED_EXTENSIONS)}"
            )
        
        return True
    
    async def save_upload_file(self, file: UploadFile) -> str:
        """Save uploaded file temporarily and return file path"""
        self.validate_file(file)
        
        # Generate unique filename
        file_id = str(uuid.uuid4())
        file_ext = Path(file.filename).suffix.lower()
        temp_filename = f"{file_id}{file_ext}"
        file_path = self.upload_dir / temp_filename
        
        # Check file size while reading
        total_size = 0
        async with aiofiles.open(file_path, 'wb') as f:
            while chunk := await file.read(8192):  # Read in 8KB chunks
                total_size += len(chunk)
                if total_size > settings.MAX_FILE_SIZE:
                    # Clean up partial file
                    await f.close()
                    if file_path.exists():
                        file_path.unlink()
                    raise HTTPException(
                        status_code=413, 
                        detail=f"File too large. Maximum size: {settings.MAX_FILE_SIZE / 1024 / 1024:.1f}MB"
                    )
                await f.write(chunk)
        
        return str(file_path)
    
    def delete_file(self, file_path: str) -> bool:
        """Delete a file safely"""
        try:
            path = Path(file_path)
            if path.exists() and path.parent == self.upload_dir:
                path.unlink()
                return True
        except Exception as e:
            print(f"Error deleting file {file_path}: {e}")
        return False
    
    async def cleanup_old_files(self):
        """Clean up files older than retention period"""
        try:
            current_time = time.time()
            for file_path in self.upload_dir.iterdir():
                if file_path.is_file():
                    file_age = current_time - file_path.stat().st_mtime
                    if file_age > settings.FILE_RETENTION:
                        try:
                            file_path.unlink()
                            print(f"Cleaned up old file: {file_path}")
                        except Exception as e:
                            print(f"Error cleaning up file {file_path}: {e}")
        except Exception as e:
            print(f"Error during cleanup: {e}")
    
    def get_file_info(self, file_path: str) -> Optional[dict]:
        """Get file information"""
        try:
            path = Path(file_path)
            if path.exists():
                stat = path.stat()
                return {
                    "size": stat.st_size,
                    "created": stat.st_ctime,
                    "modified": stat.st_mtime,
                    "name": path.name
                }
        except Exception:
            pass
        return None

# Global instance
file_service = FileService()
