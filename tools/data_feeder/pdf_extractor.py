"""
PDF Text Extractor Module
Extracts text from PDF files using PyMuPDF (fitz), pdfplumber, or PyPDF2.
Includes security validation, context length limits, and async support.
"""

import os
import re
import asyncio
from pathlib import Path
from typing import Optional, Dict, Any
from concurrent.futures import ThreadPoolExecutor

# Configuration
MAX_TEXT_LENGTH = 500_000  # Max characters to extract (prevents memory issues)
MAX_PAGES = 1000  # Max pages to process
MAX_FILE_SIZE_MB = 100  # Max file size in MB
ALLOWED_EXTENSIONS = {'.pdf'}

try:
    import fitz  # PyMuPDF
    FITZ_AVAILABLE = True
except ImportError:
    FITZ_AVAILABLE = False

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


class PDFSecurityError(Exception):
    """Raised when security validation fails"""
    pass


class PDFExtractionError(Exception):
    """Raised when text extraction fails"""
    pass


def validate_pdf_path(pdf_path: str) -> Path:
    """
    Validate and sanitize PDF file path.
    
    Security checks:
    - Path traversal prevention
    - File extension validation
    - File size limits
    - File existence
    
    Args:
        pdf_path: Path to the PDF file
        
    Returns:
        Validated Path object
        
    Raises:
        PDFSecurityError: If validation fails
    """
    if not pdf_path or not isinstance(pdf_path, str):
        raise PDFSecurityError("Invalid path: Path must be a non-empty string")
    
    # Normalize and resolve path
    try:
        path = Path(pdf_path).resolve()
    except Exception as e:
        raise PDFSecurityError(f"Invalid path format: {e}")
    
    # Check for path traversal attempts
    if '..' in str(pdf_path):
        raise PDFSecurityError("Security error: Path traversal detected")
    
    # Check file exists
    if not path.exists():
        raise PDFSecurityError(f"File not found: {path}")
    
    # Check it's a file, not directory
    if not path.is_file():
        raise PDFSecurityError(f"Not a file: {path}")
    
    # Check extension
    if path.suffix.lower() not in ALLOWED_EXTENSIONS:
        raise PDFSecurityError(f"Invalid file type: {path.suffix}. Only PDF files allowed.")
    
    # Check file size
    file_size_mb = path.stat().st_size / (1024 * 1024)
    if file_size_mb > MAX_FILE_SIZE_MB:
        raise PDFSecurityError(f"File too large: {file_size_mb:.1f}MB. Max: {MAX_FILE_SIZE_MB}MB")
    
    return path


def truncate_text(text: str, max_length: int = MAX_TEXT_LENGTH) -> tuple[str, bool]:
    """
    Truncate text to max length if needed.
    
    Returns:
        Tuple of (text, was_truncated)
    """
    if len(text) <= max_length:
        return text, False
    return text[:max_length] + f"\n\n[... Truncated at {max_length:,} characters ...]", True


def extract_text_from_pdf(
    pdf_path: str,
    max_pages: Optional[int] = None,
    max_length: Optional[int] = None
) -> str:
    """
    Extract text from all pages of a PDF file.
    
    Strategy:
    1. Try PyMuPDF (fitz) - Fastest and good Unicode support
    2. Try pdfplumber - Good for complex layouts
    3. Try PyPDF2 - Fallback
    
    Args:
        pdf_path: Path to the PDF file
        max_pages: Maximum pages to extract (default: MAX_PAGES)
        max_length: Maximum text length (default: MAX_TEXT_LENGTH)
        
    Returns:
        Extracted text with page markers, or error message if extraction fails
    """
    max_pages = max_pages or MAX_PAGES
    max_length = max_length or MAX_TEXT_LENGTH
    
    # Security validation
    try:
        validated_path = validate_pdf_path(pdf_path)
    except PDFSecurityError as e:
        return f"Error: {e}"
    
    text = ""
    
    # 1. Try PyMuPDF (fitz)
    if FITZ_AVAILABLE:
        text = _extract_with_fitz(str(validated_path), max_pages)
        if text and not text.startswith("Error") and len(text.strip()) > 10:
            text, _ = truncate_text(text, max_length)
            return text

    # 2. Try pdfplumber
    if PDFPLUMBER_AVAILABLE:
        text = _extract_with_pdfplumber(str(validated_path), max_pages)
        if text and not text.startswith("Error") and len(text.strip()) > 10:
            text, _ = truncate_text(text, max_length)
            return text
    
    # 3. Try PyPDF2
    if PYPDF2_AVAILABLE:
        text = _extract_with_pypdf2(str(validated_path), max_pages)
        if text and not text.startswith("Error"):
            text, _ = truncate_text(text, max_length)
            return text
    
    if not (FITZ_AVAILABLE or PDFPLUMBER_AVAILABLE or PYPDF2_AVAILABLE):
        return "Error: No PDF extraction library available. Install PyMuPDF, pdfplumber, or PyPDF2."
    
    return text if text else "Error: Could not extract text from PDF"


