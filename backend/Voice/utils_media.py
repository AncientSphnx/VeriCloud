# backend/utils_media.py
import os
import tempfile
from typing import Tuple
from moviepy.editor import VideoFileClip

AUDIO_EXT = ".wav"

def is_video(filename: str) -> bool:
    lower = filename.lower()
    return lower.endswith((".mp4", ".mov", ".mkv", ".avi", ".webm"))

def is_audio(filename: str) -> bool:
    lower = filename.lower()
    return lower.endswith((".wav", ".mp3", ".m4a", ".flac", ".ogg"))

def write_upload_to_tmp(data: bytes, suffix: str) -> str:
    f = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    f.write(data)
    f.close()
    return f.name

def ensure_wav_from_any(input_path: str) -> Tuple[str, bool]:
    """
    Returns (wav_path, cleanup_input)
    If input is video -> extract audio to wav.
    If input is audio and not wav -> convert to wav via moviepy.
    If already wav -> returns same path.
    """
    lower = input_path.lower()
    if lower.endswith(".wav"):
        return input_path, False

    if is_video(lower):
        clip = VideoFileClip(input_path)
        out_path = input_path + AUDIO_EXT
        clip.audio.write_audiofile(out_path, verbose=False, logger=None)
        clip.close()
        return out_path, True

    # audio but not wav -> convert via moviepy
    clip = VideoFileClip(input_path) if not is_audio(lower) else None
    if clip:
        out_path = input_path + AUDIO_EXT
        clip.audio.write_audiofile(out_path, verbose=False, logger=None)
        clip.close()
        return out_path, True

    # audio path but not wav — use moviepy AudioFileClip
    from moviepy.audio.io.AudioFileClip import AudioFileClip
    aclip = AudioFileClip(input_path)
    out_path = input_path + AUDIO_EXT
    aclip.write_audiofile(out_path, verbose=False, logger=None)
    aclip.close()
    return out_path, True
