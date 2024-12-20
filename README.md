# PII/PHI/PCI Data Scanner

## Project Overview
A web application designed to scan and classify sensitive information in various file types, identifying Personally Identifiable Information (PII), Protected Health Information (PHI), and Payment Card Information (PCI).

## deployed the backend on `render.com`
<a href='https://document-scanner-p889.onrender.com/'>Document scanner website link</a>

## Features
- File upload support (txt, csv, log, pdf)
- Pattern-based sensitive data detection
- Optional AI-powered classification using Google Gemini
- Store scan results in SQLite database
- View and delete scan results
- Supports multiple file types
## System design diagram
<img width="436" alt="system-design" src="https://github.com/user-attachments/assets/5d6130d0-0b89-4e1d-b6f0-7f6ee9ba8956">

## Technology Stack
- Backend: FastAPI
- Database: SQLAlchemy (SQLite)
- AI Classification: Google Gemini
- Frontend: Jinja2 Templates
- Language: Python 3.9+

## Prerequisites
- Python 3.9+
- pip
- Google Gemini API Key


### 1. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Set Up Environment Variables
Create a `.env` file in the project root:
```
GEMINI_API_KEY=your_google_gemini_api_key
DATABASE_URL=sqlite:///./scanner.db
```

## Configuration
- Modify `app/scanner.py` to add or update regex patterns
- Adjust classification logic in `classify_data()` and `classify_gemini()` methods

## Running the Application
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```
## Testing the application
Go to the root directory of the app and run the below command:
```
pytest
```
OR

### Access the Application
- Upload Page: `http://localhost:8000/`

## Docker Deployment
```bash
docker-compose up --build
```

## Future work
- Implement user authentication
- Sanitize and validate all file uploads
- Rotate Gemini API keys regularly

## Limitations
- AI classification is experimental
- Regex patterns may not catch all variations of sensitive data
- Performance may vary with large files
