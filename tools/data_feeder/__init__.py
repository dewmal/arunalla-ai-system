"""
Data Feeder module for RAG Data Curator Tool.
Provides PDF extraction and Google Drive download functionality.
"""

from .pdf_extractor import extract_text_from_pdf, get_pdf_info
from .downloader import download, download_file, download_folder, is_folder_url

__all__ = [
    "extract_text_from_pdf",
    "get_pdf_info",
    "download",
    "download_file",
    "download_folder",
    "is_folder_url"
]
