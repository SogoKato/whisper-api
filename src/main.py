import logging
import time
from typing import Annotated

import ffmpeg
import numpy as np
import whisper
from fastapi import FastAPI, Form, UploadFile
from pydantic import BaseModel
from pydantic_settings import BaseSettings

app = FastAPI()


class APIConfig(BaseSettings):
    default_model: str = "medium"
    preload: bool = True
    preloaded_models: list[str] = ["medium"]


config = APIConfig()
logger = logging.getLogger("uvicorn")


def preload_models():
    if not config.preload:
        return
    for m in config.preloaded_models:
        start = time.time()
        whisper.load_model(m)
        end = time.time()
        logger.info(f"Loaded '{m}' model in {end - start} seconds.")


preload_models()


@app.get("/healthz")
def healthz():
    return {"ok": True}


class TranscriptionRequest(BaseModel):
    file: UploadFile
    model: str = config.default_model


@app.post("/transcription")
async def transcribe(req: Annotated[TranscriptionRequest, Form()]):
    logger.info(f"Using '{req.model}' model.")
    content = await req.file.read()

    # load audio and pad/trim it to fit 30 seconds
    audio = load_audio(content)
    audio = whisper.pad_or_trim(audio)

    # load model
    model = whisper.load_model(req.model)

    # make log-Mel spectrogram and move to the same device as the model
    mel = whisper.log_mel_spectrogram(audio, model.dims.n_mels).to(model.device)

    # detect the spoken language
    _, probs = model.detect_language(mel)
    detected_language = max(probs, key=probs.get)

    # decode the audio
    options = whisper.DecodingOptions()
    result = whisper.decode(model, mel, options)

    res = {"text": result.text, "lang": detected_language}
    logger.info(res)
    return res


def load_audio(file: bytes, sr: int = 16000):
    """
    Open an audio file and read as mono waveform, resampling as necessary

    Parameters
    ----------
    file: (str, bytes)
        The audio file to open or bytes of audio file

    sr: int
        The sample rate to resample the audio if necessary

    Returns
    -------
    A NumPy array containing the audio waveform, in float32 dtype.
    """

    inp = file
    file = "pipe:"

    try:
        # This launches a subprocess to decode audio while down-mixing and resampling as necessary.
        # Requires the ffmpeg CLI and `ffmpeg-python` package to be installed.
        out, _ = (
            ffmpeg.input(file, threads=0)
            .output("-", format="s16le", acodec="pcm_s16le", ac=1, ar=sr)
            .run(cmd="ffmpeg", capture_stdout=True, capture_stderr=True, input=inp)
        )
    except ffmpeg.Error as e:
        raise RuntimeError(f"Failed to load audio: {e.stderr.decode()}") from e

    return np.frombuffer(out, np.int16).flatten().astype(np.float32) / 32768.0
