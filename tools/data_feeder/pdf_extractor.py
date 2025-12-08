"""
PDF Text Extractor Module
Extracts text from PDF files using pdfplumber with PyPDF2 fallback.
"""

import os

try:
    import pdfplumber
    PDFPLUMBER_AVAILABLE = True
except ImportError:
    PDFPLUMBER_AVAILABLE = False

try:
    import PyPDF2
    PYPDF2_AVAILABLE = True
except ImportError:
    PYPDF2_AVAILABLE = False


def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extract text from all pages of a PDF file.
    
    Uses pdfplumber as primary extractor (better accuracy for complex layouts),
    falls back to PyPDF2 if pdfplumber fails or is unavailable.
    
    Args:
        pdf_path: Path to the PDF file
        
    Returns:
        Extracted text with page markers, or error message if extraction fails
    """
    if not os.path.exists(pdf_path):
        return f"Error: File not found: {pdf_path}"
    
    if not pdf_path.lower().endswith('.pdf'):
        return "Error: File is not a PDF"
    
    text = ""
    
    if PDFPLUMBER_AVAILABLE:
        text = _extract_with_pdfplumber(pdf_path)
        if text and not text.startswith("Error"):
            return text
    
    if PYPDF2_AVAILABLE:
        text = _extract_with_pypdf2(pdf_path)
        if text and not text.startswith("Error"):
            return text
    
    if not PDFPLUMBER_AVAILABLE and not PYPDF2_AVAILABLE:
        return "Error: No PDF extraction library available. Install pdfplumber or PyPDF2."
    
    return text if text else "Error: Could not extract text from PDF"


def _extract_with_pdfplumber(pdf_path: str) -> str:
    """Extract text using pdfplumber (better for complex layouts)"""
    try:
        text_parts = []
        with pdfplumber.open(pdf_path) as pdf:
            total_pages = len(pdf.pages)
            for i, page in enumerate(pdf.pages, 1):
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(f"--- Page {i}/{total_pages} ---\n{page_text}")
                else:
                    text_parts.append(f"--- Page {i}/{total_pages} ---\n(No text extracted)")
        return "\n\n".join(text_parts)
    except Exception as e:
        return f"Error (pdfplumber): {e}"


def _extract_with_pypdf2(pdf_path: str) -> str:
    """Extract text using PyPDF2 (fallback)"""
    try:
        text_parts = []
        with open(pdf_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            total_pages = len(reader.pages)
            for i, page in enumerate(reader.pages, 1):
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(f"--- Page {i}/{total_pages} ---\n{page_text}")
                else:
                    text_parts.append(f"--- Page {i}/{total_pages} ---\n(No text extracted)")
        return "\n\n".join(text_parts)
    except Exception as e:
        return f"Error (PyPDF2): {e}"


def get_pdf_info(pdf_path: str) -> dict:
    """
    Get PDF metadata and page count.
    
    Args:
        pdf_path: Path to the PDF file
        
    Returns:
        Dictionary with page_count, title, author, and other metadata
    """
    info = {
        "page_count": 0,
        "title": None,
        "author": None,
        "subject": None,
        "creator": None
    }
    
    if PDFPLUMBER_AVAILABLE:
        try:
            with pdfplumber.open(pdf_path) as pdf:
                info["page_count"] = len(pdf.pages)
                if pdf.metadata:
                    info["title"] = pdf.metadata.get("Title")
                    info["author"] = pdf.metadata.get("Author")
                    info["subject"] = pdf.metadata.get("Subject")
                    info["creator"] = pdf.metadata.get("Creator")
            return info
        except Exception:
            pass
    
    if PYPDF2_AVAILABLE:
        try:
            with open(pdf_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                info["page_count"] = len(reader.pages)
                if reader.metadata:
                    info["title"] = reader.metadata.get("/Title")
                    info["author"] = reader.metadata.get("/Author")
                    info["subject"] = reader.metadata.get("/Subject")
                    info["creator"] = reader.metadata.get("/Creator")
            return info
        except Exception:
            pass
    
    return info


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        pdf_file = sys.argv[1]
        print(f"Extracting text from: {pdf_file}")
        print("=" * 50)
        result = extract_text_from_pdf(pdf_file)
        print(result)
    else:
        print("Usage: python pdf_extractor.py <pdf_file>")
