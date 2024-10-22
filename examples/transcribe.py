"""
Sample script to transcribe using API.
"""

import time
from argparse import ArgumentParser

import requests


def transcribe(filename: str, endpoint: str, content_type: str, model: str):
    with open(filename, "rb") as f:
        file = ("audio", f, content_type)
        data = None
        if model:
            data = {"model": model}
        start = time.time()
        res = requests.post(endpoint, files={"file": file}, data=data)
        end = time.time()
    print(res.json())
    print("time_total:", end - start)


if __name__ == "__main__":
    parser = ArgumentParser(description="Sample script to record voice.")
    parser.add_argument("--filename", default="outputs/example.wav")
    parser.add_argument("--endpoint", default="http://localhost:8000/transcription")
    parser.add_argument("--content-type", default="audio/wav")
    parser.add_argument("--model")
    args = parser.parse_args()
    transcribe(
        filename=args.filename,
        endpoint=args.endpoint,
        content_type=args.content_type,
        model=args.model,
    )
