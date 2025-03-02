import gc
from typing import Any

import jiwer
import numpy as np
import torch
import whisperx
from backend.src.vaait.settings import app


def transcribe_with_whisperx(audio_file: str, model_size: str = "large-v3") -> dict[str, Any]:
    device = app.DEVICE
    batch_size = 16
    compute_type = "int8"

    model = whisperx.load_model(model_size, device=device, language="en", compute_type=compute_type)

    audio = whisperx.load_audio(audio_file)
    result = model.transcribe(audio_file, batch_size=batch_size)

    model_a, metadata = whisperx.load_align_model(language_code=result["language"], device=device)
    aligned_segments = whisperx.align(
        result["segments"],
        model_a,
        metadata,
        audio,
        device,
        return_char_alignments=False,
    )

    return aligned_segments, audio


def diarize_with_whisperx(segments: list, audio: np.ndarray) -> dict[str, Any]:
    torch.cuda.empty_cache()
    diarize_model = whisperx.DiarizationPipeline(use_auth_token=app.HF_TOKEN, device=app.DEVICE)

    diarize_segments = diarize_model(audio, max_speakers=2)

    diarized_transcripts = []
    for segment in whisperx.assign_word_speakers(diarize_segments, segments)["segments"]:
        text = segment["text"]
        speaker = segment.get("speaker", "UNKNOWN")
        diarized_transcripts.append(
            {"start": segment["start"], "end": segment["end"], "text": text, "speaker": speaker},
        )

    torch.cuda.empty_cache()
    del diarize_model
    del diarize_segments
    del segments
    gc.collect()
    return {"transcription": diarized_transcripts}


def calculate_error_rate(hypothesis: str, reference: str) -> float:
    transforms = jiwer.Compose(
        [
            jiwer.ExpandCommonEnglishContractions(),
            jiwer.RemoveEmptyStrings(),
            jiwer.ToLowerCase(),
            jiwer.RemoveMultipleSpaces(),
            jiwer.Strip(),
            jiwer.RemovePunctuation(),
            jiwer.ReduceToListOfListOfWords(),
        ],
    )
    return jiwer.wer(
        hypothesis,
        reference,
        truth_transform=transforms,
        hypothesis_transform=transforms,
    )
