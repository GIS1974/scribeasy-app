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
            print(f"DEBUG: Starting transcription for {filename}")
            print(f"DEBUG: File path: {file_path}")
            print(f"DEBUG: API key configured: {bool(settings.ASSEMBLYAI_API_KEY)}")

            # Skip API test and proceed directly to transcription submission
            print("DEBUG: Proceeding with transcription submission...")
            # Configure transcription settings for highest accuracy using slam-1 model
            config = aai.TranscriptionConfig(
                speech_model=aai.SpeechModel.slam_1,  # Highest accuracy model for English
                # Note: slam-1 is English-only, so language_detection is not compatible
                punctuate=True,
                format_text=True,
                dual_channel=False,
                speaker_labels=True,  # Enable speaker diarization for better segmentation
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
            
            # Submit transcription job with timeout
            print(f"DEBUG: Submitting transcription job for file: {file_path}")
            loop = asyncio.get_event_loop()
            try:
                transcript = await asyncio.wait_for(
                    loop.run_in_executor(
                        self.executor,
                        lambda: self.client.submit(file_path, config=config)
                    ),
                    timeout=120.0  # 2 minute timeout for submission
                )
                print(f"DEBUG: Transcription job submitted successfully, ID: {transcript.id}")
            except asyncio.TimeoutError:
                raise Exception("Timeout while submitting transcription job to AssemblyAI")
            except Exception as e:
                print(f"DEBUG: Error submitting transcription job: {str(e)}")
                raise
            
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
        """Get subtitle export in specified format using our improved segmentation"""
        print(f"DEBUG: get_subtitle_export called with job_id={job_id}, format_type={format_type}")

        if job_id not in self.jobs:
            raise Exception("Job not found")

        # Get the transcription result with our improved segments
        result = await self.get_transcription_status(job_id)

        if result.status != TranscriptionStatus.COMPLETED:
            raise Exception(f"Transcription not completed. Status: {result.status}")

        if not result.segments:
            raise Exception("No segments available for export")

        try:
            from utils.format_converter import format_converter

            if format_type.lower() == 'srt':
                print("DEBUG: Exporting SRT using improved segmentation")
                subtitle_content = format_converter.to_srt(result.segments)
            elif format_type.lower() == 'vtt':
                print("DEBUG: Exporting VTT using improved segmentation")
                subtitle_content = format_converter.to_vtt(result.segments)
            else:
                print("DEBUG: Exporting TXT using improved segmentation")
                subtitle_content = format_converter.to_txt(result.text, result.segments)

            print(f"DEBUG: Export successful, content length: {len(subtitle_content)}")
            return subtitle_content

        except Exception as e:
            print(f"DEBUG: Export failed with error: {str(e)}")
            raise Exception(f"Error exporting subtitles: {str(e)}")

    def _create_segments_from_utterances(self, utterances) -> list:
        """Create segments from AssemblyAI utterances with speaker-based segmentation"""
        segments = []

        for utterance in utterances:
            # Convert utterance to segments, splitting on sentence boundaries if needed
            utterance_segments = self._split_utterance_by_sentences(
                text=utterance.text,
                start_time=utterance.start / 1000.0,  # Convert to seconds
                end_time=utterance.end / 1000.0,
                speaker=utterance.speaker,
                words=utterance.words if hasattr(utterance, 'words') else None
            )
            segments.extend(utterance_segments)

        return segments

    def _create_segments_from_words(self, words) -> list:
        """Fallback method to create segments from words when utterances are not available"""
        segments = []
        current_segment = []
        segment_start = None
        current_speaker = None

        for word in words:
            word_speaker = getattr(word, 'speaker', None)

            if segment_start is None:
                segment_start = word.start / 1000.0
                current_speaker = word_speaker

            # Check if we should start a new segment
            should_split = False

            # Split on speaker change
            if word_speaker and current_speaker and word_speaker != current_speaker:
                should_split = True

            # Split on sentence boundaries
            elif word.text.endswith(('.', '!', '?')):
                should_split = True

            # Split if segment is too long (max 5 seconds)
            elif (word.end / 1000.0 - segment_start) > 5.0:
                should_split = True

            current_segment.append(word.text)

            if should_split:
                segments.append(SubtitleSegment(
                    start=segment_start,
                    end=word.end / 1000.0,
                    text=' '.join(current_segment).strip(),
                    speaker=current_speaker
                ))
                current_segment = []
                segment_start = None
                current_speaker = word_speaker

        # Add remaining words as final segment
        if current_segment and segment_start is not None:
            last_word = words[-1]
            segments.append(SubtitleSegment(
                start=segment_start,
                end=last_word.end / 1000.0,
                text=' '.join(current_segment).strip(),
                speaker=current_speaker
            ))

        return segments

    def _split_utterance_by_sentences(self, text: str, start_time: float, end_time: float,
                                     speaker: str, words=None) -> list:
        """Split an utterance into segments based on sentence boundaries"""
        import re

        segments = []

        # If the utterance is short or doesn't contain sentence endings, return as single segment
        if len(text) < 100 or not re.search(r'[.!?]', text):
            return [SubtitleSegment(
                start=start_time,
                end=end_time,
                text=text.strip(),
                speaker=speaker
            )]

        # Split text into sentences while preserving punctuation
        sentence_pattern = r'([.!?]+)'
        parts = re.split(sentence_pattern, text)

        sentences = []
        current_sentence = ""

        for i, part in enumerate(parts):
            if re.match(sentence_pattern, part):
                # This is punctuation, add it to current sentence
                current_sentence += part
                sentences.append(current_sentence.strip())
                current_sentence = ""
            else:
                # This is text
                current_sentence += part

        # Add any remaining text as the last sentence
        if current_sentence.strip():
            sentences.append(current_sentence.strip())

        # Remove empty sentences
        sentences = [s for s in sentences if s.strip()]

        if len(sentences) <= 1:
            # If we only have one sentence, return as single segment
            return [SubtitleSegment(
                start=start_time,
                end=end_time,
                text=text.strip(),
                speaker=speaker
            )]

        # Calculate timing for each sentence based on character count
        total_chars = len(text)
        current_time = start_time
        duration = end_time - start_time

        for i, sentence in enumerate(sentences):
            sentence_chars = len(sentence)
            sentence_duration = (sentence_chars / total_chars) * duration

            # Ensure minimum segment duration of 0.5 seconds
            if sentence_duration < 0.5:
                sentence_duration = 0.5

            segment_end = min(current_time + sentence_duration, end_time)

            # For the last sentence, make sure it ends at the utterance end time
            if i == len(sentences) - 1:
                segment_end = end_time

            segments.append(SubtitleSegment(
                start=current_time,
                end=segment_end,
                text=sentence.strip(),
                speaker=speaker
            ))

            current_time = segment_end

        return segments

    async def get_transcription_status(self, job_id: str) -> TranscriptionResult:
        """Get current status of transcription job"""
        if job_id not in self.jobs:
            raise Exception("Job not found")
        
        job_info = self.jobs[job_id]
        transcript = job_info["transcript"]
        
        try:
            # Poll transcript status with timeout
            loop = asyncio.get_event_loop()
            try:
                current_transcript = await asyncio.wait_for(
                    loop.run_in_executor(
                        self.executor,
                        lambda: aai.Transcript.get_by_id(transcript.id)
                    ),
                    timeout=30.0  # 30 second timeout
                )
            except asyncio.TimeoutError:
                raise Exception("Timeout while checking transcription status")

            # Update job status - check for the correct status enum values
            if current_transcript.status == "completed":
                job_info["status"] = TranscriptionStatus.COMPLETED
                job_info["completed_at"] = time.time()

                # Convert segments to our format using improved segmentation logic
                segments = []

                if current_transcript.utterances:
                    # Use utterances for speaker-based segmentation
                    segments = self._create_segments_from_utterances(current_transcript.utterances)
                elif current_transcript.words:
                    # Fallback to word-based segmentation if no utterances available
                    segments = self._create_segments_from_words(current_transcript.words)

                return TranscriptionResult(
                    job_id=job_id,
                    status=TranscriptionStatus.COMPLETED,
                    text=current_transcript.text,
                    segments=segments,
                    confidence=current_transcript.confidence,
                    audio_duration=current_transcript.audio_duration / 1000.0 if current_transcript.audio_duration else None
                )

            elif current_transcript.status == "error":
                job_info["status"] = TranscriptionStatus.ERROR
                return TranscriptionResult(
                    job_id=job_id,
                    status=TranscriptionStatus.ERROR,
                    error=current_transcript.error or "Unknown error occurred"
                )

            else:
                # Still processing (queued, processing, etc.)
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
