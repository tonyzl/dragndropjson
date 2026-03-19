# File Word Extractor

Upload **two files** (PDF or images) and get back a JSON with every extracted word.

## Stack

| Layer | Tech |
|---|---|
| Backend | FastAPI + PyMuPDF + Tesseract OCR |
| Frontend | React 18 + Vite 5 |

---

## Setup & Run

### 1. Install Tesseract (system dependency)

**Ubuntu/Debian:**
```bash
sudo apt-get install tesseract-ocr tesseract-ocr-eng
```

**macOS:**
```bash
brew install tesseract
```

**Windows:**
Download installer: https://github.com/UB-Mannheim/tesseract/wiki  
Then add tesseract to your PATH.

---

### 2. Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

API → http://localhost:8000  
Docs → http://localhost:8000/docs

---

### 3. Frontend

Open a second terminal:

```bash
cd frontend
npm install
npm run dev
```

App → http://localhost:5173

---

## API

### POST /extract

Multipart form-data:
- `file1` — PDF or image
- `file2` — PDF or image

Response:
```json
{
  "document.pdf": {
    "word_count": 142,
    "words": ["hello", "world", "..."]
  },
  "photo.png": {
    "word_count": 37,
    "words": ["invoice", "total", "..."]
  }
}
```

Supported formats: PDF · PNG · JPG · WEBP · TIFF · BMP

---

## How it works

- **PDF** → PyMuPDF extracts text natively (no OCR needed for digital PDFs)
- **Images** → Tesseract OCR reads text from scanned docs or photos
- **Proxy** → Vite forwards `/extract` to FastAPI, so no CORS issues
