import pytest
from app.scanner import DataScanner

def test_pan_detection():
    test_content = b"My PAN is ABCDE1234F"
    results = DataScanner.scan_file(test_content)
    assert any(result['info_type'] == 'PAN' for result in results)

def test_ssn_detection():
    test_content = b"SSN: 123-45-6789"
    results = DataScanner.scan_file(test_content)
    assert any(result['info_type'] == 'SSN' for result in results)
