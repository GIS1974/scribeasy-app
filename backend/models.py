from pydantic import BaseModel
from typing import Optional, List
from enum import Enum

class TranscriptionStatus(str, Enum):
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    ERROR = "error"

class OutputFormat(str, Enum):
    SRT = "srt"
    VTT = "vtt"
    TXT = "txt"

class UploadResponse(BaseModel):
    job_id: str
    message: str
    filename: str

class TranscriptionStatusResponse(BaseModel):
    job_id: str
    status: TranscriptionStatus
    progress: Optional[float] = None
    error: Optional[str] = None
    completed_at: Optional[str] = None

class SubtitleSegment(BaseModel):
    start: float
    end: float
    text: str
    speaker: Optional[str] = None  # Speaker label (A, B, C, etc.)

class TranscriptionResult(BaseModel):
    job_id: str
    status: TranscriptionStatus
    text: Optional[str] = None
    segments: Optional[List[SubtitleSegment]] = None
    confidence: Optional[float] = None
    audio_duration: Optional[float] = None
    error: Optional[str] = None

class DownloadResponse(BaseModel):
    content: str
    filename: str
    content_type: str

class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None
