# Backend - ImagineRead Lite

FastAPI backend for file uploads and downloads.

## Setup

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your Google Cloud credentials
uvicorn main:app --reload
```

## Endpoints

- `POST /upload` - Upload file, returns code
- `GET /file/{code}` - Get file info and signed URL
- `GET /health` - Health check
