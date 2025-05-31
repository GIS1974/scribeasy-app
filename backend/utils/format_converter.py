from typing import List
from models import SubtitleSegment, OutputFormat
import re

class FormatConverter:
    @staticmethod
    def to_srt(segments: List[SubtitleSegment]) -> str:
        """Convert segments to SRT format"""
        srt_content = []
        
        for i, segment in enumerate(segments, 1):
            start_time = FormatConverter._seconds_to_srt_time(segment.start)
            end_time = FormatConverter._seconds_to_srt_time(segment.end)
            
            srt_content.append(f"{i}")
            srt_content.append(f"{start_time} --> {end_time}")
            srt_content.append(segment.text)
            srt_content.append("")  # Empty line between segments
        
        return "\n".join(srt_content)
    
    @staticmethod
    def to_vtt(segments: List[SubtitleSegment]) -> str:
        """Convert segments to WebVTT format"""
        vtt_content = ["WEBVTT", ""]
        
        for segment in segments:
            start_time = FormatConverter._seconds_to_vtt_time(segment.start)
            end_time = FormatConverter._seconds_to_vtt_time(segment.end)
            
            vtt_content.append(f"{start_time} --> {end_time}")
            vtt_content.append(segment.text)
            vtt_content.append("")  # Empty line between segments
        
        return "\n".join(vtt_content)
    
    @staticmethod
    def to_txt(text: str, segments: List[SubtitleSegment] = None) -> str:
        """Convert to plain text format"""
        if text:
            # Clean up the text
            cleaned_text = re.sub(r'\s+', ' ', text.strip())
            return cleaned_text
        elif segments:
            # Fallback to segments if no full text available
            return "\n".join(segment.text for segment in segments)
        else:
            return ""
    
    @staticmethod
    def _seconds_to_srt_time(seconds: float) -> str:
        """Convert seconds to SRT time format (HH:MM:SS,mmm)"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        milliseconds = int((seconds % 1) * 1000)
        
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{milliseconds:03d}"
    
    @staticmethod
    def _seconds_to_vtt_time(seconds: float) -> str:
        """Convert seconds to WebVTT time format (HH:MM:SS.mmm)"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        milliseconds = int((seconds % 1) * 1000)
        
        return f"{hours:02d}:{minutes:02d}:{secs:02d}.{milliseconds:03d}"
    
    @staticmethod
    def get_content_type(format_type: OutputFormat) -> str:
        """Get appropriate content type for format"""
        content_types = {
            OutputFormat.SRT: "application/x-subrip",
            OutputFormat.VTT: "text/vtt",
            OutputFormat.TXT: "text/plain"
        }
        return content_types.get(format_type, "text/plain")
    
    @staticmethod
    def get_file_extension(format_type: OutputFormat) -> str:
        """Get file extension for format"""
        extensions = {
            OutputFormat.SRT: ".srt",
            OutputFormat.VTT: ".vtt",
            OutputFormat.TXT: ".txt"
        }
        return extensions.get(format_type, ".txt")

# Global instance
format_converter = FormatConverter()
