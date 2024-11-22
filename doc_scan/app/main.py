from fastapi import FastAPI, File, UploadFile, Depends, HTTPException, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.requests import Request
from sqlalchemy.orm import Session
import os

from .database import SessionLocal, ScanResult
from .scanner import DataScanner

app = FastAPI()
templates = Jinja2Templates(directory="app/templates")

def get_db():
    """
    Dependency function that yields a database session.
    
    This function is a FastAPI dependency that yields a database session to be used
    by the endpoint. It also ensures that the database session is closed after use.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/upload/", response_class=HTMLResponse)
async def upload_file(
    request: Request, 
    file: UploadFile = File(...), 
    db: Session = Depends(get_db),
    use_ai_classification: bool = Form(False)  # New parameter
):
    print(use_ai_classification)
    if not file.filename.endswith(('.txt', '.csv', '.log', '.pdf')):
        raise HTTPException(status_code=400, detail="Invalid file type")
    
    file_content = await file.read()
    scan_results = DataScanner.scan_file(file_content, file.filename, use_ai=use_ai_classification)
    
    for result in scan_results:
        db_result = ScanResult(
            filename=file.filename,
            datatype=result['type'],
            value=''.join(result['value'])
        )
        db.add(db_result)
    
    db.commit()
    
    return templates.TemplateResponse("scan_results.html", {
        "request": request, 
        "filename": file.filename, 
        "results": scan_results,
        "use_ai": use_ai_classification
    })

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/scans", response_class=HTMLResponse)
async def list_scans(request: Request, db: Session = Depends(get_db)):
    scans = db.query(ScanResult).all()
    return templates.TemplateResponse("scans.html", {"request": request, "scans": scans})

@app.delete("/scans/{scan_id}")
async def delete_scan(scan_id: int, db: Session = Depends(get_db)):
    scan = db.query(ScanResult).filter(ScanResult.id == scan_id).first()
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
    db.delete(scan)
    db.commit()
    return {"message": "Scan deleted successfully"}
