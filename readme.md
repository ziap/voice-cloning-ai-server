# Voice cloning AI Server

REST API wrapper for <https://github.com/CorentinJ/Real-Time-Voice-Cloning>.
Powered by [FastAPI](https://fastapi.tiangolo.com)

## Install

Create a virtual environment with python3.7

Clone the repository

```bash
git clone --recursive --depth=1 https://github.com/ziap/voice-cloning-ai-server ai-server
cd ai-server
```

Install [PyTorch](https://pytorch.org/get-started/locally/)

Install other dependencies

```bash
pip install -r model/requirements.txt
pip install fastapi "uvicorn[standard]" python-multipart aiofiles
```

Run the server

```bash
./main.py
```

## Configuration

This server is configured via environment variables.

You can use a `.env` file to configure it

```bash
HOST=127.0.0.1
PORT=3000
DEBUG=True # Enable live-reloading
```

## Documentation

Run the server and navigate to <localhost:3000/docs>.

## License

This repository is licensed under the [AGPL-3.0 license](LICENSE).
