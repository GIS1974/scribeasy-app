from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
import asyncio
from pathlib import Path

from config import settings
from models import (
    UploadResponse, TranscriptionStatusResponse, TranscriptionResult, 
    DownloadResponse, ErrorResponse, OutputFormat, TranscriptionStatus
)
from services.file_service import file_service
from services.transcription_service import transcription_service
from utils.format_converter import format_converter

app = FastAPI(
    title="ScribeEasy API",
    description="Audio/Video Transcription API using AssemblyAI",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Background task for cleanup
async def cleanup_files():
    """Background task to clean up old files"""
    while True:
        await file_service.cleanup_old_files()
        await asyncio.sleep(settings.CLEANUP_INTERVAL)

@app.on_event("startup")
async def startup_event():
    """Start background tasks"""
    asyncio.create_task(cleanup_files())

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "ScribeEasy API is running", "version": "1.0.0"}

@app.post("/upload", response_model=UploadResponse)
async def upload_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...)
):
    """Upload file and start transcription"""
    try:
        # Save uploaded file
        file_path = await file_service.save_upload_file(file)
        
        # Start transcription
        job_id = await transcription_service.start_transcription(file_path, file.filename)
        
        # Schedule file cleanup after processing
        background_tasks.add_task(cleanup_after_processing, job_id, file_path)
        
        return UploadResponse(
            job_id=job_id,
            message="File uploaded successfully. Transcription started.",
            filename=file.filename
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@app.get("/status/{job_id}", response_model=TranscriptionResult)
async def get_transcription_status(job_id: str):
    """Get transcription status"""
    try:
        result = await transcription_service.get_transcription_status(job_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.get("/download/{job_id}/{format}")
async def download_transcription(job_id: str, format: OutputFormat):
    """Download transcription in specified format"""
    try:
        # Get transcription result
        result = await transcription_service.get_transcription_status(job_id)
        
        if result.status != TranscriptionStatus.COMPLETED:
            raise HTTPException(
                status_code=400, 
                detail=f"Transcription not completed. Status: {result.status}"
            )
        
        if not result.text and not result.segments:
            raise HTTPException(status_code=404, detail="No transcription data available")
        
        # Convert to requested format
        if format == OutputFormat.SRT:
            if not result.segments:
                raise HTTPException(status_code=400, detail="Segments not available for SRT format")
            content = format_converter.to_srt(result.segments)
        elif format == OutputFormat.VTT:
            if not result.segments:
                raise HTTPException(status_code=400, detail="Segments not available for VTT format")
            content = format_converter.to_vtt(result.segments)
        elif format == OutputFormat.TXT:
            content = format_converter.to_txt(result.text, result.segments)
        else:
            raise HTTPException(status_code=400, detail="Invalid format")
        
        # Get job info for filename
        job_info = transcription_service.get_job_info(job_id)
        original_filename = job_info.get("filename", "transcription") if job_info else "transcription"
        base_filename = Path(original_filename).stem
        
        # Create download filename
        extension = format_converter.get_file_extension(format)
        download_filename = f"{base_filename}_transcription{extension}"
        
        # Return file content
        content_type = format_converter.get_content_type(format)
        
        return Response(
            content=content,
            media_type=content_type,
            headers={
                "Content-Disposition": f"attachment; filename={download_filename}"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Download failed: {str(e)}")

@app.get("/preview/{job_id}")
async def get_preview(job_id: str, lines: int = 10):
    """Get preview of transcription (first few lines)"""
    try:
        result = await transcription_service.get_transcription_status(job_id)
        
        if result.status != TranscriptionStatus.COMPLETED:
            raise HTTPException(
                status_code=400, 
                detail=f"Transcription not completed. Status: {result.status}"
            )
        
        preview_segments = result.segments[:lines] if result.segments else []
        preview_text = result.text[:500] + "..." if result.text and len(result.text) > 500 else result.text
        
        return {
            "job_id": job_id,
            "preview_text": preview_text,
            "preview_segments": preview_segments,
            "total_segments": len(result.segments) if result.segments else 0,
            "audio_duration": result.audio_duration,
            "confidence": result.confidence
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Preview failed: {str(e)}")

async def cleanup_after_processing(job_id: str, file_path: str):
    """Clean up files after transcription is complete or failed"""
    max_wait = 3600  # 1 hour max wait
    check_interval = 30  # Check every 30 seconds
    waited = 0
    
    while waited < max_wait:
        try:
            result = await transcription_service.get_transcription_status(job_id)
            if result.status in [TranscriptionStatus.COMPLETED, TranscriptionStatus.ERROR]:
                # Wait a bit more to allow downloads
                await asyncio.sleep(300)  # 5 minutes
                break
        except:
            break
        
        await asyncio.sleep(check_interval)
        waited += check_interval
    
    # Clean up file and job data
    file_service.delete_file(file_path)
    transcription_service.cleanup_job(job_id)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.API_HOST, port=settings.API_PORT)
