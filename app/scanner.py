import regex as re
import PyPDF2
import io
import google.generativeai as genai

api_key = "AIzaSyDZ9kU8DSjbCq5sZOcV0Nj-4LSvCe8qyfo"

class DataScanner:
    PATTERNS = {
        'PAN': r'\b[A-Z]{5}\d{4}[A-Z]{1}\b',
        'SSN': r'\b\d{3}-\d{2}-\d{4}\b',
        'Medical Record': r'\b\d{8,10}\b',
        'Credit Card': r'\b(?:\d{4}[-\s]?){3}\d{4}\b',
        'Health Insurance': r'\b[A-Z]{2}\d{10}\b',
        'voter_id': r'\b[A-Z]{3}\d{7}\b',
        'driving_licence': r'\b(([A-Z]{2}\d{2})(\s)|([A-Z]{2}-\d{2}))((19|20)[0-9][0-9])[0-9]{7}\b'
    }
    
    @classmethod
    def extract_pdf_text(cls, file_content):
/*************  ✨ Codeium Command ⭐  *************/
"""
Extracts text from a PDF file content.

This method takes the binary content of a PDF file and extracts its textual 
content using the PyPDF2 library. It iterates through each page of the PDF, 
appending the extracted text to a cumulative string which is returned. If 
an error occurs during extraction, it prints an error message and returns 
an empty string.

Parameters:
file_content (bytes): The binary content of the PDF file.

Returns:
str: The extracted text from the PDF. Returns an empty string if extraction fails.
"""
/******  2d760bf9-4238-4b28-b3e9-ba2b6a16bf46  *******/
        try:
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_content))
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()
            return text
        except Exception as e:
            print(f"PDF extraction error: {e}")
            return ""
    
    @classmethod
    def scan_file(cls, file_content, filename, use_ai=False):
        results = []

        # Extract content based on file type
        if filename.lower().endswith('.pdf'):
            content = cls.extract_pdf_text(file_content)
        else:
            content = file_content.decode('utf-8')
        
        # Pattern-based scanning
        for info_type, pattern in cls.PATTERNS.items():
            matches = re.findall(pattern, content)
            for match in matches:
                # Determine classification
                if use_ai:
                    classification = cls.classify_gemini(match)
                else:
                    classification = cls.classify_data(info_type)
                
                results.append({
                    'type': classification,
                    'info_type': info_type,
                    'value': match
                })
        
        return results
    
    @staticmethod
    def classify_data(info_type):
        classifications = {
            'PAN': 'PII',
            'SSN': 'PII',
            'voter_id': 'PII',
            'driving_licence': 'PII',
            'Medical Record': 'PHI',
            'Credit Card': 'PCI',
            'Health Insurance': 'PHI'
        }
        return classifications.get(info_type, 'Unknown')
    
    @staticmethod
    def classify_gemini(sensitive_data):
        try:
            # Configure Gemini API (ensure to keep API key secure)
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            # Prompt for classification
            prompt = f"""
            Classify the following sensitive data into one of these categories:
            - PII (Personally Identifiable Information)
            - PHI (Protected Health Information)
            - PCI (Payment Card Information)
            - Unknown
            
            Provide only the classification for this data: {sensitive_data}
            """
            
            response = model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            print(f"Gemini classification error: {e}")
            return 'Unknown'