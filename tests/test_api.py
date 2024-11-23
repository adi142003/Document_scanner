import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from app.main import app
import io

client = TestClient(app)

def test_upload_endpoint_valid_file():
    """Test file upload with valid content"""
    test_file = io.BytesIO(b"SSN: 123-45-6789")
    response = client.post(
        "/upload/",
        files={"file": ("test.txt", test_file, "text/plain")}
    )
    assert response.status_code == 200
    assert "123-45-6789" in response.text

def test_upload_endpoint_invalid_file():
    """Test file upload with invalid file type"""
    test_file = io.BytesIO(b"test content")
    response = client.post(
        "/upload/",
        files={"file": ("test.exe", test_file, "application/x-msdownload")}
    )
    assert response.status_code == 400

def test_list_scans():
    """Test scans listing endpoint"""
    response = client.get("/scans")
    assert response.status_code == 200

def test_delete_scan():
    """Test scan deletion"""
    # First create a scan
    test_file = io.BytesIO(b"SSN: 123-45-6789")
    client.post("/upload/", files={"file": ("test.txt", test_file, "text/plain")})
    
    # Then try to delete it
    response = client.delete("/scans/1")
    assert response.status_code == 200