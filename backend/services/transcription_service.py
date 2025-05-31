import assemblyai as aai
from typing import Optional, Dict, Any
from models import TranscriptionStatus, TranscriptionResult, SubtitleSegment
from config import settings
import asyncio
from concurrent.futures import ThreadPoolExecutor
import time

class TranscriptionService:
    def __init__(self):
        aai.settings.api_key = settings.ASSEMBLYAI_API_KEY
        self.client = aai.Transcriber()
        self.jobs: Dict[str, Dict[str, Any]] = {}
        self.executor = ThreadPoolExecutor(max_workers=4)
    
    async def start_transcription(self, file_path: str, filename: str) -> str:
        """Start transcription job with AssemblyAI"""
        try:
            # Configure transcription settings for highest accuracy using slam-1 model
            config = aai.TranscriptionConfig(
                speech_model=aai.SpeechModel.slam_1,  # Highest accuracy model for English
                # Note: slam-1 is English-only, so language_detection is not compatible
                punctuate=True,
                format_text=True,
                dual_channel=False,
                speaker_labels=False,  # Can be enabled if needed
                auto_highlights=False,
                content_safety=False,
                iab_categories=False,
                custom_spelling=None,
                disfluencies=False,
                sentiment_analysis=False,
                auto_chapters=False,
                entity_detection=False,
                speech_threshold=0.5,
                boost_param="default",
                redact_pii=False,
                redact_pii_audio=False,
                redact_pii_policies=None,
                redact_pii_sub="***",
                webhook_url=None,
                webhook_auth_header_name=None,
                webhook_auth_header_value=None,
            )
            
            # Submit transcription job
            loop = asyncio.get_event_loop()
            transcript = await loop.run_in_executor(
                self.executor,
                lambda: self.client.submit(file_path, config=config)
            )
            
            job_id = transcript.id
            
            # Store job info
            self.jobs[job_id] = {
                "transcript": transcript,
                "filename": filename,
                "file_path": file_path,
                "started_at": time.time(),
                "status": TranscriptionStatus.QUEUED
            }
            
            return job_id
            
        except Exception as e:
            raise Exception(f"Failed to start transcription: {str(e)}")
    
    async def get_subtitle_export(self, job_id: str, format_type: str) -> str:
        """Get subtitle export in specified format using AssemblyAI's export functionality"""
        if job_id not in self.jobs:
            raise Exception("Job not found")

        job_info = self.jobs[job_id]
        transcript = job_info["transcript"]

        try:
            loop = asyncio.get_event_loop()

            if format_type.lower() == 'srt':
                subtitle_content = await loop.run_in_executor(
                    self.executor,
                    lambda: transcript.export_subtitles_srt()
                )
            elif format_type.lower() == 'vtt':
                subtitle_content = await loop.run_in_executor(
                    self.executor,
                    lambda: transcript.export_subtitles_vtt()
                )
            else:
                # For TXT, get the full transcript text
                current_transcript = await loop.run_in_executor(
                    self.executor,
                    lambda: aai.Transcript.get_by_id(transcript.id)
                )
                subtitle_content = current_transcript.text or ""

            return subtitle_content

        except Exception as e:
            raise Exception(f"Error exporting subtitles: {str(e)}")

    async def get_transcription_status(self, job_id: str) -> TranscriptionResult:
        """Get current status of transcription job"""
        if job_id not in self.jobs:
            raise Exception("Job not found")
        
        job_info = self.jobs[job_id]
        transcript = job_info["transcript"]
        
        try:
            # Poll transcript status
            loop = asyncio.get_event_loop()
            current_transcript = await loop.run_in_executor(
                self.executor,
                lambda: aai.Transcript.get_by_id(transcript.id)
            )
            
            # Update job status
            if current_transcript.status == aai.TranscriptStatus.completed:
                job_info["status"] = TranscriptionStatus.COMPLETED
                job_info["completed_at"] = time.time()
                
                # Convert segments to our format
                segments = []
                if current_transcript.words:
                    # Group words into segments (sentences or by time intervals)
                    current_segment = []
                    segment_start = None
                    
                    for word in current_transcript.words:
                        if segment_start is None:
                            segment_start = word.start / 1000.0  # Convert to seconds
                        
                        current_segment.append(word.text)
                        
                        # End segment on sentence boundaries or after 5 seconds
                        if (word.text.endswith(('.', '!', '?')) or 
                            (word.end / 1000.0 - segment_start) > 5.0):
                            
                            segments.append(SubtitleSegment(
                                start=segment_start,
                                end=word.end / 1000.0,
                                text=' '.join(current_segment).strip()
                            ))
                            current_segment = []
                            segment_start = None
                    
                    # Add remaining words as final segment
                    if current_segment and segment_start is not None:
                        last_word = current_transcript.words[-1]
                        segments.append(SubtitleSegment(
                            start=segment_start,
                            end=last_word.end / 1000.0,
                            text=' '.join(current_segment).strip()
                        ))
                
                return TranscriptionResult(
                    job_id=job_id,
                    status=TranscriptionStatus.COMPLETED,
                    text=current_transcript.text,
                    segments=segments,
                    confidence=current_transcript.confidence,
                    audio_duration=current_transcript.audio_duration / 1000.0 if current_transcript.audio_duration else None
                )
                
            elif current_transcript.status == aai.TranscriptStatus.error:
                job_info["status"] = TranscriptionStatus.ERROR
                return TranscriptionResult(
                    job_id=job_id,
                    status=TranscriptionStatus.ERROR,
                    error=current_transcript.error or "Unknown error occurred"
                )
                
            else:
                # Still processing
                job_info["status"] = TranscriptionStatus.PROCESSING
                return TranscriptionResult(
                    job_id=job_id,
                    status=TranscriptionStatus.PROCESSING
                )
                
        except Exception as e:
            job_info["status"] = TranscriptionStatus.ERROR
            return TranscriptionResult(
                job_id=job_id,
                status=TranscriptionStatus.ERROR,
                error=f"Error checking status: {str(e)}"
            )
    
    def cleanup_job(self, job_id: str):
        """Clean up job data"""
        if job_id in self.jobs:
            del self.jobs[job_id]
    
    def get_job_info(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get job information"""
        return self.jobs.get(job_id)

# Global instance
transcription_service = TranscriptionService()
