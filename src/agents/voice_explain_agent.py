"""Voice Explanation Agent (TTS)

Generates a short spoken explanation (audio) for a selected banking term using OpenAI TTS.
It can reuse the existing text explanation from `term_explain_agent`, or generate it first
if not provided.

Outputs audio bytes (MP3 by default) to be played in Streamlit via st.audio.
"""

from __future__ import annotations

from io import BytesIO
from typing import Optional, Tuple
import os
import tempfile
import pathlib

from src.agents.term_explain_agent import explain_term


def text_to_speech_openai(text: str, voice: str = "alloy", audio_format: str = "mp3") -> bytes:
    """Convert text to speech using OpenAI's TTS (gpt-4o-mini-tts).

    Returns raw audio bytes (e.g., MP3). Requires OPENAI_API_KEY in env.
    Uses streaming to a temporary file for maximum compatibility across OpenAI SDK versions.
    """
    if not isinstance(text, str) or not text.strip():
        return b""

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        # Graceful message in audio not possible; return empty bytes and let caller show warning
        return b""

    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)

        # Use streaming response to a temp file; avoids API differences between SDK versions
        suffix = f".{audio_format}" if audio_format else ".mp3"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp_path = tmp.name

        # Some SDK versions support with_streaming_response
        try:
            with client.audio.speech.with_streaming_response.create(
                model="gpt-4o-mini-tts",
                voice=voice,
                input=text,
            ) as response:
                response.stream_to_file(tmp_path)
        except Exception:
            # Fallback to non-streaming create, writing bytes to file
            resp = client.audio.speech.create(
                model="gpt-4o-mini-tts",
                voice=voice,
                input=text,
                format=audio_format,
            )
            # Try various response shapes
            data: bytes
            if hasattr(resp, "read"):
                data = resp.read()
            elif hasattr(resp, "content"):
                data = resp.content  # type: ignore[attr-defined]
            elif isinstance(resp, (bytes, bytearray)):
                data = bytes(resp)
            else:
                # Last-resort: try attribute 'audio' or 'data'
                data = getattr(resp, "audio", b"") or getattr(resp, "data", b"")
            pathlib.Path(tmp_path).write_bytes(data)

        audio_bytes = pathlib.Path(tmp_path).read_bytes()
        try:
            os.unlink(tmp_path)
        except Exception:
            pass
        return audio_bytes
    except Exception:
        return b""


def explain_term_voice(
    term: str,
    summary_text: str,
    education_level: Optional[str],
    product_name: Optional[str],
    product_markdown: Optional[str],
    *,
    voice: str = "alloy",
    audio_format: str = "mp3",
) -> Tuple[str, bytes]:
    """Generate a short text explanation (if needed) and return its TTS audio.

    Returns (text_explanation, audio_bytes).
    """
    # Generate text using the existing term explanation agent
    text = explain_term(
        term=term,
        summary_text=summary_text,
        education_level=education_level,
        product_name=product_name,
        product_markdown=product_markdown,
    )

    audio_bytes = text_to_speech_openai(text, voice=voice, audio_format=audio_format)
    return text, audio_bytes
