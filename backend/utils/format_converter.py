from typing import List
from models import SubtitleSegment, OutputFormat
import re

class FormatConverter:
    @staticmethod
    def to_srt(segments: List[SubtitleSegment]) -> str:
        """Convert segments to SRT format with speaker labels"""
        srt_content = []

        for i, segment in enumerate(segments, 1):
            start_time = FormatConverter._seconds_to_srt_time(segment.start)
            end_time = FormatConverter._seconds_to_srt_time(segment.end)

            # Format text with speaker label if available
            text = segment.text
            if segment.speaker:
                text = f"[{segment.speaker}] {text}"

            srt_content.append(f"{i}")
            srt_content.append(f"{start_time} --> {end_time}")
            srt_content.append(text)
            srt_content.append("")  # Empty line between segments

        return "\n".join(srt_content)
    
    @staticmethod
    def to_vtt(segments: List[SubtitleSegment]) -> str:
        """Convert segments to WebVTT format with speaker labels"""
        vtt_content = ["WEBVTT", ""]

        for segment in segments:
            start_time = FormatConverter._seconds_to_vtt_time(segment.start)
            end_time = FormatConverter._seconds_to_vtt_time(segment.end)

            # Format text with speaker label if available
            text = segment.text
            if segment.speaker:
                text = f"<v {segment.speaker}>{text}"

            vtt_content.append(f"{start_time} --> {end_time}")
            vtt_content.append(text)
            vtt_content.append("")  # Empty line between segments

        return "\n".join(vtt_content)
    
    @staticmethod
    def to_txt(text: str, segments: List[SubtitleSegment] = None) -> str:
        """Convert to plain text format with speaker labels"""
        if text:
            # Clean up the text
            cleaned_text = re.sub(r'\s+', ' ', text.strip())
            return cleaned_text
        elif segments:
            # Fallback to segments if no full text available, include speaker labels
            lines = []
            for segment in segments:
                if segment.speaker:
                    lines.append(f"[{segment.speaker}] {segment.text}")
                else:
                    lines.append(segment.text)
            return "\n".join(lines)
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