async def extract_text_from_pdf_async(
    pdf_path: str,
    max_pages: Optional[int] = None,
    max_length: Optional[int] = None
) -> str:
    """
    Async version of extract_text_from_pdf.
    Runs extraction in a thread pool to avoid blocking.
    
    Args:
        pdf_path: Path to the PDF file
        max_pages: Maximum pages to extract
        max_length: Maximum text length
        
    Returns:
        Extracted text with page markers
    """
    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor() as executor:
        result = await loop.run_in_executor(
            executor,
            lambda: extract_text_from_pdf(pdf_path, max_pages, max_length)
        )
    return result


def _extract_with_fitz(pdf_path: str, max_pages: int = MAX_PAGES) -> str:
    """Extract text using PyMuPDF (fitz)"""
    try:
        text_parts = []
        doc = fitz.open(pdf_path)
        total_pages = min(len(doc), max_pages)
        for i in range(total_pages):
            page = doc.load_page(i)
            page_text = page.get_text()
            if page_text.strip():
                text_parts.append(f"--- Page {i+1}/{len(doc)} ---\n{page_text}")
            else:
                text_parts.append(f"--- Page {i+1}/{len(doc)} ---\n(No text extracted)")
        doc.close()
        
        if len(doc) > max_pages:
            text_parts.append(f"\n[... {len(doc) - max_pages} more pages not extracted (limit: {max_pages}) ...]")
        
        return "\n\n".join(text_parts)
    except Exception as e:
        return f"Error (PyMuPDF): {e}"



def _extract_with_pdfplumber(pdf_path: str, max_pages: int = MAX_PAGES) -> str:
    """Extract text using pdfplumber (better for complex layouts)"""
    try:
        text_parts = []
        with pdfplumber.open(pdf_path) as pdf:
            total_pages = len(pdf.pages)
            pages_to_process = min(total_pages, max_pages)
            for i in range(pages_to_process):
                page = pdf.pages[i]
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(f"--- Page {i+1}/{total_pages} ---\n{page_text}")
                else:
                    text_parts.append(f"--- Page {i+1}/{total_pages} ---\n(No text extracted)")
            
            if total_pages > max_pages:
                text_parts.append(f"\n[... {total_pages - max_pages} more pages not extracted (limit: {max_pages}) ...]")
        
        return "\n\n".join(text_parts)
    except Exception as e:
        return f"Error (pdfplumber): {e}"


def _extract_with_pypdf2(pdf_path: str, max_pages: int = MAX_PAGES) -> str:
    """Extract text using PyPDF2 (fallback)"""
    try:
        text_parts = []
        with open(pdf_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            total_pages = len(reader.pages)
            pages_to_process = min(total_pages, max_pages)
            for i in range(pages_to_process):
                page = reader.pages[i]
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(f"--- Page {i+1}/{total_pages} ---\n{page_text}")
                else:
                    text_parts.append(f"--- Page {i+1}/{total_pages} ---\n(No text extracted)")
            
            if total_pages > max_pages:
                text_parts.append(f"\n[... {total_pages - max_pages} more pages not extracted (limit: {max_pages}) ...]")
        
        return "\n\n".join(text_parts)
    except Exception as e:
        return f"Error (PyPDF2): {e}"


def get_pdf_info(pdf_path: str) -> Dict[str, Any]:
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
        "creator": None,
        "file_size_mb": 0,
        "is_valid": False,
        "error": None
    }
    
    # Validate path first
    try:
        validated_path = validate_pdf_path(pdf_path)
        info["file_size_mb"] = round(validated_path.stat().st_size / (1024 * 1024), 2)
        info["is_valid"] = True
    except PDFSecurityError as e:
        info["error"] = str(e)
        return info
    
    if FITZ_AVAILABLE:
        try:
            doc = fitz.open(pdf_path)
            info["page_count"] = len(doc)
            info["title"] = doc.metadata.get("title")
            info["author"] = doc.metadata.get("author")
            info["subject"] = doc.metadata.get("subject")
            info["creator"] = doc.metadata.get("creator")
            doc.close()
            return info
        except Exception:
            pass

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
