"""Hindi and Urdu speech to text with local Whisper (faster-whisper). Added by Ahmad Dev.

PeakCut's own speech model (Parakeet) does not know Hindi or Urdu. When a video is set to Hindi or Urdu, this is
used instead. It runs on this machine, free. The model (about 480 MB for "small") downloads once on first use.
PEAKCUT_WHISPER_MODEL picks another size (base: faster, medium / large-v3-turbo: better, slower).
"""
import os
import threading

import numpy as np

_models, _lock = {}, threading.Lock()
PROMPTS = {"hi": "तो, यार, क्या बात है! अरे भाई, चलो।", "ur": "تو، یار، کیا بات ہے! ارے بھائی، چلو۔"}


def _model():
    name = os.environ.get("PEAKCUT_WHISPER_MODEL", "small").strip() or "small"
    with _lock:
        if name not in _models:
            try:
                from faster_whisper import WhisperModel
            except ImportError:
                raise RuntimeError("Hindi/Urdu needs faster-whisper: run  pip install faster-whisper") from None
            _models[name] = WhisperModel(name, device="cpu", compute_type="int8")
        return _models[name]


def transcribe(audio: np.ndarray, lang: str, on_progress=None) -> list:
    """audio: 16 kHz mono. Returns [{'w', 's', 'e'}] like transcribe.transcribe."""
    audio = np.asarray(audio)
    audio = audio.astype(np.float32) / 32768.0 if np.issubdtype(audio.dtype, np.integer) else audio.astype(np.float32)
    total = max(len(audio) / 16000, 1)
    segs, _ = _model().transcribe(audio, language=lang, word_timestamps=True, vad_filter=True,
                                  initial_prompt=PROMPTS.get(lang), condition_on_previous_text=False)
    words = []
    for seg in segs:
        for w in seg.words or []:
            t = w.word.strip()
            if t:
                words.append({"w": t, "s": round(w.start, 2), "e": round(w.end, 2)})
        if on_progress:
            on_progress(min(seg.end / total, 1.0))
    return words
