# ImagineRead Lite

Serviço de compartilhamento de arquivos (PDF, CBZ, CBR, EPUB) via QRCode/código alfanumérico.

## Quick Start

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

### Landing Page
```bash
cd landing
npm install
npm run dev
```

## Project Structure
- `landing/` - React landing page
- `backend/` - Python FastAPI backend
- `functions/` - Cloud Functions for cleanup
- `mobile/` - iOS integration code

## Environment Variables
See `.env.example` in each directory.
