import regex as re
import PyPDF2
import io
import google.generativeai as genai

api_key = "AIzaSyDZ9kU8DSjbCq5sZOcV0Nj-4LSvCe8qyfo"

genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-1.5-flash')

class DataScanner:
    PATTERNS = {
        'PAN': r'\b[A-Z]{5}\d{4}[A-Z]{1}\b',
        'SSN': r'\b\d{3}-\d{2}-\d{4}\b',
        'Medical Record': r'\b\d{8,10}\b',
        'Credit Card': r'\b(?:\d{4}[-\s]?){3}\d{4}\b',
        'Health Insurance': r'\b[A-Z]{2}\d{10}\b',
        'voter_id': r'\b[A-Z]{3}\d{7}\b',
        'driving_licence': r'^(([A-Z]{2}[0-9]{2})( )|([A-Z]{2}-[0-9]{2}))((19|20)[0-9][0-9])[0-9]{7}$'
    }
    
    @classmethod
    def extract_pdf_text(cls, file_content):
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
                # if use_ai:
                #     classification = cls.classify_gemini(match)
                # else:
                classification = cls.classify_data(info_type)
                
                results.append({
                    'type': classification,
                    'info_type': info_type,
                    'value': "".join(match)
                })
        
        if use_ai:
            classification = cls.classify_gemini_2(file_content)
            results.append({
                'type': classification,
                'info_type': "AI", 
                'value': "AI",
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
        
    @staticmethod
    def classify_gemini_2(file_content):
        try:
            prompt = f'''
                Scan this content {file_content} and 
                detect if it contains sensitive data like,
                'PAN': 'PII',
                'SSN': 'PII',
                'voter_id': 'PII',
                'driving_licence': 'PII',
                'Medical Record': 'PHI',
                'Credit Card': 'PCI',
                'Health Insurance': 'PHI' etc.
                Then classifify into 
                - PII (Personally Identifiable Information)
                - PHI (Protected Health Information)
                - PCI (Payment Card Information)
                - Unknown
                
                Your reply should be brief and contain full information
            '''
            response = model.generate_content(prompt)
            return response.text
        
        except Exception as e:
            print(f"Gemini classification error: {e}")
            return 'Unknown'