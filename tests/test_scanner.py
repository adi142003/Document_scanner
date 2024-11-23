import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.scanner import DataScanner
import pytest
import io
from PyPDF2 import PdfWriter

class TestDataScanner:
    def create_test_pdf(self, content):
        """Helper method to create a test PDF"""
        writer = PdfWriter()
        writer.add_page()
        writer.add_metadata({'/Content': content})
        output = io.BytesIO()
        writer.write(output)
        return output.getvalue()

    def test_pan_detection(self):
        """Test PAN card number detection"""
        test_content = b"My PAN is ABCDE1234F"
        results = DataScanner.scan_file(test_content, "test.txt")
        assert any(result['info_type'] == 'PAN' and result['value'] == 'ABCDE1234F' for result in results)

    def test_ssn_detection(self):
        """Test SSN detection"""
        test_content = b"SSN: 123-45-6789"
        results = DataScanner.scan_file(test_content, "test.txt")
        assert any(result['info_type'] == 'SSN' and result['value'] == '123-45-6789' for result in results)

    def test_credit_card_detection(self):
        """Test credit card number detection"""
        test_content = b"CC: 4111-1111-1111-1111"
        results = DataScanner.scan_file(test_content, "test.txt")
        assert any(result['info_type'] == 'Credit Card' for result in results)

    def test_multiple_detections(self):
        """Test detection of multiple sensitive data types"""
        test_content = b"PAN: ABCDE1234F\nSSN: 123-45-6789"
        results = DataScanner.scan_file(test_content, "test.txt")
        assert len(results) == 2

    def test_pdf_scanning(self):
        """Test PDF file scanning"""
        pdf_content = self.create_test_pdf("SSN: 123-45-6789")
        results = DataScanner.scan_file(pdf_content, "test.pdf")
        assert any(result['info_type'] == 'SSN' for result in results)

    def test_classification(self):
        """Test data classification"""
        assert DataScanner.classify_data('PAN') == 'PII'
        assert DataScanner.classify_data('SSN') == 'PII'
        assert DataScanner.classify_data('Medical Record') == 'PHI'
        assert DataScanner.classify_data('Credit Card') == 'PCI'