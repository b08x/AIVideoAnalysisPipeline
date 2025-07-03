# subtitle_processor/parsers.py
import re
from typing import List
from models import Utterance

def timecode_to_seconds(tc: str) -> float:
    """Converts a timecode string (HH:MM:SS.ms) to seconds."""
    if ',' in tc:
        tc = tc.replace(',', '.')
    parts = tc.split(':')
    if len(parts) == 3:
        h, m, s = parts
        return int(h) * 3600 + int(m) * 60 + float(s)
    elif len(parts) == 2:
        m, s = parts
        return int(m) * 60 + float(s)
    return 0.0

def parse_vtt(content: str) -> List[Utterance]:
    """Parses a VTT subtitle file content."""
    utterances = []
    # Pattern to match VTT cues with optional hours
    pattern = re.compile(r"(\d{2}:)?\d{2}:\d{2}\.\d{3} --> (\d{2}:)?\d{2}:\d{2}\.\d{3}\n(.*?)\n\n", re.DOTALL)
    for match in pattern.finditer(content):
        start_tc, end_tc, text = match.groups()[0:3] # Adjusted to handle optional groups
        start_time = timecode_to_seconds(start_tc if start_tc else "00:" + match.group(0).split(" --> ")[0])
        end_time = timecode_to_seconds(end_tc if end_tc else "00:" + match.group(0).split(" --> ")[1].split("\n")[0])
        
        clean_text = re.sub(r'<.*?>', '', text).strip()
        if clean_text:
            utterances.append(Utterance(start_time=start_time, end_time=end_time, text=clean_text))
    return utterances

def parse_srt(content: str) -> List[Utterance]:
    """Parses an SRT subtitle file content."""
    utterances = []
    # Pattern to match SRT blocks
    pattern = re.compile(r"\d+\n(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})\n(.*?)\n\n", re.DOTALL)
    for start_tc, end_tc, text in pattern.findall(content):
        start_time = timecode_to_seconds(start_tc)
        end_time = timecode_to_seconds(end_tc)
        clean_text = re.sub(r'<.*?>', '', text).strip()
        if clean_text:
            utterances.append(Utterance(start_time=start_time, end_time=end_time, text=clean_text))
    return utterances

def parse_ass(content: str) -> List[Utterance]:
    """Parses an ASS subtitle file content."""
    utterances = []
    # Find the format line to map columns
    format_line = re.search(r"Format: (.*)", content)
    if not format_line:
        return []
    
    columns = [col.strip() for col in format_line.group(1).split(',')]
    try:
        start_idx = columns.index("Start")
        end_idx = columns.index("End")
        text_idx = columns.index("Text")
    except ValueError:
        return [] # Essential columns not found

    # Pattern to match Dialogue lines
    dialogue_pattern = re.compile(r"Dialogue: (.*)")
    for line in dialogue_pattern.findall(content):
        parts = line.split(',', len(columns) - 1)
        if len(parts) == len(columns):
            start_tc = parts[start_idx]
            end_tc = parts[end_idx]
            text = parts[text_idx]
            
            start_time = timecode_to_seconds(start_tc)
            end_time = timecode_to_seconds(end_tc)
            # Remove ASS styling tags like {\\an8}
            clean_text = re.sub(r'\{.*?\}', '', text).strip()
            if clean_text:
                utterances.append(Utterance(start_time=start_time, end_time=end_time, text=clean_text))
    return utterances

def parse_subtitles(file_path: str, content: str) -> List[Utterance]:
    """
    Detects the subtitle format from file extension and parses the content.
    """
    if file_path.endswith(".vtt"):
        return parse_vtt(content)
    elif file_path.endswith(".srt"):
        return parse_srt(content)
    elif file_path.endswith(".ass"):
        return parse_ass(content)
    else:
        raise ValueError(f"Unsupported subtitle format for file: {file_path}")

