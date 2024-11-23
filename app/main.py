from fastapi import FastAPI, File, UploadFile, Depends, HTTPException, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.requests import Request
from sqlalchemy.orm import Session
# import os

from .database import SessionLocal, ScanResult
from .scanner import DataScanner

app = FastAPI()
templates = Jinja2Templates(directory="app/templates")

def get_db():
    """
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
    """
    Endpoint for uploading a file to be scanned for sensitive information.

    This endpoint expects a file to be uploaded, and it will scan the file for sensitive
    information (such as credit card numbers, social security numbers, etc.).  It will
    then store the results in the database and render an HTML template with the scan
    results.

    Parameters:
    request (Request): The request object, used for rendering the HTML template.
    file (UploadFile): The file to be scanned, passed as a form file.
    db (Session): The database session, used for storing the scan results.
    use_ai_classification (bool): If True, the AI classification will be used.  If False,
        the pattern-based classification will be used.

    Returns:
    A rendered HTML template with the scan results.
    """
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
    """
    Handles the root endpoint of the application and renders the homepage.

    This asynchronous function responds to GET requests at the root URL ("/") 
    and returns an HTML response that renders the "index.html" template.

    Parameters:
    request (Request): The request object used for rendering the HTML template.

    Returns:
    A TemplateResponse object rendering the "index.html" template.
    """
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/scans", response_class=HTMLResponse)
async def list_scans(request: Request, db: Session = Depends(get_db)):
    
    """
    Retrieves and displays a list of all scan results stored in the database.

    This asynchronous function handles GET requests to the "/scans" endpoint.
    It queries the database for all scan results and renders them in the "scans.html" template.

    Parameters:
    request (Request): The request object used for rendering the HTML template.
    db (Session): The database session dependency, used for querying scan results.

    Returns:
    A TemplateResponse object rendering the "scans.html" template with the list of scan results.
    """
    scans = db.query(ScanResult).all()
    return templates.TemplateResponse("scans.html", {"request": request, "scans": scans})

@app.delete("/scans/{scan_id}")
async def delete_scan(scan_id: int, db: Session = Depends(get_db)):
    """
    Deletes a scan result from the database.

    This asynchronous function handles DELETE requests to the "/scans/{scan_id}" endpoint.
    It queries the database for a scan result with the given ID, and if found, deletes it.
    If the scan result is not found, it returns a 404 error.

    Parameters:
    scan_id (int): The ID of the scan result to delete.
    db (Session): The database session dependency, used for deleting the scan result.

    Returns:
    A JSON response with a message indicating the scan was deleted successfully.
    """
    scan = db.query(ScanResult).filter(ScanResult.id == scan_id).first()
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
    db.delete(scan)
    db.commit()
    return {"message": "Scan deleted successfully"}
