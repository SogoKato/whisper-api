"""
Sample script to record voice.

References:
- https://zenn.dev/kun432/scraps/190f23ec825b12
- https://moromisenpy.com/pyaudio/
"""

import os
import sys
import wave
from argparse import ArgumentParser

import pyaudio

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1 if sys.platform == "darwin" else 2
RATE = 44100


def record(filename: str, seconds: int):
    with wave.open(filename, "wb") as wf:
        p = pyaudio.PyAudio()
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)

        stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True)

        print("Recording...")
        for _ in range(0, RATE // CHUNK * seconds):
            wf.writeframes(stream.read(CHUNK))
        print("Done")

        stream.close()
        p.terminate()


if __name__ == "__main__":
    parser = ArgumentParser(description="Sample script to record voice.")
    parser.add_argument("--filename", default="outputs/example.wav")
    parser.add_argument("--seconds", default=5, type=int)
    args = parser.parse_args()
    os.makedirs(os.path.dirname(args.filename), exist_ok=True)
    record(filename=args.filename, seconds=args.seconds)
