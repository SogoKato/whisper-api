# whisper-api

API server running [Whisper](https://github.com/openai/whisper)

Blog (Japanese): https://sogo.dev/posts/2024/10/building-whisper-api

## Getting started

### Prerequisites

* [rye](https://rye.astral.sh/)
* [portaudio](https://www.portaudio.com/) if you are using macOS and record voice using `examples/record.py` script
  * `brew install portaudio`
* [ffmpeg](https://ffmpeg.org/)
  * `brew install ffmpeg`
  * For further details, see https://github.com/openai/whisper?tab=readme-ov-file#setup

### Prepare audio files (optional)

If you have audio files to transcribe, skip this step.

Create a virtual environment and install dependencies.

```
rye sync
```

Speak something for five seconds.

```
rye run python examples/record.py
```

`outputs/example.wav` will be created.

### Run locally

Create a virtual environment and install dependencies, unless you have not run `rye sync` yet.

```
rye sync --no-dev
```

Run API server.

```
rye run uvicorn src.main:app
```

### Run in container

Build a docker image.

```
docker build -t whisper-api:0.1.0 --build-arg PYTHON_VERSION=$(cat .python-version) .
```

Run docker container.

```
docker run --rm -p 8000:8000 -v ${HOME}/.cache/whisper:/home/ryeuser/.cache/whisper whisper-api:0.1.0
```

Note that transcription in container is 2x slower than in host OS (tested with M2 Macbook Air).

### Transcribe!

#### Using curl

```
curl -w "\ntime_total: %{time_total}\n" -X POST http://localhost:8000/transcription -F "file=@$(pwd)/outputs/example.wav;type=audio/wav"
```

output:

```
{"text":"そもそも大将軍の私に直に教わろうなんて虫が良すぎますよコココココ","lang":"ja"}
time_total: 33.191537
```

You can change models by passing `model` parameter, e.g. `-F "model=small"`.

#### Using Python requests

```
rye run python examples/transcribe.py
```

output:

```
{'text': 'そもそも大将軍の私に直に教わろうなんて虫が良すぎますよコココココ', 'lang': 'ja'}
time_total: 33.6490957736969
```
